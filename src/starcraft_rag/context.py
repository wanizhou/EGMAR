from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class QueryPlan:
    """Router 输出的弱结构化计划。

    entities、abilities、scenario_tags 都允许为空；它们只是检索加权信号，
    不是系统继续运行的前置条件。
    """

    raw_query: str
    intent_candidates: list[str] = field(default_factory=list)
    candidate_agents: list[str] = field(default_factory=list)
    candidate_doc_types: list[str] = field(default_factory=list)
    query_terms: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    abilities: list[str] = field(default_factory=list)
    scenario_tags: list[str] = field(default_factory=list)
    # Questions can require more than one independent fact.  These short
    # natural-language slots are diagnostic requirements, never gold answers.
    answer_requirements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedDocument:
    doc_id: str
    score: float
    document: dict[str, Any]
    reasons: list[str] = field(default_factory=list)


@dataclass
class ProfileRef:
    profile_id: str
    profile_type: str
    matched_by: str


@dataclass
class KnowledgeHit:
    """rag_documents 命中结果解析后的统一对象。

    这个对象把 doc_id、Agent 路由提示和 profile 引用集中在一起，
    避免各模块反复手写 entity_id/ability_id/relation_id 到 profile_id 的映射。
    """

    hit_id: str
    doc_id: str
    score: float
    doc_type: str
    primary_agent: str
    secondary_agents: list[str]
    source_profile_id: str
    source_profile_type: str
    profile_refs: list[ProfileRef] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


@dataclass
class AgentTask:
    agent_name: str
    profile_refs: list[ProfileRef] = field(default_factory=list)
    hit_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def profile_ids(self) -> list[str]:
        return [ref.profile_id for ref in self.profile_refs]


@dataclass
class EvidenceClaim:
    claim: str
    evidence_type: str
    source_profile_id: str
    source_field: str
    confidence: float | None = None
    source_layer: str | None = None
    score: float = 0.0
    rank: int = 0
    matched_terms: list[str] = field(default_factory=list)
    reason: str = ""
    supporting_profile_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentEvidence:
    agent: str
    summary: str = ""
    claims: list[EvidenceClaim] = field(default_factory=list)
    used_profiles: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGContext:
    """贯穿一次查询的调试对象。

    调试时只盯着 ctx，看它从 query 逐步增加 plan、documents、hits、
    tasks、agent_results 和 answer。
    """

    query: str
    plan: QueryPlan | None = None
    documents: list[RetrievedDocument] = field(default_factory=list)
    knowledge_hits: list[KnowledgeHit] = field(default_factory=list)
    agent_tasks: list[AgentTask] = field(default_factory=list)
    agent_results: list[AgentEvidence] = field(default_factory=list)
    answer: str = ""
    used_profiles: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    synthesis_output: dict[str, Any] = field(default_factory=dict)
    synthesis_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

