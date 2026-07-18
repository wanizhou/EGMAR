from __future__ import annotations

import json
import re
from typing import Any

from starcraft_rag.context import RAGContext
from starcraft_rag.llm import BaseLLMProvider


def compact_text(text: Any, limit: int = 260) -> str:
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 3] + "..."


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def clamp01(value: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def contains_cjk(text: Any) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", str(text or "")))


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise LLMJSONError("No JSON object found in LLM output")
    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMJSONError(f"Failed to parse LLM JSON output: {exc}") from exc


def normalize_evidence_id(value: Any) -> str:
    """把 LLM 常见的 evidence_1 写法修正为 evidence_001，降低格式抖动带来的回退。"""

    text = str(value or "").strip()
    match = re.fullmatch(r"evidence_(\d+)", text, flags=re.IGNORECASE)
    if match:
        return f"evidence_{int(match.group(1)):03d}"
    return text


class LLMJSONError(ValueError):
    """用于区分 LLM 输出 JSON 解析失败，便于 run_eval 统计。"""


class LLMValidationError(ValueError):
    """用于区分 LLM 输出可解析但不符合答案合成协议的情况。"""


class TemplateAnswerSynthesizer:
    """模板式答案合成器，作为轻量基线和 LLM 失败后的回退路径。"""

    def synthesize(self, ctx: RAGContext) -> str:
        ctx.synthesis_metadata.update(
            {
                "mode": "template",
                "llm_synthesizer_fallback": False,
                "llm_json_parse_failure": False,
                "prompt_evidence_count": 0,
            }
        )
        # The fallback is user-facing too.  Do not leak internal document IDs,
        # warnings, or a retrieval dump as an apparent answer.
        claims = [claim for result in ctx.agent_results for claim in result.claims]
        if not claims:
            answer_text = "I cannot determine this from the retrieved evidence."
            ctx.synthesis_output = {
                "text": answer_text,
                "answer_sentences": [],
                "supporting_points": [],
                "uncertainties": ["No directly supported answer claim was available."],
                "conflicts": [],
                "used_profiles": ctx.used_profiles,
            }
            return answer_text

        query_terms = {
            token.lower()
            for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]+", ctx.query)
            if len(token) >= 3 and token.lower() not in {"what", "which", "does", "have", "with", "from", "that", "this", "the", "and"}
        }
        focus_terms = query_terms & {
            "ability", "armor", "attack", "cost", "cooldown", "damage", "energy", "health", "land", "lift",
            "produce", "produced", "production", "range", "require", "requires", "shield", "space", "target",
        }
        target_terms = {
            part.lower()
            for identifier in ((ctx.plan.entities if ctx.plan else []) + (ctx.plan.abilities if ctx.plan else []))
            for part in str(identifier).split("_")
            if len(part) >= 3 and part.lower() not in {"ability", "terran", "protoss", "zerg"}
        }
        ability_target_terms: set[str] = set()
        for identifier in (ctx.plan.abilities if ctx.plan else []):
            parts = str(identifier).lower().split("_")
            try:
                parts = parts[parts.index("ability") + 1 :]
            except ValueError:
                pass
            ability_target_terms.update(part for part in parts if len(part) >= 3)
        def relevance(claim: Any) -> tuple[int, int, int, int, int, int, float]:
            text = str(claim.claim or "").lower()
            factual_type = int(
                str(claim.evidence_type or "")
                in {"ability_base_effect", "ability_metrics", "entity_survival", "tech_cost", "tech_tree_edge"}
            )
            return (
                sum(int(term in text) for term in ability_target_terms),
                sum(int(term in text) for term in focus_terms),
                factual_type,
                sum(int(term in text) for term in target_terms),
                sum(int(term in text) for term in query_terms),
                int((claim.source_layer or "") == "processed"),
                float(claim.score or 0.0),
            )
        required_count = len((ctx.plan.answer_requirements if ctx.plan else []) or [])
        candidate_limit = min(3, max(1, required_count))
        ranked: list[Any] = []
        used_agents: set[str] = set()
        for claim in sorted(claims, key=relevance, reverse=True):
            agent = str((claim.metadata or {}).get("producing_agent") or "")
            if agent and agent in used_agents:
                continue
            ranked.append(claim)
            if agent:
                used_agents.add(agent)
            if len(ranked) >= candidate_limit:
                break
        if len(ranked) < candidate_limit:
            ranked.extend(
                claim for claim in sorted(claims, key=relevance, reverse=True)
                if claim not in ranked
            )
            ranked = ranked[:candidate_limit]
        answer_text = " ".join(claim.claim.rstrip() for claim in ranked)
        supporting_points = [
            {
                "point": claim.claim,
                "source_evidence_ids": [],
                "evidence_layer": claim.source_layer or "unknown",
                "confidence": claim.confidence,
                "sources": [{"source_profile_id": claim.source_profile_id, "source_field": claim.source_field}],
            }
            for claim in ranked
        ]
        ctx.synthesis_output = {
            "text": answer_text,
            "answer_sentences": [
                {"text": claim.claim, "source_evidence_ids": [], "evidence_layer": claim.source_layer or "unknown"}
                for claim in ranked
            ],
            "supporting_points": supporting_points,
            "uncertainties": [],
            "conflicts": [],
            "used_profiles": ctx.used_profiles,
        }
        return answer_text


