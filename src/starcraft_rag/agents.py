from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any

from starcraft_rag.context import AgentEvidence, AgentTask, EvidenceClaim, QueryPlan
from starcraft_rag.kb import KBStore
from starcraft_rag.llm import BaseLLMProvider


def fmt_list(values: list[Any] | None, empty: str = "No records", limit: int = 8) -> str:
    values = [str(value) for value in (values or []) if value not in (None, "")]
    if not values:
        return empty
    suffix = "" if len(values) <= limit else f" and {len(values) - limit} more"
    return ", ".join(values[:limit]) + suffix


def compact_text(text: Any, limit: int = 220) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def clamp01(value: Any, default: float = 0.5) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def contains_cjk(text: Any) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", str(text or "")))


def normalize_object_key(value: Any) -> str:
    return re.sub(r"[\s_\-\.:'\"/\\()\[\]{}]+", "", str(value or "").lower())


OBJECT_MENTION_STOPWORDS = {
    "a",
    "an",
    "and",
    "anti",
    "aoe",
    "air",
    "agent",
    "armored",
    "attack",
    "biological",
    "claim",
    "combat",
    "cost",
    "current",
    "detector",
    "effect",
    "enriched",
    "evidence",
    "fast",
    "from",
    "ground",
    "ii",
    "light",
    "massive",
    "mechanical",
    "normal",
    "processed",
    "production",
    "psionic",
    "protoss",
    "record",
    "relation",
    "scenario",
    "source",
    "starcraft",
    "structure",
    "summary",
    "target",
    "terran",
    "the",
    "this",
    "unit",
    "unknown",
    "zerg",
}


def extract_object_like_mentions(text: Any) -> list[str]:
    """从 LLM 输出中抽取可能的单位、建筑、技能名称，用于证据一致性校验。"""
    raw = str(text or "")
    mentions: list[str] = []

    def add(value: str) -> None:
        words = value.strip().split()
        while words and words[0].lower() in OBJECT_MENTION_STOPWORDS:
            words.pop(0)
        while words and words[-1].lower() in OBJECT_MENTION_STOPWORDS:
            words.pop()
        cleaned = " ".join(words).strip(" .,:;()[]{}")
        key = normalize_object_key(cleaned)
        if not cleaned or len(key) < 3 or key in OBJECT_MENTION_STOPWORDS:
            return
        if cleaned not in mentions:
            mentions.append(cleaned)

    for match in re.finditer(r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*){0,3}\b", raw):
        add(match.group(0))
    for match in re.finditer(r"\b(?:protoss|terran|zerg|neutral)_[a-z0-9_]+\b", raw, flags=re.IGNORECASE):
        add(match.group(0))
    return mentions


def profile_object_metadata(profile: dict[str, Any]) -> dict[str, Any]:
    """把 profile 的主体对象显式写进 metadata，避免 LLM 把 A 的字段误写成 B 的结论。"""
    profile_type = profile.get("profile_type")
    names: list[Any] = []
    ids: list[Any] = []
    metadata: dict[str, Any] = {}

    if profile_type == "entity_profile":
        identity = profile.get("identity") or {}
        entity_id = profile.get("entity_id")
        names = [identity.get("name"), *(identity.get("aliases") or [])]
        ids = [entity_id]
        metadata.update({"entity_id": entity_id, "profile_name": identity.get("name") or entity_id})
    elif profile_type == "ability_profile":
        owner = profile.get("owner") or {}
        names = [profile.get("ability_name"), profile.get("ability_id"), owner.get("name"), owner.get("entity_id")]
        ids = [profile.get("ability_id"), owner.get("entity_id")]
        metadata.update(
            {
                "ability_id": profile.get("ability_id"),
                "ability_name": profile.get("ability_name"),
                "owner_entity_id": owner.get("entity_id"),
                "owner_name": owner.get("name"),
                "profile_name": profile.get("ability_name") or profile.get("ability_id"),
            }
        )
    elif profile_type == "relation_profile":
        source = profile.get("source") or {}
        target = profile.get("target") or {}
        source_names = [source.get("name"), source.get("entity_id")]
        target_names = [target.get("name"), target.get("entity_id")]
        names = [*source_names, *target_names]
        ids = [source.get("entity_id"), target.get("entity_id"), profile.get("relation_id")]
        metadata.update(
            {
                "relation_id": profile.get("relation_id"),
                "source_object_names": unique_keep_order([str(v) for v in source_names if v]),
                "target_object_names": unique_keep_order([str(v) for v in target_names if v]),
                "profile_name": profile.get("relation_id"),
            }
        )
    elif profile_type == "scenario_profile":
        scenario_tag = profile.get("scenario_tag")
        names = [scenario_tag]
        ids = [scenario_tag]
        metadata.update({"scenario_tag": scenario_tag, "profile_name": scenario_tag})

    metadata["object_names"] = unique_keep_order([str(v) for v in names if v])
    metadata["object_ids"] = unique_keep_order([str(v) for v in ids if v])
    return metadata


