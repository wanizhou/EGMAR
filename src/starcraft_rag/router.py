from __future__ import annotations

import json
import re
from dataclasses import asdict
from typing import Any

from starcraft_rag.context import QueryPlan
from starcraft_rag.domain_alias import DomainAliasResolver
from starcraft_rag.kb import KBStore
from starcraft_rag.llm import BaseLLMProvider, ROUTER_FEW_SHOT_EXAMPLES, ROUTER_SYSTEM_PROMPT


AGENT_NAMES = {
    "UnitProfileAgent",
    "AbilityAgent",
    "CounterAgent",
    "TechTreeAgent",
    "ScenarioRouterAgent",
}

DOC_TYPE_TO_PRIMARY_AGENT = {
    "entity_overview": "UnitProfileAgent",
    "entity_combat": "UnitProfileAgent",
    "entity_cost_tech": "TechTreeAgent",
    "entity_abilities": "AbilityAgent",
    "entity_tactical": "UnitProfileAgent",
    "ability_effect": "AbilityAgent",
    "ability_usage": "AbilityAgent",
    "relation_counter": "CounterAgent",
    "scenario_router": "ScenarioRouterAgent",
    "scenario_candidates": "ScenarioRouterAgent",
}

DEFAULT_AGENTS = list(AGENT_NAMES)
DEFAULT_DOC_TYPES = list(DOC_TYPE_TO_PRIMARY_AGENT)