class LLMAnswerSynthesizer(TemplateAnswerSynthesizer):
    """基于 AgentEvidence 的本地 LLM 答案合成器。

    Synthesizer 不主动查库，只消费当前 RAGContext 中已有证据。对外只保留一个
    answer.text，证据点、不确定性和冲突作为结构化字段单独保存。
    """

    CAUTION_TEXT = "This is a rule-enriched signal, not an absolute conclusion."
    CAUTION_TERMS = ("rule-enriched", "not absolute", "not an absolute", "signal", "inference", "suggests", "may")
    INSUFFICIENT_UNCERTAINTY_PATTERNS = (
        "does not provide information",
        "do not provide information",
        "doesn't provide information",
        "no evidence",
        "insufficient evidence",
        "not enough evidence",
        "lack of evidence",
        "lacks evidence",
        "does not specify",
        "do not specify",
    )

    def __init__(
        self,
        llm_provider: BaseLLMProvider | None,
        max_new_tokens: int = 768,
        evidence_top_k: int = 16,
        supporting_point_top_k: int = 5,
    ) -> None:
        self.llm_provider = llm_provider
        self.max_new_tokens = max_new_tokens
        self.evidence_top_k = evidence_top_k
        self.supporting_point_top_k = supporting_point_top_k

    def synthesize(self, ctx: RAGContext) -> str:
        evidence_rows: list[dict[str, Any]] = []
        try:
            if self.llm_provider is None:
                raise LLMValidationError("LLMAnswerSynthesizer requires an llm_provider")

            all_evidence = self._build_synthesis_evidence(ctx)
            evidence_rows = self._select_synthesis_evidence(all_evidence)
            if not evidence_rows:
                raise LLMValidationError("No synthesis evidence available")

            llm_data, response_metadata = self._call_llm(ctx, evidence_rows)
            validated = self._validate_output(llm_data, evidence_rows)
            answer_object = self._build_answer_object(validated, evidence_rows, ctx)
            ctx.synthesis_output = answer_object
            ctx.synthesis_metadata.update(
                {
                    "mode": "local-llm",
                    "provider": getattr(self.llm_provider, "name", ""),
                    "response_model": response_metadata.get("model", ""),
                    "all_evidence_count": len(all_evidence),
                    "prompt_evidence_count": len(evidence_rows),
                    "supporting_point_count": len(answer_object["supporting_points"]),
                    "llm_synthesizer_fallback": False,
                    "llm_json_parse_failure": False,
                    "fallback_reason": "",
                }
            )
            return str(answer_object["text"])
        except Exception as exc:
            fallback = TemplateAnswerSynthesizer().synthesize(ctx)
            ctx.synthesis_metadata.update(
                {
                    "mode": "template-fallback",
                    "provider": getattr(self.llm_provider, "name", "") if self.llm_provider else "",
                    "prompt_evidence_count": len(evidence_rows),
                    "llm_synthesizer_fallback": True,
                    "llm_json_parse_failure": isinstance(exc, LLMJSONError),
                    "fallback_reason": str(exc),
                }
            )
            return fallback

    def _build_synthesis_evidence(self, ctx: RAGContext) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        counter = 1
        for result in ctx.agent_results:
            ranked_claims = sorted(result.claims, key=lambda claim: (claim.rank <= 0, claim.rank, -claim.score))
            for claim in ranked_claims:
                claim_text = compact_text(claim.claim, 520)
                reason = compact_text(claim.reason, 360)
                # 运行数据要求英文化；如果上游异常产出中文证据，先不送入最终合成。
                if contains_cjk(claim_text) or contains_cjk(reason):
                    continue
                confidence = None if claim.confidence is None else clamp01(claim.confidence)
                rows.append(
                    {
                        "evidence_id": f"evidence_{counter:03d}",
                        "agent": result.agent,
                        "agent_summary": compact_text(result.summary, 260),
                        "claim": claim_text,
                        "reason": reason,
                        "evidence_type": claim.evidence_type,
                        "source_profile_id": claim.source_profile_id,
                        "source_field": claim.source_field,
                        "source_layer": claim.source_layer or "unknown",
                        "confidence": confidence,
                        "score": round(float(claim.score or 0.0), 4),
                        "rank": int(claim.rank or 0),
                        "supporting_profile_ids": claim.supporting_profile_ids,
                    }
                )
                counter += 1
        return rows

    def _select_synthesis_evidence(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        def sort_key(row: dict[str, Any]) -> tuple[float, float, int]:
            rank = int(row.get("rank") or 9999)
            confidence = row.get("confidence")
            return (float(row.get("score") or 0.0), float(confidence if confidence is not None else 0.0), -rank)

        sorted_rows = sorted(rows, key=sort_key, reverse=True)
        selected: list[dict[str, Any]] = []
        per_agent_count: dict[str, int] = {}
        for row in sorted_rows:
            agent = str(row.get("agent") or "unknown")
            # 防止某一个 Agent 的证据占满 prompt，保留多 Agent 合成空间。
            if per_agent_count.get(agent, 0) >= 4:
                continue
            selected.append(row)
            per_agent_count[agent] = per_agent_count.get(agent, 0) + 1
            if len(selected) >= self.evidence_top_k:
                break
        return selected

    def _call_llm(self, ctx: RAGContext, evidence_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        output_schema: dict[str, Any] = {
            "answer_sentences": [
                {"text": "one evidence-backed English sentence", "source_evidence_ids": ["evidence_001"]}
            ],
            "supporting_points": [
                {
                    "point": "evidence-backed point",
                    "source_evidence_ids": ["evidence_001"],
                    "evidence_layer": "processed|enriched|mixed|unknown",
                    "confidence": 0.0,
                }
            ],
            "uncertainties": [],
            "conflicts": [],
        }
        user_payload = {
            "query": ctx.query,
            "query_plan": ctx.plan.to_dict() if hasattr(ctx.plan, "to_dict") else (ctx.plan.__dict__ if ctx.plan else None),
            "warnings": ctx.warnings[:10],
            "supporting_point_top_k": self.supporting_point_top_k,
            "synthesis_evidence": evidence_rows,
            "output_schema": output_schema,
        }
        system_prompt = """
You are the StarCraft II RAG answer synthesizer.
Use only the provided synthesis_evidence. Do not add external StarCraft II knowledge.
The user query is not evidence.
Write all output text in English.
Return exactly one valid JSON object and no Markdown.
Use the schema with fields: answer_sentences, supporting_points, uncertainties, conflicts.
Do not output answer, direct_answer, or final_answer.
Every answer sentence must cite source_evidence_ids from the input.
Every supporting point must cite source_evidence_ids from the input.
Do not cite evidence that does not support the point.
processed evidence can be stated as raw KB facts.
enriched evidence is rule-based and must be phrased as a signal or inference, not as an absolute conclusion.
If supporting evidence answers the query, do not add an uncertainty saying the evidence provides no information.
Only use uncertainties for evidence boundaries, such as rule-enriched inference, missing direct combat simulation, or missing exact metrics.
If evidence conflicts, list the conflict and prefer direct, higher-scored, processed evidence.
Do not output more supporting_points than supporting_point_top_k.
"""
        response = self.llm_provider.complete(
            [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            max_new_tokens=self.max_new_tokens,
            temperature=0.0,
            enable_thinking=False,
        )
        return extract_json_object(response.text), {"model": response.model, **(response.metadata or {})}

    def _validate_output(self, data: dict[str, Any], evidence_rows: list[dict[str, Any]]) -> dict[str, Any]:
        evidence_by_id = {row["evidence_id"]: row for row in evidence_rows}

        supporting_points: list[dict[str, Any]] = []
        raw_points = data.get("supporting_points")
        if not isinstance(raw_points, list):
            raise LLMValidationError("LLM synthesizer output supporting_points is not a list")
        for item in raw_points[: self.supporting_point_top_k]:
            if not isinstance(item, dict):
                continue
            point = compact_text(item.get("point"), 520)
            if not point:
                continue
            if contains_cjk(point):
                raise LLMValidationError("LLM synthesizer supporting point contains CJK text")
            # Prompt 要求 source_evidence_ids；本地模型偶尔会输出近义字段，这里做兼容。
            raw_source_ids = item.get("source_evidence_ids")
            if raw_source_ids is None:
                raw_source_ids = item.get("source_evidence_id")
            if raw_source_ids is None:
                raw_source_ids = item.get("source_claim_ids")
            source_ids = [
                normalized_id
                for normalized_id in (normalize_evidence_id(value) for value in as_list(raw_source_ids))
                if normalized_id in evidence_by_id
            ]
            if not source_ids:
                raise LLMValidationError(f"Supporting point has no valid source_evidence_ids: {item}")
            self._validate_grounded_text(point, [evidence_by_id[source_id] for source_id in source_ids])
            layers = {str(evidence_by_id[source_id].get("source_layer") or "unknown") for source_id in source_ids}
            evidence_layer = self._normalize_layer(str(item.get("evidence_layer") or ""), layers)
            if evidence_layer == "enriched" and not self._has_caution(point):
                point = f"{point} {self.CAUTION_TEXT}"
            supporting_points.append(
                {
                    "point": point,
                    "source_evidence_ids": source_ids,
                    "evidence_layer": evidence_layer,
                    "confidence": clamp01(item.get("confidence")),
                }
            )

        if not supporting_points:
            raise LLMValidationError("LLM synthesizer output has no usable supporting points")

        answer_sentences: list[dict[str, Any]] = []
        raw_sentences = data.get("answer_sentences")
        if isinstance(raw_sentences, list):
            for item in raw_sentences[: self.supporting_point_top_k]:
                if not isinstance(item, dict):
                    continue
                text = compact_text(item.get("text"), 520)
                source_ids = [
                    normalized_id
                    for normalized_id in (normalize_evidence_id(value) for value in as_list(item.get("source_evidence_ids")))
                    if normalized_id in evidence_by_id
                ]
                if not text or not source_ids:
                    continue
                self._validate_grounded_text(text, [evidence_by_id[source_id] for source_id in source_ids])
                answer_sentences.append({"text": text, "source_evidence_ids": source_ids})
        # Backward-compatible models may still emit only supporting_points.
        # Their free-form `answer` is intentionally ignored to prevent an
        # uncited hallucination from becoming the visible answer.
        if not answer_sentences:
            answer_sentences = [
                {"text": point["point"], "source_evidence_ids": point["source_evidence_ids"]}
                for point in supporting_points
            ]
        if not answer_sentences:
            raise LLMValidationError("LLM synthesizer output has no grounded answer sentence")

        uncertainties = self._validate_text_list(data.get("uncertainties"), "uncertainties")
        uncertainties = self._filter_uncertainties(uncertainties, supporting_points)
        conflicts = self._validate_text_list(data.get("conflicts"), "conflicts")
        answer_text = " ".join(sentence["text"] for sentence in answer_sentences)
        if contains_cjk(answer_text):
            raise LLMValidationError("LLM synthesizer output answer contains CJK text")
        if any(point["evidence_layer"] == "enriched" for point in supporting_points) and not self._has_caution(answer_text):
            uncertainties.append(self.CAUTION_TEXT)

        return {
            "answer": answer_text,
            "answer_sentences": answer_sentences,
            "supporting_points": supporting_points,
            "uncertainties": self._dedupe_texts(uncertainties),
            "conflicts": self._dedupe_texts(conflicts),
        }

    def _validate_grounded_text(self, text: str, sources: list[dict[str, Any]]) -> None:
        """Reject answer-sentence numbers absent from its cited evidence."""

        source_text = " ".join(str(source.get("claim") or "") for source in sources)
        missing_numbers = [number for number in re.findall(r"\d+(?:\.\d+)?", text) if number not in source_text]
        if missing_numbers:
            raise LLMValidationError(f"Answer sentence contains numbers absent from cited evidence: {missing_numbers}")

    def _validate_text_list(self, value: Any, field_name: str) -> list[str]:
        result: list[str] = []
        for item in as_list(value):
            text = compact_text(item, 360)
            if not text:
                continue
            if contains_cjk(text):
                raise LLMValidationError(f"LLM synthesizer output field {field_name} contains CJK text")
            result.append(text)
        return result

    def _filter_uncertainties(self, uncertainties: list[str], supporting_points: list[dict[str, Any]]) -> list[str]:
        if not supporting_points:
            return uncertainties
        filtered: list[str] = []
        has_enriched = any(point["evidence_layer"] == "enriched" for point in supporting_points)
        for uncertainty in uncertainties:
            lower = uncertainty.lower()
            if any(pattern in lower for pattern in self.INSUFFICIENT_UNCERTAINTY_PATTERNS):
                # 如果已经有可引用的 supporting_points，就不要保留“没有证据”式矛盾表述。
                continue
            filtered.append(uncertainty)
        if has_enriched and not any(self._has_caution(item) for item in filtered):
            filtered.append("The available evidence is based on rule-enriched signals and does not prove a guaranteed combat outcome.")
        return filtered

    def _dedupe_texts(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(value)
        return result

    def _normalize_layer(self, requested_layer: str, source_layers: set[str]) -> str:
        if len(source_layers) == 1:
            layer = next(iter(source_layers))
            return layer if layer in {"processed", "enriched"} else "unknown"
        if len(source_layers) > 1:
            return "mixed"
        return requested_layer if requested_layer in {"processed", "enriched", "mixed", "unknown"} else "unknown"

    def _has_caution(self, text: str) -> bool:
        lower = text.lower()
        return any(term in lower for term in self.CAUTION_TERMS)

    def _build_answer_object(self, data: dict[str, Any], evidence_rows: list[dict[str, Any]], ctx: RAGContext) -> dict[str, Any]:
        evidence_by_id = {row["evidence_id"]: row for row in evidence_rows}
        supporting_points: list[dict[str, Any]] = []
        for point in data["supporting_points"]:
            sources: list[dict[str, Any]] = []
            for source_id in point["source_evidence_ids"]:
                row = evidence_by_id[source_id]
                sources.append(
                    {
                        "evidence_id": source_id,
                        "agent": row.get("agent", ""),
                        "evidence_type": row.get("evidence_type", ""),
                        "source_profile_id": row.get("source_profile_id", ""),
                        "source_field": row.get("source_field", ""),
                        "source_layer": row.get("source_layer", "unknown"),
                    }
                )
            supporting_points.append({**point, "sources": sources})

        answer_sentence_rows: list[dict[str, Any]] = []
        for sentence in data["answer_sentences"]:
            answer_sentence_rows.append(
                {
                    **sentence,
                    "sources": [
                        {"evidence_id": source_id, "source_profile_id": evidence_by_id[source_id].get("source_profile_id", ""), "source_field": evidence_by_id[source_id].get("source_field", "")}
                        for source_id in sentence["source_evidence_ids"]
                    ],
                }
            )

        return {
            "text": " ".join(sentence["text"] for sentence in data["answer_sentences"]),
            "answer_sentences": answer_sentence_rows,
            "supporting_points": supporting_points,
            "uncertainties": data["uncertainties"],
            "conflicts": data["conflicts"],
            "used_profiles": ctx.used_profiles,
        }