def merge_claim_metadata(base: dict[str, Any], extra: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (extra or {}).items():
        if key in {"object_names", "object_ids", "source_object_names", "target_object_names"}:
            merged[key] = unique_keep_order([str(v) for v in [*as_list(merged.get(key)), *as_list(value)] if v])
        else:
            merged[key] = value
    return merged


def first_object_position(raw_query: str, values: list[Any]) -> int | None:
    query_key = normalize_object_key(raw_query)
    positions = [
        query_key.find(normalize_object_key(value))
        for value in values
        if normalize_object_key(value) and query_key.find(normalize_object_key(value)) >= 0
    ]
    return min(positions) if positions else None


def relation_direction_signal(raw_query: str, source_values: list[Any], target_values: list[Any]) -> float:
    """根据查询中对象出现顺序，为 A -> B 的关系方向提供轻量排序信号。"""
    source_pos = first_object_position(raw_query, source_values)
    target_pos = first_object_position(raw_query, target_values)
    if source_pos is None or target_pos is None:
        return 0.0
    return 0.28 if source_pos < target_pos else -0.22


class LLMJSONError(ValueError):
    """用于区分 LLM 输出 JSON 解析失败，便于 run_eval 统计。"""


class LLMValidationError(ValueError):
    """用于区分 LLM 输出可解析但不符合 Agent 证据协议的情况。"""


def repair_json_object_text(text: str) -> str:
    """对本地模型常见 JSON 小错误做一次轻量修复。

    这里只处理低风险格式错误：尾随逗号、相邻字段之间漏逗号。
    不尝试改写语义内容，避免把错误答案“修成”看似合法的答案。
    """

    repaired = re.sub(r",\s*([}\]])", r"\1", text)
    repaired = re.sub(
        r'(?<=[}\]"\d])\s*\n\s*(?="(?:agent|summary|claims|warnings|claim|evidence_type|source_claim_ids|source_claim_id|reason|confidence)"\s*:)',
        ",\n",
        repaired,
    )
    repaired = re.sub(
        r'(?<=[}\]"\d])\s+(?="(?:agent|summary|claims|warnings|claim|evidence_type|source_claim_ids|source_claim_id|reason|confidence)"\s*:)',
        ", ",
        repaired,
    )
    return repaired


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
        json_text = cleaned[start : end + 1]
        repaired = repair_json_object_text(json_text)
        if repaired != json_text:
            try:
                data = json.loads(repaired)
                data.setdefault("_json_repaired", True)
                return data
            except json.JSONDecodeError:
                pass
        raise LLMJSONError(f"Failed to parse LLM JSON output: {exc}") from exc


def normalize_claim_id(value: Any, agent_name: str) -> str:
    """兼容 LLM 把 AbilityAgent_001 写成 AbilityAgent_1 的情况。"""

    text = str(value or "").strip()
    if not text:
        return ""
    match = re.fullmatch(rf"({re.escape(agent_name)})_(\d+)", text, flags=re.IGNORECASE)
    if match:
        return f"{agent_name}_{int(match.group(2)):03d}"
    return text


@dataclass
class CandidateClaim:
    """Agent 内部候选证据，不写入 runtime_kb。

    CandidateClaim 的职责是把 profile 里的字段变成 LLM 容易阅读、且能追溯来源的
    小证据块。LLM Agent 最终只能引用这里给出的 claim_id。
    """

    claim_id: str
    claim_text: str
    claim_text_en: str
    evidence_type: str
    source_profile_id: str
    source_profile_type: str
    source_field: str
    source_layer: str
    confidence: float | None = None
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


COMMON_AGENT_SYSTEM_PROMPT = """
You are a typed knowledge agent in a StarCraft II RAG system.
You are not the final chat model. Your only job is to select relevant local evidence from the provided evidence_claims.
Strict requirements:
1. Answer only from the provided evidence_claims. Do not add external StarCraft II knowledge.
2. Select only claim_id values from the input evidence_claims. Never generate, paraphrase, or explain a claim yourself.
3. selected_claim_ids must be non-empty, unique, and contain at most output_top_k IDs.
4. Every selected_claim_id must exactly match an input claim_id.
5. Unit names, ability names, and effect words in the user query are objects to explain, not factual evidence.
6. If a query has multiple parts, select every relevant candidate available to this agent, up to output_top_k.
7. Output only one valid minified JSON object. Do not output Markdown, code fences, comments, or extra explanation.
8. Use plain double quotes. Escape any quote characters inside strings.
9. The JSON object must have exactly these top-level keys: agent, selected_claim_ids, warnings.
10. All warning strings must be written in English.
"""


AGENT_SPECIFIC_PROMPTS = {
    "UnitProfileAgent": "Explain only unit/building attributes, attack targets, survival data, combat roles, and tactical profile. Do not answer production requirements. If the query is about ability effects but the evidence only contains unit profile data, state only the unit-profile clue and leave specific ability effects to AbilityAgent.",
    "AbilityAgent": "Explain only ability effects, ability constraints, applicable scenarios, and ability ownership. Do not add mechanisms beyond the provided evidence.",
    "CounterAgent": "Explain only counter relations, relation direction, and relation basis. Do not explain detailed ability mechanics. If the query asks whether A is strong against B, prioritize A -> B and do not report B -> A unless the query explicitly asks for reciprocal relations. If evidence comes from an enriched relation, state that it is a rule-enriched signal rather than an absolute win/loss conclusion.",
    "TechTreeAgent": "Explain only costs, production source, tech requirements, upgrades, and action conditions. Do not answer combat strength.",
    "ScenarioRouterAgent": "Explain only scenario identification, triggers, recommended knowledge sources, and candidate entities/abilities/relations. Do not generate a full tactical plan. Do not replace AbilityAgent for detailed ability values or effects.",
}


AGENT_EVIDENCE_TYPE_HINTS = {
    "UnitProfileAgent": ["identity", "target", "type", "survival", "role", "strength", "weakness", "tactical"],
    "AbilityAgent": ["ability", "effect", "constraint", "scenario", "owner"],
    "CounterAgent": ["relation", "counter", "source", "target", "basis", "confidence"],
    "TechTreeAgent": ["cost", "produce", "tech", "upgrade", "action"],
    "ScenarioRouterAgent": ["scenario", "trigger", "recommended", "matched"],
}


AGENT_EVIDENCE_PRIORITIES = {
    "UnitProfileAgent": ["entity_target", "entity_type_profile", "entity_survival", "entity_enrichment", "entity_identity", "entity_tactical"],
    "AbilityAgent": ["ability_base_effect", "ability_metrics", "ability_effects", "ability_constraints", "ability_scenarios", "ability_owner"],
    "CounterAgent": ["counter_relation", "counter_type_basis"],
    "TechTreeAgent": ["tech_cost", "tech_tree_edge", "tech_upgrade", "tech_action_condition"],
    "ScenarioRouterAgent": [
        "scenario_description",
        "scenario_triggers",
        "scenario_matched_abilities",
        "scenario_matched_entities",
        "scenario_recommended_kbs",
        "scenario_matched_relations",
    ],
}


class BaseAgent(ABC):
    name = "BaseAgent"

    def __init__(
        self,
        agent_mode: str = "rule",
        llm_provider: BaseLLMProvider | None = None,
        llm_max_new_tokens: int = 768,
        claim_top_k: int = 8,
        output_top_k: int = 5,
    ) -> None:
        self.agent_mode = agent_mode
        self.llm_provider = llm_provider
        # Candidate selection has a deliberately tiny, fixed response contract.
        # Keeping this independent of the answer/synthesis budget avoids verbose
        # Qwen outputs that previously caused JSON and zero-claim fallbacks.
        self.llm_max_new_tokens = 256
        self.claim_top_k = claim_top_k
        self.output_top_k = output_top_k

    def run(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        if self.agent_mode in {"local-llm", "llm"} and self.llm_provider is not None:
            return self._run_llm(task, kb_store, query_plan)
        return self._run_rule(task, kb_store, query_plan)

    @abstractmethod
    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        raise NotImplementedError

    @abstractmethod
    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        raise NotImplementedError

    def _new_evidence(self) -> AgentEvidence:
        return AgentEvidence(agent=self.name)

    def _run_rule_from_candidates(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        # 规则 Agent 也走 CandidateClaim 排序与裁剪，避免把一个 profile 中的所有字段都塞进答案。
        # 这样 rule/local-llm 两种模式使用同一套 evidence 选择入口，后续做对比更稳定。
        candidates = self._rank_claims(self._build_candidate_claims(task, kb_store, query_plan), task, query_plan)
        evidence = self._new_evidence()
        if not candidates:
            evidence.warnings.append(f"{self.name} did not find usable candidate claims.")
            evidence.metadata.update({"mode": "rule-ranked", "candidate_claim_count": 0, "output_claim_count": 0})
            return evidence

        selected = self._select_diverse_claims(candidates, self.output_top_k)
        used_profiles: list[str] = []
        for rank, candidate in enumerate(selected, start=1):
            used_profiles.append(candidate.source_profile_id)
            evidence.claims.append(
                self._claim(
                    claim=candidate.claim_text,
                    evidence_type=candidate.evidence_type,
                    source_profile_id=candidate.source_profile_id,
                    source_field=candidate.source_field,
                    confidence=candidate.confidence,
                    source_layer=candidate.source_layer,
                    score=candidate.score,
                    rank=rank,
                    reason="Selected by rule-based candidate claim ranking.",
                    matched_terms=as_list(candidate.metadata.get("matched_terms")),
                    supporting_profile_ids=[candidate.source_profile_id] if candidate.source_profile_id else [],
                    metadata={
                        "candidate_claim_id": candidate.claim_id,
                        "rule_agent": self.name,
                        "candidate_metadata": candidate.metadata,
                    },
                )
            )

        evidence.used_profiles = unique_keep_order(used_profiles)
        evidence.metadata.update(
            {
                "mode": "rule-ranked",
                "candidate_claim_count": len(candidates),
                "output_claim_count": len(selected),
            }
        )
        return evidence

    def _select_diverse_claims(self, candidates: list[CandidateClaim], limit: int) -> list[CandidateClaim]:
        # 先限制同一 profile 和同一 evidence_type 的占比，防止 UnitProfileAgent/ScenarioRouterAgent
        # 被一个大 profile 或一个大字段淹没；不足时再按分数补齐。
        limit = max(1, limit)
        if self.name == "CounterAgent":
            # 如果查询明确呈现 A -> B 的顺序，只把同方向的关系 profile 交给 CounterAgent。
            # 这能避免 “A strong against B” 的问题同时输出 B -> A。
            directed_profile_ids = {
                claim.source_profile_id
                for claim in candidates
                if float(claim.metadata.get("direction_score") or 0.0) > 0
            }
            if directed_profile_ids:
                candidates = [claim for claim in candidates if claim.source_profile_id in directed_profile_ids]
        focused_candidates = [claim for claim in candidates if int(claim.metadata.get("query_focus_hits") or 0) > 0]
        # When the query names a concrete property (health, Land, cost, ...),
        # preserve candidates about that property before generic identity,
        # scenario, or type-profile rows.  This fixes a major source of
        # "evidence was retrieved but not extracted" errors.
        selection_pool = focused_candidates or candidates
        selected: list[CandidateClaim] = []
        selected_ids: set[str] = set()
        profile_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        priorities = AGENT_EVIDENCE_PRIORITIES.get(self.name, [])

        def add(candidate: CandidateClaim) -> None:
            if candidate.claim_id in selected_ids:
                return
            selected.append(candidate)
            selected_ids.add(candidate.claim_id)
            profile_counts[candidate.source_profile_id] = profile_counts.get(candidate.source_profile_id, 0) + 1
            type_counts[candidate.evidence_type] = type_counts.get(candidate.evidence_type, 0) + 1

        # 先给高优先级 evidence_type 各保留一条，避免关键字段被普通 metadata 类证据挤掉。
        for evidence_type in priorities:
            if len(selected) >= limit:
                break
            for candidate in selection_pool:
                if candidate.evidence_type == evidence_type:
                    add(candidate)
                    break

        for candidate in selection_pool:
            if len(selected) >= limit:
                break
            if candidate.claim_id in selected_ids:
                continue
            if profile_counts.get(candidate.source_profile_id, 0) >= 2:
                continue
            if type_counts.get(candidate.evidence_type, 0) >= 2:
                continue
            add(candidate)

        for candidate in selection_pool:
            if len(selected) >= limit:
                break
            if candidate.claim_id not in selected_ids:
                add(candidate)

        return selected

    def _claim(
        self,
        claim: str,
        evidence_type: str,
        source_profile_id: str,
        source_field: str,
        confidence: float | None = None,
        source_layer: str | None = None,
        score: float = 0.0,
        rank: int = 0,
        reason: str = "",
        matched_terms: list[str] | None = None,
        supporting_profile_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceClaim:
        return EvidenceClaim(
            claim=claim,
            evidence_type=evidence_type,
            source_profile_id=source_profile_id,
            source_field=source_field,
            confidence=confidence,
            source_layer=source_layer,
            score=score,
            rank=rank,
            reason=reason,
            matched_terms=matched_terms or [],
            supporting_profile_ids=supporting_profile_ids or [],
            metadata={"producing_agent": self.name, **(metadata or {})},
        )

    def _candidate(
        self,
        claims: list[CandidateClaim],
        profile: dict[str, Any],
        claim_text: str,
        evidence_type: str,
        source_field: str,
        source_layer: str,
        confidence: float | None = None,
        claim_text_en: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        text = compact_text(claim_text, 520)
        if not text:
            return
        # 每条候选证据都带上它所属的对象，后续 prompt 与 validator 会用它阻止跨对象归因。
        merged_metadata = merge_claim_metadata(profile_object_metadata(profile), metadata)
        claims.append(
            CandidateClaim(
                claim_id=f"{self.name}_{len(claims) + 1:03d}",
                claim_text=text,
                claim_text_en=compact_text(claim_text_en, 520),
                evidence_type=evidence_type,
                source_profile_id=profile.get("profile_id", ""),
                source_profile_type=profile.get("profile_type", ""),
                source_field=source_field,
                source_layer=source_layer,
                confidence=confidence,
                metadata=merged_metadata,
            )
        )

    def _run_llm(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        # LLM Agent does not create facts.  It only selects from canonical
        # CandidateClaims, so every resulting EvidenceClaim is grounded by
        # construction instead of by a brittle post-hoc text validator.
        candidates = self._rank_claims(self._build_candidate_claims(task, kb_store, query_plan), task, query_plan)
        if not candidates:
            evidence = self._run_rule(task, kb_store, query_plan)
            evidence.metadata.update(
                {
                    "mode": "rule-no-candidate",
                    "candidate_claim_count": 0,
                    "prompt_claim_count": 0,
                    "selected_claim_count": 0,
                    "llm_selector_retries": 0,
                    "llm_selector_called": False,
                    "llm_selector_success": False,
                    "llm_agent_fallback": False,
                    "llm_json_parse_failure": False,
                    "fallback_reason": "No CandidateClaim available; LLM was not called",
                }
            )
            return evidence

        prompt_claims = self._select_diverse_claims(candidates, self.claim_top_k)
        raw_output = ""
        correction = ""
        last_error: Exception | None = None
        saw_json_error = False
        for attempt in range(2):
            try:
                llm_data, raw_output = self._call_llm_reasoner(query_plan, task, prompt_claims, correction=correction)
                evidence = self._evidence_from_llm(llm_data, prompt_claims)
                evidence.metadata.update(
                    {
                        "mode": "local-llm-selector",
                        "candidate_claim_count": len(candidates),
                        "prompt_claim_count": len(prompt_claims),
                        "selected_claim_count": len(evidence.claims),
                        "output_claim_count": len(evidence.claims),
                        "llm_provider": getattr(self.llm_provider, "name", ""),
                        "llm_selector_retries": attempt,
                        "llm_selector_called": True,
                        "llm_selector_success": True,
                        "llm_agent_fallback": False,
                        "llm_json_parse_failure": False,
                        "llm_json_repaired": bool(llm_data.get("_json_repaired")),
                        "raw_llm_output_preview": compact_text(raw_output, 1000),
                    }
                )
                return evidence
            except Exception as exc:
                last_error = exc
                saw_json_error = saw_json_error or isinstance(exc, LLMJSONError)
                correction = (
                    "Your previous response was invalid: "
                    f"{compact_text(str(exc), 300)}. Return only the required JSON object with one or more "
                    "unique selected_claim_ids copied exactly from the supplied evidence_claims."
                )

        fallback = self._run_rule(task, kb_store, query_plan)
        fallback.warnings.append(f"LLM selector fallback: {self.name}: {last_error}")
        if saw_json_error:
            fallback.warnings.append(f"LLM JSON parse failure: {self.name}")
        fallback.metadata.update(
            {
                "mode": "rule-selector-fallback",
                "candidate_claim_count": len(candidates),
                "prompt_claim_count": len(prompt_claims),
                "selected_claim_count": 0,
                "llm_selector_retries": 1,
                "llm_selector_called": True,
                "llm_selector_success": False,
                "llm_agent_fallback": True,
                "llm_json_parse_failure": saw_json_error,
                "fallback_reason": str(last_error or "LLM selector failed"),
                "raw_llm_output_preview": compact_text(raw_output, 1000),
            }
        )
        return fallback

    def _call_llm_reasoner(
        self,
        query_plan: QueryPlan,
        task: AgentTask,
        claims: list[CandidateClaim],
        *,
        correction: str = "",
    ) -> tuple[dict[str, Any], str]:
        # Prompt 中只放查询计划、当前 Agent 任务和 Top-K 证据块。
        # 这样可以避免 LLM 因上下文过大而引入未检索到的知识。
        claim_payload = [
            {
                "claim_id": claim.claim_id,
                "text": claim.claim_text,
                "evidence_type": claim.evidence_type,
                "source_profile_id": claim.source_profile_id,
                "source_field": claim.source_field,
                "source_layer": claim.source_layer,
                "confidence": claim.confidence,
                "object_names": as_list(claim.metadata.get("object_names"))[:10],
                "object_ids": as_list(claim.metadata.get("object_ids"))[:10],
            }
            for claim in claims
        ]
        user_prompt = {
            "query": query_plan.raw_query,
            "query_plan": {
                "intent_candidates": query_plan.intent_candidates,
                "query_terms": query_plan.query_terms,
                "entities": query_plan.entities,
                "abilities": query_plan.abilities,
                "scenario_tags": query_plan.scenario_tags,
                "answer_requirements": query_plan.answer_requirements,
            },
            "agent": self.name,
            "output_top_k": self.output_top_k,
            "task_answer_requirements": task.metadata.get("answer_requirements", []),
            "evidence_claims": claim_payload,
            "output_schema": '{"agent":"'
            + self.name
            + '","selected_claim_ids":["'
            + self.name
            + '_001"],"warnings":[]}',
            "selection_rule": "Select one or more IDs that directly help answer this agent task. IDs must be copied exactly from evidence_claims. Do not emit claim text.",
            "format_rule": "Return compact valid JSON only. Do not add trailing commas or Markdown. selected_claim_ids cannot be empty.",
            "correction": correction,
        }
        messages = [
            {"role": "system", "content": f"{COMMON_AGENT_SYSTEM_PROMPT.strip()}\n{AGENT_SPECIFIC_PROMPTS.get(self.name, '')}"},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ]
        response = self.llm_provider.complete(
            messages,
            max_new_tokens=self.llm_max_new_tokens,
            temperature=0.0,
            enable_thinking=False,
        )
        return extract_json_object(response.text), response.text

    def _evidence_from_llm(self, data: dict[str, Any], candidates: list[CandidateClaim]) -> AgentEvidence:
        # Candidate IDs are the grounding boundary.  The LLM never supplies
        # user-visible fact text or source metadata.
        if data.get("agent") != self.name:
            raise LLMValidationError(f"LLM agent name mismatch: {data.get('agent')} != {self.name}")
        selected_claim_ids = data.get("selected_claim_ids")
        if not isinstance(selected_claim_ids, list):
            raise LLMValidationError("LLM output field selected_claim_ids is not a list")
        if not selected_claim_ids:
            raise LLMValidationError("LLM selector returned no selected_claim_ids")
        if len(selected_claim_ids) > self.output_top_k:
            raise LLMValidationError(f"LLM selector returned more than {self.output_top_k} claim IDs")
        if any(not isinstance(claim_id, str) or not claim_id.strip() for claim_id in selected_claim_ids):
            raise LLMValidationError("LLM selector contains an empty or non-string claim ID")
        if len(set(selected_claim_ids)) != len(selected_claim_ids):
            raise LLMValidationError("LLM selector returned duplicate claim IDs")

        candidate_by_id = {claim.claim_id: claim for claim in candidates}
        unknown_ids = [claim_id for claim_id in selected_claim_ids if claim_id not in candidate_by_id]
        if unknown_ids:
            raise LLMValidationError(f"LLM selector returned unknown claim IDs: {unknown_ids}")

        evidence = AgentEvidence(agent=self.name, summary=f"Selected {len(selected_claim_ids)} canonical candidate claim(s).")
        for warning in as_list(data.get("warnings")):
            if warning:
                evidence.warnings.append(str(warning))

        used_profiles: list[str] = []
        for selected_claim_id in selected_claim_ids:
            candidate = candidate_by_id[selected_claim_id]
            supporting_profile_ids = [candidate.source_profile_id] if candidate.source_profile_id else []
            used_profiles.extend(supporting_profile_ids)
            matched_terms = as_list(candidate.metadata.get("matched_terms"))

            reason = "Selected by local LLM from canonical candidate claims."
            if self.name == "CounterAgent" and candidate.source_layer == "enriched":
                reason += " This relation comes from the enriched rule layer and should be treated as a rule-enriched signal, not an absolute win/loss conclusion."
            evidence.claims.append(
                self._claim(
                    claim=candidate.claim_text,
                    evidence_type=candidate.evidence_type,
                    source_profile_id=candidate.source_profile_id,
                    source_field=candidate.source_field,
                    confidence=candidate.confidence,
                    source_layer=candidate.source_layer,
                    score=candidate.score,
                    rank=len(evidence.claims) + 1,
                    reason=reason,
                    matched_terms=matched_terms,
                    supporting_profile_ids=supporting_profile_ids,
                    metadata={
                        "source_claim_ids": [selected_claim_id],
                        "llm_agent": self.name,
                        "candidate_evidence_types": [candidate.evidence_type],
                        "source_claim_texts": [candidate.claim_text],
                        "selector_claim_id": selected_claim_id,
                    },
                )
            )
        evidence.used_profiles = unique_keep_order(used_profiles)
        return evidence

    def _rank_claims(self, claims: list[CandidateClaim], task: AgentTask, query_plan: QueryPlan) -> list[CandidateClaim]:
        # 这里的排序只用于减少输入给 LLM 的证据数量，不作为最终事实判断。
        # 分数综合了 query term 命中、profile 检索分、证据类型和 enriched confidence。
        profile_support = task.metadata.get("profile_support_scores", {}) if task.metadata else {}
        terms = unique_keep_order(
            [
                query_plan.raw_query,
                *query_plan.query_terms,
                *query_plan.intent_candidates,
                *query_plan.entities,
                *query_plan.abilities,
                *query_plan.scenario_tags,
            ]
        )
        lower_terms = [(term, str(term).lower()) for term in terms if str(term).strip()]
        type_hints = AGENT_EVIDENCE_TYPE_HINTS.get(self.name, [])
        type_priorities = AGENT_EVIDENCE_PRIORITIES.get(self.name, [])
        focus_vocabulary = {
                "ability", "armor", "attack", "cost", "cooldown", "damage", "energy", "health", "land", "lift",
                "produce", "produced", "production", "range", "require", "requires", "shield", "space", "target",
        }
        focus_terms = {
            part
            for _, lower in lower_terms
            for part in re.split(r"[_\s-]+", lower)
            if part in focus_vocabulary
        }

        for claim in claims:
            text = f"{claim.claim_text} {claim.claim_text_en} {claim.evidence_type} {json.dumps(claim.metadata, ensure_ascii=False)}".lower()
            matched_terms = [term for term, lower in lower_terms if lower and lower in text]
            focus_hits = sum(int(str(term).lower() in text) for term in focus_terms)
            score = 0.05
            score += min(len(matched_terms) * 0.08, 0.4)
            score += 0.22 * focus_hits
            if any(entity.lower() in text for entity in query_plan.entities):
                score += 0.25
            if any(ability.lower() in text for ability in query_plan.abilities):
                score += 0.25
            if any(tag.lower() in text for tag in query_plan.scenario_tags):
                score += 0.18
            if any(hint in claim.evidence_type.lower() for hint in type_hints):
                score += 0.12
            if claim.evidence_type in type_priorities:
                # Agent 专属证据类型优先级，位置越靠前加权越高。
                score += max(0.0, 0.18 - 0.025 * type_priorities.index(claim.evidence_type))
            if self.name == "CounterAgent":
                direction_score = relation_direction_signal(
                    query_plan.raw_query,
                    [
                        *as_list(claim.metadata.get("source_object_names")),
                        claim.metadata.get("source_entity_id"),
                    ],
                    [
                        *as_list(claim.metadata.get("target_object_names")),
                        claim.metadata.get("target_entity_id"),
                    ],
                )
                score += direction_score
                claim.metadata["direction_score"] = direction_score
            if claim.confidence is not None:
                score += 0.1 * clamp01(claim.confidence)
            if claim.source_layer == "enriched":
                score += 0.03
            try:
                score += 0.3 * clamp01(profile_support.get(claim.source_profile_id), default=0.0)
            except AttributeError:
                pass
            claim.score = round(max(0.0, min(1.0, score)), 4)
            claim.metadata["matched_terms"] = matched_terms
            claim.metadata["query_focus_hits"] = focus_hits
            claim.metadata["query_term_hits"] = len(matched_terms)
        return sorted(
            claims,
            key=lambda item: (
                int(item.metadata.get("query_focus_hits") or 0),
                int(item.metadata.get("query_term_hits") or 0),
                item.score,
            ),
            reverse=True,
        )


class UnitProfileAgent(BaseAgent):
    name = "UnitProfileAgent"

    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        return self._run_rule_from_candidates(task, kb_store, query_plan)

    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        claims: list[CandidateClaim] = []
        for ref in task.profile_refs:
            profile = kb_store.get_profile(ref.profile_id)
            if not profile or profile.get("profile_type") != "entity_profile":
                continue
            identity = profile.get("identity") or {}
            attributes = profile.get("attributes") or {}
            enrich = profile.get("local_enrichment") or {}
            tactical = profile.get("tactical_profile") or {}
            name = identity.get("name") or profile.get("entity_id")
            self._candidate(claims, profile, f"{name} identity: race={identity.get('race')}; entity_type={identity.get('entity_type')}; subtype={identity.get('entity_subtype')}.", "entity_identity", "identity", "processed")
            self._candidate(claims, profile, f"{name} attack targets: {fmt_list(attributes.get('target'))}.", "entity_target", "attributes.target", "processed", metadata={"entity_id": profile.get("entity_id")})
            self._candidate(claims, profile, f"{name} self types: {fmt_list(attributes.get('type_self'))}; anti types: {fmt_list(attributes.get('type_anti'))}.", "entity_type_profile", "attributes.type_self/type_anti", "processed")
            survival = attributes.get("survival") or {}
            if survival:
                self._candidate(claims, profile, f"{name} survival attributes: {', '.join(f'{k}={v}' for k, v in survival.items() if v is not None)}.", "entity_survival", "attributes.survival", "processed")
            if enrich:
                self._candidate(
                    claims,
                    profile,
                    f"{name} rule-enriched profile: combat roles={fmt_list(enrich.get('combat_roles'))}; strengths={fmt_list(enrich.get('strengths'))}; weaknesses={fmt_list(enrich.get('weaknesses'))}; scenario tags={fmt_list(enrich.get('scenario_tags'))}.",
                    "entity_enrichment",
                    "local_enrichment",
                    "enriched",
                    confidence=enrich.get("confidence"),
                )
            if tactical.get("micro_notes"):
                self._candidate(claims, profile, f"{name} tactical guidance: {fmt_list(tactical.get('micro_notes'), limit=6)}.", "entity_tactical", "tactical_profile.micro_notes", "enriched", confidence=tactical.get("confidence"))
        return claims


class AbilityAgent(BaseAgent):
    name = "AbilityAgent"

    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        return self._run_rule_from_candidates(task, kb_store, query_plan)

    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        claims: list[CandidateClaim] = []
        for ref in task.profile_refs:
            profile = kb_store.get_profile(ref.profile_id)
            if not profile or profile.get("profile_type") != "ability_profile":
                continue
            ability_name = profile.get("ability_name") or profile.get("ability_id")
            owner = profile.get("owner") or {}
            base = profile.get("base_ability") or {}
            enrich = profile.get("local_enrichment") or {}
            self._candidate(claims, profile, f"{ability_name} ownership: it belongs to {owner.get('name') or owner.get('entity_id') or 'unknown owner'}.", "ability_owner", "owner", "processed", metadata={"ability_id": profile.get("ability_id"), "owner_entity_id": owner.get("entity_id")})
            if base.get("effect_text") or base.get("text"):
                self._candidate(claims, profile, f"{ability_name} base effect text: {compact_text(base.get('effect_text') or base.get('text'), 420)}", "ability_base_effect", "base_ability.effect_text", "processed")
            if base.get("metrics"):
                metrics_text = ", ".join(f"{key}={value}" for key, value in sorted((base.get("metrics") or {}).items()))
                self._candidate(claims, profile, f"{ability_name} structured metrics: {metrics_text}.", "ability_metrics", "base_ability.metrics", "processed")
            if enrich:
                self._candidate(claims, profile, f"{ability_name} enriched effects: {fmt_list(enrich.get('ability_effects'))}.", "ability_effects", "local_enrichment.ability_effects", "enriched", confidence=enrich.get("confidence"))
                self._candidate(claims, profile, f"{ability_name} usage constraints: {fmt_list(enrich.get('constraints'))}.", "ability_constraints", "local_enrichment.constraints", "enriched", confidence=enrich.get("confidence"))
                self._candidate(claims, profile, f"{ability_name} scenario tags: {fmt_list(enrich.get('scenario_tags'))}.", "ability_scenarios", "local_enrichment.scenario_tags", "enriched", confidence=enrich.get("confidence"))
        return claims


class CounterAgent(BaseAgent):
    name = "CounterAgent"

    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        return self._run_rule_from_candidates(task, kb_store, query_plan)

    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        claims: list[CandidateClaim] = []
        for ref in task.profile_refs:
            profile = kb_store.get_profile(ref.profile_id)
            if not profile or profile.get("profile_type") != "relation_profile":
                continue
            source = profile.get("source") or {}
            target = profile.get("target") or {}
            source_name = source.get("name") or source.get("entity_id") or "unknown source"
            target_name = target.get("name") or target.get("entity_id") or target.get("target_type") or "type-level target"
            layer = profile.get("relation_layer") or "unknown"
            basis = profile.get("basis") or profile.get("reason") or profile.get("text") or "not recorded"
            metadata = {
                "relation_id": profile.get("relation_id"),
                "source_entity_id": source.get("entity_id"),
                "target_entity_id": target.get("entity_id"),
                "target_type": target.get("target_type"),
                "relation_layer": layer,
            }
            self._candidate(
                claims,
                profile,
                f"{source_name} -> {target_name} relation={profile.get('relation')}; basis={compact_text(basis, 300)}; relation_layer={layer}; confidence={profile.get('confidence')}.",
                "counter_relation",
                "relation/basis/confidence",
                layer,
                confidence=profile.get("confidence"),
                metadata=metadata,
            )
            self._candidate(claims, profile, f"{source_name} source type summary: {fmt_list(source.get('type_self'))}. {target_name} target type summary: {fmt_list(target.get('type_self'))}.", "counter_type_basis", "source.type_self/target.type_self", layer, confidence=profile.get("confidence"), metadata=metadata)
        return claims


class TechTreeAgent(BaseAgent):
    name = "TechTreeAgent"

    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        return self._run_rule_from_candidates(task, kb_store, query_plan)

    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        claims: list[CandidateClaim] = []
        for ref in task.profile_refs:
            profile = kb_store.get_profile(ref.profile_id)
            if not profile or profile.get("profile_type") != "entity_profile":
                continue
            name = (profile.get("identity") or {}).get("name") or profile.get("entity_id")
            for idx, cost in enumerate(profile.get("costs") or [], start=1):
                self._candidate(claims, profile, f"{name} cost/production record {idx}: mineral={cost.get('mineral')}; gas={cost.get('gas')}; supply={cost.get('supply')}; produce_time={cost.get('produce_time')}; production source={fmt_list(cost.get('produce_from') or cost.get('produce_from_entity_ids'))}.", "tech_cost", f"costs[{idx - 1}]", "processed")
            tech_tree = profile.get("tech_tree") or {}
            for direction, edges in [("incoming", tech_tree.get("incoming_edges") or []), ("outgoing", tech_tree.get("outgoing_edges") or [])]:
                for idx, edge in enumerate(edges[:8], start=1):
                    self._candidate(claims, profile, f"{name} tech-tree {direction} edge {idx}: relation={edge.get('relation')}; head={edge.get('head')}; tail={edge.get('tail')}; text={compact_text(edge.get('text'), 220)}.", "tech_tree_edge", f"tech_tree.{direction}_edges[{idx - 1}]", "processed", metadata={"relation": edge.get("relation")})
            for idx, upgrade in enumerate((profile.get("upgrades") or [])[:8], start=1):
                self._candidate(claims, profile, f"{name} related upgrade {idx}: {upgrade.get('upgrade_name') or upgrade.get('upgrade_id')}; text={compact_text(upgrade.get('text'), 220)}.", "tech_upgrade", f"upgrades[{idx - 1}]", "processed")
            for idx, action in enumerate((profile.get("action_conditions") or [])[:8], start=1):
                self._candidate(claims, profile, f"{name} related action condition {idx}: {action.get('action_name') or action.get('doc_id')}; text={compact_text(action.get('text') or action, 240)}.", "tech_action_condition", f"action_conditions[{idx - 1}]", "processed")
        return claims


class ScenarioRouterAgent(BaseAgent):
    name = "ScenarioRouterAgent"

    def _run_rule(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> AgentEvidence:
        return self._run_rule_from_candidates(task, kb_store, query_plan)

    def _build_candidate_claims(self, task: AgentTask, kb_store: KBStore, query_plan: QueryPlan) -> list[CandidateClaim]:
        claims: list[CandidateClaim] = []
        for ref in task.profile_refs:
            profile = kb_store.get_profile(ref.profile_id)
            if not profile or profile.get("profile_type") != "scenario_profile":
                continue
            tag = profile.get("scenario_tag") or ref.profile_id
            self._candidate(claims, profile, f"Scenario {tag} description: {compact_text(profile.get('description') or profile.get('text'), 320)}", "scenario_description", "description", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
            self._candidate(claims, profile, f"Scenario {tag} trigger roles: {fmt_list(profile.get('trigger_roles'))}; trigger effects: {fmt_list(profile.get('trigger_effects'))}.", "scenario_triggers", "trigger_roles/trigger_effects", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
            self._candidate(claims, profile, f"Scenario {tag} recommended knowledge sources: {fmt_list(profile.get('recommended_kbs'))}.", "scenario_recommended_kbs", "recommended_kbs", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
            entities = profile.get("matched_entities") or []
            abilities = profile.get("matched_abilities") or []
            relations = profile.get("matched_relations") or []
            if entities:
                names = [item.get("name") or item.get("entity_id") for item in entities[:10]]
                self._candidate(claims, profile, f"Scenario {tag} matched {len(entities)} entities; examples: {fmt_list(names, limit=8)}.", "scenario_matched_entities", "matched_entities", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
            if abilities:
                names = [item.get("ability_name") or item.get("ability_id") for item in abilities[:10]]
                self._candidate(claims, profile, f"Scenario {tag} matched {len(abilities)} abilities; examples: {fmt_list(names, limit=8)}.", "scenario_matched_abilities", "matched_abilities", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
            if relations:
                self._candidate(claims, profile, f"Scenario {tag} matched {len(relations)} relations; these can be relation clues for CounterAgent.", "scenario_matched_relations", "matched_relations", "enriched", confidence=profile.get("confidence"), metadata={"scenario_tag": tag})
        return claims


AGENT_REGISTRY = {
    UnitProfileAgent.name: UnitProfileAgent,
    AbilityAgent.name: AbilityAgent,
    CounterAgent.name: CounterAgent,
    TechTreeAgent.name: TechTreeAgent,
    ScenarioRouterAgent.name: ScenarioRouterAgent,
}

