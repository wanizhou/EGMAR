from __future__ import annotations

from collections import defaultdict
from typing import Any

from starcraft_rag.context import AgentTask, KnowledgeHit, ProfileRef, RAGContext, RetrievedDocument
from starcraft_rag.kb import KBStore
from starcraft_rag.retriever import as_list
from starcraft_rag.router import AGENT_NAMES


AGENT_PROFILE_TYPES = {
    "UnitProfileAgent": {"entity_profile"},
    "TechTreeAgent": {"entity_profile"},
    "AbilityAgent": {"ability_profile"},
    "CounterAgent": {"relation_profile"},
    "ScenarioRouterAgent": {"scenario_profile"},
}

SCENARIO_INTENTS = {
    "anti_cloak_response",
    "air_control",
    "frontal_combat",
    "harass",
    "scenario_lookup",
}


class KnowledgeResolver:
    """集中处理 rag_documents 到 profiles 的回连。

    之前这部分逻辑分散在 Dispatcher 和 Agent 中，导致 doc_id、entity_id、
    ability_id、relation_id、scenario_tag 反复传递。现在统一解析为
    KnowledgeHit.profile_refs，后续模块只消费这个统一结果。
    """

    def __init__(self, kb_store: KBStore) -> None:
        self.kb_store = kb_store

    def resolve(self, documents: list[RetrievedDocument]) -> list[KnowledgeHit]:
        hits: list[KnowledgeHit] = []
        for index, item in enumerate(documents, start=1):
            doc = item.document
            hints = doc.get("retrieval_hints") or {}
            refs = self._profile_refs_from_doc(doc)
            hits.append(
                KnowledgeHit(
                    hit_id=f"hit_{index:03d}",
                    doc_id=item.doc_id,
                    score=item.score,
                    doc_type=doc.get("doc_type", ""),
                    primary_agent=hints.get("primary_agent", ""),
                    secondary_agents=[a for a in as_list(hints.get("secondary_agents")) if a],
                    source_profile_id=doc.get("source_profile_id", ""),
                    source_profile_type=doc.get("source_profile_type", ""),
                    profile_refs=refs,
                    reasons=item.reasons,
                )
            )
        return hits

    def _profile_refs_from_doc(self, doc: dict[str, Any]) -> list[ProfileRef]:
        refs: list[ProfileRef] = []

        def add(profile_id: str | None, profile_type: str, matched_by: str) -> None:
            if not profile_id:
                return
            key = (profile_id, profile_type)
            if any((ref.profile_id, ref.profile_type) == key for ref in refs):
                return
            refs.append(ProfileRef(profile_id=profile_id, profile_type=profile_type, matched_by=matched_by))

        source_profile_id = doc.get("source_profile_id")
        source_profile_type = doc.get("source_profile_type")
        if source_profile_id and source_profile_type:
            add(source_profile_id, source_profile_type, "source_profile_id")

        # 场景类文档是“路由/候选清单”，其中可能包含几十个实体、技能和关系。
        # 如果把这些候选项全部展开给 Unit/Ability/Counter Agent，会淹没真正由检索命中的精确文档。
        # 因此这里仅保留场景 profile 本身，让 ScenarioRouterAgent 解释场景，再由其他精确 doc 驱动具体 Agent。
        if doc.get("doc_type") in {"scenario_router", "scenario_candidates"}:
            return refs

        for entity_id in as_list(doc.get("entity_ids"))[:8]:
            add(self.kb_store.get_profile_id_for_entity(entity_id), "entity_profile", f"entity_id:{entity_id}")
        for ability_id in as_list(doc.get("ability_ids"))[:8]:
            add(self.kb_store.get_profile_id_for_ability(ability_id), "ability_profile", f"ability_id:{ability_id}")
        for relation_id in as_list(doc.get("relation_ids"))[:8]:
            add(self.kb_store.get_profile_id_for_relation(relation_id), "relation_profile", f"relation_id:{relation_id}")
        for scenario_tag in as_list(doc.get("scenario_tags"))[:8]:
            add(self.kb_store.get_profile_id_for_scenario(scenario_tag), "scenario_profile", f"scenario_tag:{scenario_tag}")

        return refs


