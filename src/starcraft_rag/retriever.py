from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import numpy as np

from starcraft_rag.context import QueryPlan, RetrievedDocument
from starcraft_rag.kb import KBStore, normalize_key


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def min_max_normalize(scores: np.ndarray) -> np.ndarray:
    # dense、sparse、metadata 三类分数的原始尺度不同，必须先压到 0~1 再融合。
    if scores.size == 0:
        return scores.astype(np.float32)
    min_score = float(np.min(scores))
    max_score = float(np.max(scores))
    if abs(max_score - min_score) < 1e-12:
        return np.ones_like(scores, dtype=np.float32)
    return ((scores - min_score) / (max_score - min_score)).astype(np.float32)


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query_plan: QueryPlan, top_k: int = 8) -> list[RetrievedDocument]:
        raise NotImplementedError


class MetadataKeywordRetriever(BaseRetriever):
    """第一版检索器：关键词匹配 + rag_documents metadata 加权。"""

    def __init__(self, kb_store: KBStore) -> None:
        self.kb_store = kb_store

    def retrieve(self, query_plan: QueryPlan, top_k: int = 8) -> list[RetrievedDocument]:
        scored: list[RetrievedDocument] = []
        fallback: list[RetrievedDocument] = []
        for doc in self.kb_store.rag_documents:
            score, reasons, strong_match = self._score_doc(doc, query_plan)
            if score <= 0:
                continue
            item = RetrievedDocument(doc_id=doc.get("doc_id", ""), score=round(score, 4), document=doc, reasons=reasons)
            if strong_match:
                scored.append(item)
            else:
                fallback.append(item)
        selected = scored if scored else fallback
        selected.sort(key=lambda item: item.score, reverse=True)
        return selected[:top_k]

    def _score_doc(self, doc: dict[str, Any], query_plan: QueryPlan) -> tuple[float, list[str], bool]:
        # 这里不是向量检索，而是“结构化线索加分”：
        # Router 已经给出了候选 doc_type、Agent、实体/技能/场景标签，
        # 这些信号如果和 rag_document 的 metadata 对上，就给文档额外加分。
        score = 0.0
        reasons: list[str] = []
        strong_match = False
        hints = doc.get("retrieval_hints") or {}

        if doc.get("doc_type") in query_plan.candidate_doc_types:
            score += 2.0
            reasons.append(f"doc_type={doc.get('doc_type')}")
        if hints.get("primary_agent") in query_plan.candidate_agents:
            score += 1.5
            reasons.append(f"primary_agent={hints.get('primary_agent')}")
        matched_secondary = [a for a in as_list(hints.get("secondary_agents")) if a in query_plan.candidate_agents]
        if matched_secondary:
            score += 0.8
            reasons.append("secondary_agent=" + ",".join(matched_secondary))

        entity_ids = set(as_list(doc.get("entity_ids")))
        ability_ids = set(as_list(doc.get("ability_ids")))
        scenario_tags = set(as_list(doc.get("scenario_tags")))

        for entity_id in query_plan.entities:
            if entity_id in entity_ids:
                score += 8.0
                strong_match = True
                reasons.append(f"entity_id={entity_id}")
        for ability_id in query_plan.abilities:
            if ability_id in ability_ids:
                score += 8.0
                strong_match = True
                reasons.append(f"ability_id={ability_id}")
        for tag in query_plan.scenario_tags:
            if tag in scenario_tags:
                score += 7.0
                strong_match = True
                reasons.append(f"scenario_tag={tag}")

        haystack = self._build_haystack(doc, include_text=True)
        keyword_haystack = self._build_haystack(doc, include_text=False)
        for term in query_plan.query_terms:
            term_key = normalize_key(term)
            if not term_key:
                continue
            if term_key in keyword_haystack:
                score += 2.5
                strong_match = True
                reasons.append(f"keyword={term}")
            elif term_key in haystack:
                score += 1.2
                strong_match = True
                reasons.append(f"text={term}")

        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]+", query_plan.raw_query):
            token_key = normalize_key(token)
            if len(token_key) >= 3 and token_key in haystack:
                score += 0.6
                strong_match = True
        return score, reasons[:12], strong_match

    def _build_haystack(self, doc: dict[str, Any], include_text: bool) -> str:
        values: list[Any] = [
            doc.get("doc_id"),
            doc.get("doc_type"),
            doc.get("source_profile_id"),
            doc.get("source_profile_type"),
            doc.get("race"),
        ]
        values.extend(as_list(doc.get("keywords")))
        values.extend(as_list(doc.get("names")))
        values.extend(as_list(doc.get("entity_ids")))
        values.extend(as_list(doc.get("ability_ids")))
        values.extend(as_list(doc.get("relation_ids")))
        values.extend(as_list(doc.get("scenario_tags")))
        if include_text:
            values.append(doc.get("text"))
        return normalize_key(" ".join(str(value) for value in values if value is not None))