ROUTING_RULES = [
    {
        "intent": "anti_cloak_response",
        "keywords": ["anti cloak", "anti-cloak", "cloak", "cloaked", "burrowed", "stealth", "invisible", "detect", "detector", "reveal", "scan", "scanner sweep"],
        "agents": ["ScenarioRouterAgent", "AbilityAgent", "CounterAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "ability_effect", "ability_usage", "relation_counter"],
        "terms": ["anti_cloak_response", "anti_cloak", "reveal", "detector", "counters_stealth", "Scanner Sweep"],
        "scenario_tags": ["anti_cloak_response"],
    },
    {
        "intent": "air_control",
        "keywords": ["air", "anti air", "anti-air", "air unit", "air army", "flying", "can attack air"],
        "agents": ["ScenarioRouterAgent", "UnitProfileAgent", "CounterAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "entity_combat", "relation_counter"],
        "terms": ["air_control", "anti_air", "air_unit", "can_attack_air"],
        "scenario_tags": ["air_control"],
    },
    {
        "intent": "counter_relation",
        "keywords": ["counter", "countered by", "strong against", "weak against", "deal with", "handle", "facing", "advantage", "threat"],
        "agents": ["CounterAgent", "UnitProfileAgent", "ScenarioRouterAgent"],
        "doc_types": ["relation_counter", "entity_combat", "entity_tactical", "scenario_candidates"],
        "terms": ["counter", "strong_against", "potentially_strong_against", "type_anti"],
        "scenario_tags": [],
    },
    {
        "intent": "tech_tree",
        "keywords": ["research", "build", "produce", "cost", "prerequisite", "require", "requires", "tech", "technology", "upgrade", "from where"],
        "agents": ["TechTreeAgent", "UnitProfileAgent", "ScenarioRouterAgent"],
        "doc_types": ["entity_cost_tech", "entity_overview", "scenario_router", "scenario_candidates"],
        "terms": ["cost", "produce_from", "requires_building", "requires_unit", "upgrade", "tech_planning"],
        "scenario_tags": ["tech_planning"],
    },
    {
        "intent": "ability_effect",
        "keywords": ["ability", "spell", "effect", "aoe", "area", "control", "slow", "damage", "reveal", "teleport", "transport"],
        "agents": ["AbilityAgent", "UnitProfileAgent", "ScenarioRouterAgent"],
        "doc_types": ["ability_effect", "ability_usage", "entity_abilities"],
        "terms": ["ability_effect", "ability_usage", "aoe", "control", "damage", "slow", "teleport"],
        "scenario_tags": [],
    },
    {
        "intent": "unit_profile",
        "keywords": ["unit", "building", "attribute", "health", "armor", "range", "speed", "can", "role", "profile"],
        "agents": ["UnitProfileAgent"],
        "doc_types": ["entity_overview", "entity_combat", "entity_tactical"],
        "terms": ["entity_overview", "combat_roles", "target", "survival", "weapons"],
        "scenario_tags": [],
    },
    {
        "intent": "frontal_combat",
        "keywords": ["frontal", "combat", "fight", "army fight", "main army", "firepower"],
        "agents": ["ScenarioRouterAgent", "UnitProfileAgent", "CounterAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "entity_combat", "relation_counter"],
        "terms": ["frontal_combat", "durable", "aoe_damage", "long_range"],
        "scenario_tags": ["frontal_combat"],
    },
    {
        "intent": "harass",
        "keywords": ["harass", "harassment", "mobility", "multi-line", "worker harass", "mineral line"],
        "agents": ["ScenarioRouterAgent", "UnitProfileAgent", "AbilityAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "entity_tactical", "ability_usage"],
        "terms": ["worker_harass", "multi_line_attack", "high_mobility", "harass"],
        "scenario_tags": ["worker_harass", "multi_line_attack"],
    },
    {
        "intent": "drop_intercept",
        "keywords": ["drop interception", "drop intercept", "interception scenario", "intercept drop", "raid-route", "raid route"],
        "agents": ["ScenarioRouterAgent", "AbilityAgent", "UnitProfileAgent", "CounterAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "ability_effect", "ability_usage", "entity_tactical", "relation_counter"],
        "terms": ["drop_intercept", "transport", "mobility", "load", "unload", "anti_air", "long_range"],
        "scenario_tags": ["drop_intercept"],
    },
    {
        "intent": "scenario_lookup",
        "keywords": ["scenario", "scenario tag", "context", "knowledge source", "retrieval plan", "which kb"],
        "agents": ["ScenarioRouterAgent", "UnitProfileAgent", "AbilityAgent", "CounterAgent"],
        "doc_types": ["scenario_router", "scenario_candidates", "entity_tactical", "relation_counter", "ability_effect"],
        "terms": ["scenario", "scenario_tags", "recommended_kbs", "matched_entities", "matched_abilities", "matched_relations"],
        "scenario_tags": [],
    },
    {
        "intent": "evidence_layer_check",
        "keywords": ["rule enriched", "inferred", "raw fact", "source", "basis", "processed", "enriched", "evidence layer", "confidence"],
        "agents": ["UnitProfileAgent", "CounterAgent", "AbilityAgent", "ScenarioRouterAgent"],
        "doc_types": ["entity_tactical", "relation_counter", "ability_usage", "scenario_router"],
        "terms": ["local_enrichment", "relation_layer", "enriched", "processed", "rule_ids", "confidence"],
        "scenario_tags": [],
    },
]


QUERY_EXPANSIONS = {
    "marine": ["Marine", "terran_marine"],
    "marauder": ["Marauder", "terran_marauder"],
    "baneling": ["Baneling", "zerg_baneling"],
    "banes": ["Baneling", "zerg_baneling"],
    "light": ["light", "anti_light", "type_anti_light", "strong_against_type"],
    "armored": ["armored", "anti_armored", "type_anti_armored", "strong_against_type"],
    "structure": ["structure", "anti_structure", "type_anti_structure"],
    "hydralisk": ["Hydralisk", "zerg_hydralisk"],
    "zergling": ["Zergling", "zerg_zergling"],
    "infestor": ["Infestor", "zerg_infestor"],
    "fungal": ["Fungal Growth", "zerg_infestor_ability_fungal_growth"],
    "scan": ["Scanner Sweep", "terran_orbital_command_ability_scanner_sweep"],
    "scanner sweep": ["Scanner Sweep", "terran_orbital_command_ability_scanner_sweep"],
    "kd8 charge": ["KD8 Charge", "terran_reaper_ability_kd8_charge"],
    "stalker": ["Stalker", "protoss_stalker"],
    "observer": ["Observer", "protoss_observer"],
    "dark templar": ["DarkTemplar", "protoss_dark_templar"],
    "carrier": ["Carrier", "protoss_carrier"],
    "void ray": ["VoidRay", "protoss_void_ray"],
    "phoenix": ["Phoenix", "protoss_phoenix"],
    "colossus": ["Colossus", "protoss_colossus"],
    "warp prism": ["WarpPrism", "protoss_warpprism"],
    "thor": ["Thor", "terran_thor"],
    "siege tank": ["SiegeTank", "terran_siege_tank"],
    "raven": ["Raven", "terran_raven"],
    "queen": ["Queen", "zerg_queen"],
    "mutalisk": ["Mutalisk", "zerg_mutalisk"],
    "photon cannon": ["Photoncannon", "protoss_photoncannon"],
    "spore crawler": ["Spore Crawler", "zerg_spore_crawler"],
    "tech planning": ["tech_planning", "scenario_profile_tech_planning"],
    "rule enriched": ["enriched", "local_enrichment", "relation_layer", "rule_ids"],
}


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return [str(value)]


def derive_answer_requirements(query: str) -> list[str]:
    """Create conservative, query-only answer slots for coverage diagnostics.

    The slots deliberately do not use the reference answer.  A conjunction
    commonly denotes two independent facts in this benchmark; otherwise the
    full question remains one requirement.
    """

    cleaned = " ".join(str(query or "").split()).strip().rstrip("?")
    if not cleaned:
        return []
    match = re.search(r"\b(?:and|as well as)\b", cleaned, flags=re.IGNORECASE)
    if not match:
        return [cleaned]
    left, right = cleaned[: match.start()].strip(" ,;:"), cleaned[match.end() :].strip(" ,;:")
    if len(left) >= 8 and len(right) >= 4:
        return [left, right]
    return [cleaned]


def _extract_json_object(text: str) -> dict[str, Any]:
    """从 LLM 输出里提取 JSON 对象，兼容 ```json 包裹。"""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM output")
    return json.loads(cleaned[start : end + 1])


class RuleBasedRouter:
    """第一版 Router：只生成弱信号，不要求完整理解自然语言。"""

    def __init__(self, kb_store: KBStore) -> None:
        self.kb_store = kb_store
        self.domain_alias_resolver = DomainAliasResolver()

    def route(self, query: str) -> QueryPlan:
        query_lower = query.lower()
        intents: list[str] = []
        agents: list[str] = []
        doc_types: list[str] = []
        terms: list[str] = [query]
        scenario_tags: list[str] = []
        domain_alias = self.domain_alias_resolver.resolve(query)

        # 先注入 StarCraft II 领域别名线索，例如 DT -> Dark Templar -> protoss_dark_templar。
        # 这样规则 Router 和 LLM Router 都不需要单独学习所有玩家缩写。
        intents.extend(domain_alias.intent_candidates)
        agents.extend(domain_alias.candidate_agents)
        doc_types.extend(domain_alias.candidate_doc_types)
        terms.extend(domain_alias.query_terms)
        scenario_tags.extend(domain_alias.scenario_tags)

        for rule in ROUTING_RULES:
            matched = [kw for kw in rule["keywords"] if kw.lower() in query_lower]
            if not matched:
                continue
            intents.append(rule["intent"])
            agents.extend(rule["agents"])
            doc_types.extend(rule["doc_types"])
            terms.extend(matched)
            terms.extend(rule["terms"])
            scenario_tags.extend(rule["scenario_tags"])

        for keyword, expansions in QUERY_EXPANSIONS.items():
            if keyword.lower() in query_lower:
                terms.append(keyword)
                terms.extend(expansions)

        # Players often describe Land indirectly as returning a lifted
        # structure to the ground.  Preserve that semantic bridge before KB
        # entity/ability resolution rather than routing only to OrbitalCommand.
        if "lift" in query_lower and any(token in query_lower for token in ("land", "ground", "return")):
            terms.extend(["Land", "land"])

        terms.extend(re.findall(r"[A-Za-z][A-Za-z0-9_\-]+", query))
        entities = dedupe_keep_order([*domain_alias.entity_ids, *self.kb_store.resolve_entities_in_text(" ".join(terms))])
        abilities = dedupe_keep_order([*domain_alias.ability_ids, *self.kb_store.resolve_abilities_in_text(" ".join(terms))])

        if entities:
            agents.append("UnitProfileAgent")
            doc_types.extend(["entity_overview", "entity_combat", "entity_tactical"])
            terms.extend(entities)
        if abilities:
            agents.append("AbilityAgent")
            doc_types.extend(["ability_effect", "ability_usage"])
            terms.extend(abilities)

        return QueryPlan(
            raw_query=query,
            intent_candidates=dedupe_keep_order(intents),
            candidate_agents=dedupe_keep_order(agents or DEFAULT_AGENTS.copy()),
            candidate_doc_types=dedupe_keep_order(doc_types or DEFAULT_DOC_TYPES.copy()),
            query_terms=dedupe_keep_order(terms),
            entities=dedupe_keep_order(entities),
            abilities=dedupe_keep_order(abilities),
            scenario_tags=dedupe_keep_order(scenario_tags),
            answer_requirements=derive_answer_requirements(query),
            metadata={
                "router": "RuleBasedRouter",
                "strategy": "weak_signals",
                "domain_alias_resolution": domain_alias.to_dict(),
            },
        )


class LLMRouter(RuleBasedRouter):
    """LLM 增强 Router。

    规则 Router 先给出 base_plan，LLM 只负责补充/修正弱信号。
    所有输出都会被白名单校验；失败时自动回退 base_plan。
    """

    def __init__(
        self,
        kb_store: KBStore,
        provider: BaseLLMProvider,
        max_new_tokens: int = 512,
    ) -> None:
        super().__init__(kb_store)
        self.provider = provider
        self.max_new_tokens = max_new_tokens

    def route(self, query: str) -> QueryPlan:
        # 先运行规则 Router，得到一个稳定、可回退的基础 QueryPlan。
        # LLM 的职责是补充自然语言理解能力，而不是替代已有规则。
        base_plan = super().route(query)
        try:
            llm_data = self._call_llm(query, base_plan)
            merged = self._merge_plans(base_plan, llm_data)
            merged.metadata.update(
                {
                    "router": "LLMRouter",
                    "base_router": "RuleBasedRouter",
                    "llm_provider": self.provider.name,
                    "llm_confidence": llm_data.get("confidence"),
                    "llm_reason": llm_data.get("reason", ""),
                    "fallback": False,
                }
            )
            return merged
        except Exception as exc:
            base_plan.metadata.update(
                {
                    "router": "LLMRouter",
                    "base_router": "RuleBasedRouter",
                    "llm_provider": self.provider.name,
                    "fallback": True,
                    "fallback_reason": str(exc),
                }
            )
            return base_plan

    def _call_llm(self, query: str, base_plan: QueryPlan) -> dict[str, Any]:
        # 把规则结果、允许的 Agent/doc_type、已知场景标签一起交给 LLM。
        # 这样 LLM 只能在当前系统支持的候选空间内做判断，减少编造字段。
        scenario_tags = sorted(self.kb_store.scenario_by_tag)
        user_prompt = {
            "query": query,
            "base_plan": asdict(base_plan),
            "domain_alias_resolution": base_plan.metadata.get("domain_alias_resolution", {}),
            "allowed_agents": sorted(AGENT_NAMES),
            "allowed_doc_types": sorted(DOC_TYPE_TO_PRIMARY_AGENT),
            "known_scenario_tags": scenario_tags,
            "routing_examples": ROUTER_FEW_SHOT_EXAMPLES,
            "output_schema": {
                "intent_candidates": ["string"],
                "candidate_agents": ["allowed agent"],
                "candidate_doc_types": ["allowed doc_type"],
                "query_terms": ["string"],
                "scenario_tags": ["known scenario tag"],
                "answer_requirements": ["short factual requirement from the query"],
                "confidence": 0.0,
                "reason": "short English routing reason",
            },
            "requirements": [
                "Output only one JSON object.",
                "Include every field in output_schema.",
                "candidate_agents must come from allowed_agents.",
                "candidate_doc_types must come from allowed_doc_types.",
                "confidence must be a number between 0 and 1.",
                "reason must be a short English reason.",
                "answer_requirements must split independent requested facts, never add a factual answer.",
                "Do not invent entity ids or ability ids; put uncertain surface forms into query_terms.",
                "The Router goal is to improve recall over rag_documents.",
            ],
        }
        messages = [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT.strip()},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ]
        response = self.provider.complete(messages, max_new_tokens=self.max_new_tokens, temperature=0.0)
        return _extract_json_object(response.text)

    def _merge_plans(self, base_plan: QueryPlan, llm_data: dict[str, Any]) -> QueryPlan:
        # 合并不是无条件相信 LLM：Agent、doc_type、scenario_tag 都先过白名单。
        # entity_id / ability_id 不直接取 LLM 输出，而是用合并后的 query_terms 再回到 KBStore 解析。
        allowed_scenarios = set(self.kb_store.scenario_by_tag)
        llm_agents = [agent for agent in _as_str_list(llm_data.get("candidate_agents")) if agent in AGENT_NAMES]
        llm_doc_types = [doc_type for doc_type in _as_str_list(llm_data.get("candidate_doc_types")) if doc_type in DOC_TYPE_TO_PRIMARY_AGENT]
        llm_scenarios = [tag for tag in _as_str_list(llm_data.get("scenario_tags")) if tag in allowed_scenarios]
        llm_terms = _as_str_list(llm_data.get("query_terms"))
        llm_requirements = [item for item in _as_str_list(llm_data.get("answer_requirements")) if 4 <= len(item) <= 180]

        # query_terms 是后续检索的核心入口，保留规则线索，同时加入 LLM 识别出的同义词/战术词。
        query_terms = dedupe_keep_order([*base_plan.query_terms, *llm_terms, *llm_scenarios])
        entities = self.kb_store.resolve_entities_in_text(" ".join(query_terms))
        abilities = self.kb_store.resolve_abilities_in_text(" ".join(query_terms))

        base_has_specific_signals = bool(
            base_plan.intent_candidates or base_plan.entities or base_plan.abilities or base_plan.scenario_tags
        )
        # 如果规则完全没命中，base_plan 里的 Agent/doc_type 是默认全量候选。
        # 此时优先采用 LLM 给出的收窄候选；如果规则已有明确命中，则保留规则结果并补充 LLM。
        if base_has_specific_signals:
            agents = dedupe_keep_order([*base_plan.candidate_agents, *llm_agents])
            doc_types = dedupe_keep_order([*base_plan.candidate_doc_types, *llm_doc_types])
        else:
            agents = dedupe_keep_order(llm_agents or base_plan.candidate_agents)
            doc_types = dedupe_keep_order(llm_doc_types or base_plan.candidate_doc_types)
        if entities:
            agents = dedupe_keep_order([*agents, "UnitProfileAgent"])
            doc_types = dedupe_keep_order([*doc_types, "entity_overview", "entity_combat", "entity_tactical"])
        if abilities:
            agents = dedupe_keep_order([*agents, "AbilityAgent"])
            doc_types = dedupe_keep_order([*doc_types, "ability_effect", "ability_usage"])

        metadata = dict(base_plan.metadata)
        metadata["llm_narrowed_default_candidates"] = not base_has_specific_signals and bool(llm_agents or llm_doc_types)

        return QueryPlan(
            raw_query=base_plan.raw_query,
            intent_candidates=dedupe_keep_order([*base_plan.intent_candidates, *_as_str_list(llm_data.get("intent_candidates"))]),
            candidate_agents=agents or DEFAULT_AGENTS.copy(),
            candidate_doc_types=doc_types or DEFAULT_DOC_TYPES.copy(),
            query_terms=query_terms,
            entities=dedupe_keep_order(entities),
            abilities=dedupe_keep_order(abilities),
            scenario_tags=dedupe_keep_order([*base_plan.scenario_tags, *llm_scenarios]),
            answer_requirements=dedupe_keep_order(llm_requirements or base_plan.answer_requirements),
            metadata=metadata,
        )