class AgentPlanner:
    """根据 KnowledgeHit 中的 Agent 提示和 ProfileRef 生成 AgentTask。"""

    def __init__(self, kb_store: KBStore, max_profiles_per_agent: int = 6) -> None:
        self.kb_store = kb_store
        self.max_profiles_per_agent = max_profiles_per_agent

    def plan(self, ctx: RAGContext) -> list[AgentTask]:
        if not ctx.plan:
            return []

        refs_by_agent: dict[str, list[ProfileRef]] = defaultdict(list)
        hits_by_agent: dict[str, list[str]] = defaultdict(list)
        hit_scores_by_agent: dict[str, dict[str, float]] = defaultdict(dict)
        doc_types_by_agent: dict[str, list[str]] = defaultdict(list)
        profile_support_by_agent: dict[str, dict[str, float]] = defaultdict(dict)
        matched_by_agent: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

        plan_agents = set(ctx.plan.candidate_agents)
        scenario_explicit = bool(ctx.plan.scenario_tags) or any(intent in SCENARIO_INTENTS for intent in ctx.plan.intent_candidates)

        for hit in ctx.knowledge_hits:
            agents = self._agents_for_hit(hit, plan_agents, scenario_explicit)
            for agent in agents:
                if agent not in AGENT_NAMES:
                    continue
                allowed_types = AGENT_PROFILE_TYPES.get(agent, set())
                for ref in hit.profile_refs:
                    if ref.profile_type not in allowed_types:
                        continue
                    if ref.profile_id not in [existing.profile_id for existing in refs_by_agent[agent]]:
                        refs_by_agent[agent].append(ref)
                    profile_support_by_agent[agent][ref.profile_id] = max(
                        profile_support_by_agent[agent].get(ref.profile_id, 0.0),
                        hit.score,
                    )
                    if ref.matched_by not in matched_by_agent[agent][ref.profile_id]:
                        matched_by_agent[agent][ref.profile_id].append(ref.matched_by)
                if hit.hit_id not in hits_by_agent[agent]:
                    hits_by_agent[agent].append(hit.hit_id)
                hit_scores_by_agent[agent][hit.hit_id] = hit.score
                if hit.doc_type and hit.doc_type not in doc_types_by_agent[agent]:
                    doc_types_by_agent[agent].append(hit.doc_type)

        # A retrieved scenario document may introduce many unrelated profiles,
        # but an entity/ability explicitly resolved from the query is a hard
        # anchor.  Ensure its own profile reaches the responsible Agent so a
        # multi-part question cannot lose "Reaper production" to an unrelated
        # Mothership profile merely because of ranking noise.
        def ensure_ref(agent: str, profile_id: str, profile_type: str, matched_by: str) -> None:
            if not profile_id or agent not in plan_agents:
                return
            if profile_id not in [ref.profile_id for ref in refs_by_agent[agent]]:
                refs_by_agent[agent].append(ProfileRef(profile_id=profile_id, profile_type=profile_type, matched_by=matched_by))
            profile_support_by_agent[agent][profile_id] = max(profile_support_by_agent[agent].get(profile_id, 0.0), 1.0)
            matched_by_agent[agent][profile_id].append(matched_by)

        for entity_id in ctx.plan.entities:
            profile_id = self.kb_store.get_profile_id_for_entity(entity_id)
            ensure_ref("UnitProfileAgent", profile_id, "entity_profile", f"query_entity:{entity_id}")
            ensure_ref("TechTreeAgent", profile_id, "entity_profile", f"query_entity:{entity_id}")
        for ability_id in ctx.plan.abilities:
            profile_id = self.kb_store.get_profile_id_for_ability(ability_id)
            ensure_ref("AbilityAgent", profile_id, "ability_profile", f"query_ability:{ability_id}")

        tasks: list[AgentTask] = []
        for agent, refs in refs_by_agent.items():
            if not refs:
                continue
            ranked_refs = sorted(refs, key=lambda ref: profile_support_by_agent[agent].get(ref.profile_id, 0.0), reverse=True)
            ranked_hit_ids = sorted(hits_by_agent[agent], key=lambda hit_id: hit_scores_by_agent[agent].get(hit_id, 0.0), reverse=True)
            tasks.append(
                AgentTask(
                    agent_name=agent,
                    profile_refs=ranked_refs[: self.max_profiles_per_agent],
                    hit_ids=ranked_hit_ids[: self.max_profiles_per_agent],
                    metadata={
                        "planner": "KnowledgeHit",
                        "doc_types": doc_types_by_agent[agent],
                        "hit_scores": hit_scores_by_agent[agent],
                        "profile_support_scores": profile_support_by_agent[agent],
                        "profile_matched_by": dict(matched_by_agent[agent]),
                        "max_profiles_per_agent": self.max_profiles_per_agent,
                        "answer_requirements": list(ctx.plan.answer_requirements),
                    },
                )
            )
        return tasks

    def _agents_for_hit(self, hit: KnowledgeHit, plan_agents: set[str], scenario_explicit: bool) -> list[str]:
        # primary_agent 是 rag_document 的主职责；secondary_agents 只在 Router 也认为相关时才激活。
        # 这里刻意不再把 plan.candidate_agents 追加到每个 hit，避免一个 scenario doc 扩散出 4-5 个 Agent。
        agents: list[str] = []
        if hit.primary_agent == "ScenarioRouterAgent" and hit.doc_type in {"scenario_router", "scenario_candidates"}:
            if scenario_explicit:
                agents.append(hit.primary_agent)
        elif hit.primary_agent:
            agents.append(hit.primary_agent)

        for agent in hit.secondary_agents:
            if agent in plan_agents:
                agents.append(agent)

        return list(dict.fromkeys(agent for agent in agents if agent in AGENT_NAMES))