class HybridRetriever(MetadataKeywordRetriever):
    """BGE-M3 检索器：dense、sparse、hybrid 三种模式可切换，默认 hybrid。"""

    VALID_SCORE_MODES = {"dense", "sparse", "hybrid"}

    def __init__(
        self,
        kb_store: KBStore,
        model_path: str | Path | None = None,
        score_mode: str = "hybrid",
        index_dir: str | Path | None = None,
        batch_size: int = 16,
        max_length: int = 512,
        dense_weight: float = 0.65,
        sparse_weight: float = 0.35,
        metadata_weight: float = 0.18,
        candidate_pool_size: int = 80,
        use_fp16: bool = True,
        rebuild_index: bool = False,
    ) -> None:
        super().__init__(kb_store)
        mode = score_mode.lower()
        if mode not in self.VALID_SCORE_MODES:
            raise ValueError(f"Unknown BGE-M3 retrieval mode: {score_mode}; allowed values: dense/sparse/hybrid")
        if dense_weight < 0 or sparse_weight < 0 or metadata_weight < 0:
            raise ValueError("dense_weight, sparse_weight, and metadata_weight must be non-negative")

        package_dir = Path(__file__).resolve().parent
        self.model_path = Path(model_path) if model_path else package_dir / "LLM" / "bge-m3"
        self.score_mode = mode
        self.batch_size = batch_size
        self.max_length = max_length
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.metadata_weight = metadata_weight
        self.candidate_pool_size = max(candidate_pool_size, 1)
        self.use_fp16 = use_fp16
        self.index_dir = Path(index_dir) if index_dir else self.kb_store.runtime_kb_dir / "vector_index" / "bge_m3"
        self.model: Any | None = None
        self.doc_texts = [self._build_document_text(doc) for doc in self.kb_store.rag_documents]
        self.doc_ids = [doc.get("doc_id", "") for doc in self.kb_store.rag_documents]
        self.dense_vectors: np.ndarray | None = None
        self.lexical_weights: list[dict[str, float]] = []

        self._load_or_build_index(rebuild_index=rebuild_index)

    def retrieve(self, query_plan: QueryPlan, top_k: int = 8) -> list[RetrievedDocument]:
        if not self.kb_store.rag_documents:
            return []

        # 1. 把 Router 输出的 QueryPlan 拼成 BGE-M3 能理解的查询文本。
        # raw_query 保留用户原话；query_terms/entities/abilities/scenario_tags 提供标准化领域线索。
        query_text = self._build_query_text(query_plan)
        query_dense, query_sparse = self._encode_query(query_text)

        # 2. 分别计算 dense 语义相似度、sparse 词项匹配分、metadata 结构化加权分。
        # dense 负责“意思像不像”，sparse 负责“专有名词是否对上”，metadata 负责“是否命中 KB 中的明确 id/标签”。
        dense_scores = self._dense_scores(query_dense)
        sparse_scores = self._sparse_scores(query_sparse)
        metadata_scores, metadata_reasons, metadata_strong = self._metadata_scores(query_plan)

        # 3. 先融合向量分数，再叠加少量 metadata 分数，既保留语义召回，也不丢精确命中。
        vector_scores = self._combine_vector_scores(dense_scores, sparse_scores)
        final_scores = vector_scores + self.metadata_weight * min_max_normalize(metadata_scores)

        # 4. 先取一个较大的候选池，再做多样性筛选和关键 doc_type 入口保护。
        candidate_count = min(len(final_scores), max(top_k * 6, self.candidate_pool_size))
        candidate_indexes = np.argsort(-final_scores)[:candidate_count]
        selected_indexes = self._select_diverse_indexes(candidate_indexes, final_scores, query_plan, top_k)

        # 5. 输出 RetrievedDocument。reasons 是调试用，能看到每条文档为什么被召回。
        results: list[RetrievedDocument] = []
        dense_norm = min_max_normalize(dense_scores)
        sparse_norm = min_max_normalize(sparse_scores)
        for index in selected_indexes:
            doc = self.kb_store.rag_documents[int(index)]
            reasons = [
                f"bge_mode={self.score_mode}",
                f"dense={dense_scores[index]:.4f}",
                f"sparse={sparse_scores[index]:.4f}",
            ]
            if self.score_mode == "hybrid":
                reasons.append(f"dense_norm={dense_norm[index]:.4f}")
                reasons.append(f"sparse_norm={sparse_norm[index]:.4f}")
            reasons.extend(metadata_reasons[int(index)])
            if metadata_strong[int(index)]:
                reasons.append("metadata_strong=true")
            results.append(
                RetrievedDocument(
                    doc_id=doc.get("doc_id", ""),
                    score=round(float(final_scores[index]), 4),
                    document=doc,
                    reasons=reasons[:14],
                )
            )
        return results

    def _load_model(self) -> Any:
        if self.model is not None:
            return self.model
        try:
            from FlagEmbedding import BGEM3FlagModel
        except ImportError as exc:
            raise RuntimeError(
                "FlagEmbedding is missing. Run in the starcraft-rag-llm environment or install FlagEmbedding and torch."
            ) from exc
        if not self.model_path.exists():
            raise RuntimeError(f"BGE-M3 model directory does not exist: {self.model_path}")
        self.model = BGEM3FlagModel(str(self.model_path), use_fp16=self.use_fp16)
        return self.model

    def _load_or_build_index(self, rebuild_index: bool) -> None:
        # 索引缓存由四个文件组成：
        # dense_vectors.npy 保存 dense 向量；lexical_weights.jsonl 保存 sparse 词权重；
        # doc_ids.json 和 manifest.json 用来判断缓存是否还对应当前 rag_documents。
        self.index_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.index_dir / "manifest.json"
        dense_path = self.index_dir / "dense_vectors.npy"
        sparse_path = self.index_dir / "lexical_weights.jsonl"
        doc_ids_path = self.index_dir / "doc_ids.json"

        expected_manifest = self._build_manifest()
        cache_ready = (
            not rebuild_index
            and manifest_path.exists()
            and dense_path.exists()
            and sparse_path.exists()
            and doc_ids_path.exists()
        )
        if cache_ready:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                cached_doc_ids = json.loads(doc_ids_path.read_text(encoding="utf-8"))
                # manifest 完全一致才复用缓存；只要文档文本、模型路径或 max_length 变了，就重建。
                if manifest == expected_manifest and cached_doc_ids == self.doc_ids:
                    self.dense_vectors = np.load(dense_path).astype(np.float32)
                    self.lexical_weights = self._read_sparse_jsonl(sparse_path)
                    if len(self.lexical_weights) == len(self.doc_texts):
                        return
            except Exception:
                pass

        self._build_index()
        np.save(dense_path, self.dense_vectors)
        self._write_sparse_jsonl(sparse_path, self.lexical_weights)
        doc_ids_path.write_text(json.dumps(self.doc_ids, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest_path.write_text(json.dumps(expected_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_index(self) -> None:
        model = self._load_model()
        # 一次性编码所有 rag_documents；当前只有几千条，构建一次缓存后，后续查询只需要编码 query。
        # return_dense=True 得到语义向量；return_sparse=True 得到 BGE-M3 的词项权重。
        output = model.encode(
            self.doc_texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        self.dense_vectors = np.asarray(output["dense_vecs"], dtype=np.float32)
        self.lexical_weights = [self._normalize_sparse_weights(item) for item in output["lexical_weights"]]

    def _encode_query(self, query_text: str) -> tuple[np.ndarray, dict[str, float]]:
        # 每次查询只编码一条 query。这里同时拿 dense 和 sparse，后面按 score_mode 决定怎么使用。
        model = self._load_model()
        output = model.encode(
            [query_text],
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        dense = np.asarray(output["dense_vecs"][0], dtype=np.float32)
        sparse = self._normalize_sparse_weights(output["lexical_weights"][0])
        return dense, sparse

    def _dense_scores(self, query_dense: np.ndarray) -> np.ndarray:
        if self.dense_vectors is None:
            raise RuntimeError("BGE-M3 dense index has not been initialized")
        # BGE-M3 默认会归一化 dense 向量，因此点积可以作为 cosine similarity 使用。
        return np.matmul(self.dense_vectors, query_dense).astype(np.float32)

    def _sparse_scores(self, query_sparse: dict[str, float]) -> np.ndarray:
        model = self._load_model()
        # sparse 分数由 BGE-M3 根据 query/doc 的 lexical_weights 计算，更偏向专有词和短语匹配。
        scores = [
            float(model.compute_lexical_matching_score(query_sparse, doc_sparse))
            for doc_sparse in self.lexical_weights
        ]
        return np.asarray(scores, dtype=np.float32)

    def _combine_vector_scores(self, dense_scores: np.ndarray, sparse_scores: np.ndarray) -> np.ndarray:
        # score_mode 控制只用 dense、只用 sparse，还是二者归一化后按权重融合。
        if self.score_mode == "dense":
            return min_max_normalize(dense_scores)
        if self.score_mode == "sparse":
            return min_max_normalize(sparse_scores)
        dense_norm = min_max_normalize(dense_scores)
        sparse_norm = min_max_normalize(sparse_scores)
        total = self.dense_weight + self.sparse_weight
        if total <= 0:
            return np.zeros_like(dense_norm)
        return (self.dense_weight * dense_norm + self.sparse_weight * sparse_norm) / total

    def _metadata_scores(self, query_plan: QueryPlan) -> tuple[np.ndarray, list[list[str]], list[bool]]:
        # 复用关键词检索器的打分逻辑，把 Router 给出的结构化线索变成额外排序信号。
        # 这一步的结果不会单独决定排名，而是作为 final_scores 的一部分参与融合。
        scores: list[float] = []
        reasons: list[list[str]] = []
        strong: list[bool] = []
        for doc in self.kb_store.rag_documents:
            score, doc_reasons, strong_match = self._score_doc(doc, query_plan)
            scores.append(score)
            reasons.append(doc_reasons)
            strong.append(strong_match)
        return np.asarray(scores, dtype=np.float32), reasons, strong

    def _select_diverse_indexes(
        self,
        candidate_indexes: np.ndarray,
        final_scores: np.ndarray,
        query_plan: QueryPlan,
        top_k: int,
    ) -> list[int]:
        selected: list[int] = []
        profile_counts: dict[str, int] = {}
        relation_limit = top_k if "relation_counter" in query_plan.candidate_doc_types else max(2, top_k // 3)
        relation_count = 0

        # 第一轮先按融合分数取高分文档，同时限制同一 profile 和 relation_counter 的数量。
        # 这样可以避免一个单位的多条派生文档，或大量克制关系文档，把结果列表挤满。
        for raw_index in candidate_indexes:
            index = int(raw_index)
            doc = self.kb_store.rag_documents[index]
            doc_type = doc.get("doc_type", "")
            profile_id = doc.get("source_profile_id", "")
            if doc_type == "relation_counter" and relation_count >= relation_limit:
                continue
            if profile_id and profile_counts.get(profile_id, 0) >= 2:
                continue
            selected.append(index)
            profile_counts[profile_id] = profile_counts.get(profile_id, 0) + 1
            if doc_type == "relation_counter":
                relation_count += 1
            if len(selected) >= top_k:
                break

        # 如果多样性限制导致数量不足，再直接从候选池里补齐。
        for raw_index in candidate_indexes:
            index = int(raw_index)
            if index not in selected:
                selected.append(index)
            if len(selected) >= top_k:
                break
        selected = self._add_required_doc_types(selected, final_scores, query_plan, top_k)
        selected.sort(key=lambda idx: float(final_scores[idx]), reverse=True)
        return selected[:top_k]

    def _add_required_doc_types(
        self,
        selected: list[int],
        final_scores: np.ndarray,
        query_plan: QueryPlan,
        top_k: int,
    ) -> list[int]:
        protected: set[int] = set()

        # BGE-M3 的语义分数很强，但偶尔会把结构化入口挤到 top_k 外。
        # 这里按 Router/Agent 结果补入关键 doc_type，例如技能问题优先保留 ability_effect。
        for doc_type in self._required_doc_types(query_plan):
            if any(self.kb_store.rag_documents[index].get("doc_type") == doc_type for index in selected):
                continue

            selected_set = set(selected)
            candidates = [
                index
                for index, doc in enumerate(self.kb_store.rag_documents)
                if index not in selected_set and doc.get("doc_type") == doc_type
            ]
            if not candidates:
                continue
            best_index = max(candidates, key=lambda index: float(final_scores[index]))
            selected.append(best_index)
            protected.add(best_index)

        # 补入关键入口后，如果超出 top_k，只移除未受保护的最低分文档。
        while len(selected) > top_k:
            removable = [index for index in selected if index not in protected]
            if not removable:
                break
            remove_index = min(removable, key=lambda index: float(final_scores[index]))
            selected.remove(remove_index)
        return selected

    def _required_doc_types(self, query_plan: QueryPlan) -> list[str]:
        # 根据将要调用的 Agent，推断“必须尽量保留”的检索入口类型。
        # 例如 AbilityAgent 需要 ability_effect；TechTreeAgent 需要 entity_cost_tech。
        required: list[str] = []

        def add(doc_type: str) -> None:
            if doc_type in query_plan.candidate_doc_types and doc_type not in required:
                required.append(doc_type)

        for doc_type in query_plan.candidate_doc_types[:2]:
            add(doc_type)
        if "AbilityAgent" in query_plan.candidate_agents:
            add("ability_effect")
        if query_plan.entities or "UnitProfileAgent" in query_plan.candidate_agents:
            add("entity_overview")
            add("entity_combat")
        if "TechTreeAgent" in query_plan.candidate_agents:
            add("entity_cost_tech")
        if query_plan.scenario_tags:
            add("scenario_router")
            add("scenario_candidates")
        if "CounterAgent" in query_plan.candidate_agents:
            add("relation_counter")
        return required[:5]

    def _build_document_text(self, doc: dict[str, Any]) -> str:
        # rag_document 的 metadata 和正文都放进编码文本：
        # metadata 有利于命中 id/name/tag，正文 text 有利于语义匹配。
        values: list[Any] = [
            doc.get("doc_id"),
            doc.get("doc_type"),
            doc.get("source_profile_id"),
            doc.get("source_profile_type"),
            doc.get("race"),
            doc.get("confidence"),
        ]
        values.extend(as_list(doc.get("names")))
        values.extend(as_list(doc.get("keywords")))
        values.extend(as_list(doc.get("entity_ids")))
        values.extend(as_list(doc.get("ability_ids")))
        values.extend(as_list(doc.get("relation_ids")))
        values.extend(as_list(doc.get("scenario_tags")))
        hints = doc.get("retrieval_hints") or {}
        values.append(hints.get("primary_agent"))
        values.extend(as_list(hints.get("secondary_agents")))
        values.append(doc.get("text"))
        return "\n".join(str(value) for value in values if value not in (None, ""))

    def _build_query_text(self, query_plan: QueryPlan) -> str:
        # 查询文本不只包含用户原话，还包含 Router 扩展出的领域线索。
        # 这样问题即使没有直接写出完整技能 ID，也能通过 query_terms 命中相关文档。
        values: list[Any] = [
            query_plan.raw_query,
            *query_plan.intent_candidates,
            *query_plan.candidate_agents,
            *query_plan.candidate_doc_types,
            *query_plan.query_terms,
            *query_plan.entities,
            *query_plan.abilities,
            *query_plan.scenario_tags,
        ]
        # Router 已经把自然语言映射到稳定 id/标签，这里一起送入 BGE-M3。
        return "\n".join(str(value) for value in values if value not in (None, ""))

    def _build_manifest(self) -> dict[str, Any]:
        # 用文档文本摘要判断缓存是否过期；只要 rag_documents 内容变了，digest 就会变化。
        digest = hashlib.sha256()
        for doc_id, text in zip(self.doc_ids, self.doc_texts):
            digest.update(doc_id.encode("utf-8", errors="ignore"))
            digest.update(b"\0")
            digest.update(text.encode("utf-8", errors="ignore"))
            digest.update(b"\0")
        return {
            "index_type": "bge_m3_dense_sparse_v1",
            "model_path": str(self.model_path.resolve()),
            "doc_count": len(self.doc_texts),
            "max_length": self.max_length,
            "doc_digest": digest.hexdigest(),
        }

    @staticmethod
    def _read_sparse_jsonl(path: Path) -> list[dict[str, float]]:
        rows: list[dict[str, float]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append({str(k): float(v) for k, v in json.loads(line).items()})
        return rows

    @staticmethod
    def _write_sparse_jsonl(path: Path, rows: list[dict[str, float]]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                cleaned = {str(k): float(v) for k, v in row.items()}
                f.write(json.dumps(cleaned, ensure_ascii=False, separators=(",", ":")) + "\n")

    @staticmethod
    def _normalize_sparse_weights(row: dict[Any, Any]) -> dict[str, float]:
        return {str(k): float(v) for k, v in row.items()}
