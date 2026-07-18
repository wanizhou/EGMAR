from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


@dataclass(frozen=True)
class DomainAliasEntry:
    aliases: list[str]
    query_terms: list[str]
    entity_ids: list[str] = field(default_factory=list)
    ability_ids: list[str] = field(default_factory=list)
    base_intents: list[str] = field(default_factory=list)
    base_agents: list[str] = field(default_factory=list)
    base_doc_types: list[str] = field(default_factory=list)
    base_scenario_tags: list[str] = field(default_factory=list)
    threat_terms: list[str] = field(default_factory=list)
    threat_intents: list[str] = field(default_factory=list)
    threat_agents: list[str] = field(default_factory=list)
    threat_doc_types: list[str] = field(default_factory=list)
    threat_scenario_tags: list[str] = field(default_factory=list)


@dataclass
class AliasResolution:
    """DomainAliasResolver 的输出结果。

    这些字段都是 Router 的弱信号：用于补充 query_terms、候选 Agent 和场景标签，
    不直接替代后续 KBStore 的实体/技能回连。
    """

    matched_aliases: list[str] = field(default_factory=list)
    query_terms: list[str] = field(default_factory=list)
    entity_ids: list[str] = field(default_factory=list)
    ability_ids: list[str] = field(default_factory=list)
    intent_candidates: list[str] = field(default_factory=list)
    candidate_agents: list[str] = field(default_factory=list)
    candidate_doc_types: list[str] = field(default_factory=list)
    scenario_tags: list[str] = field(default_factory=list)
    context_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        return asdict(self)


DOMAIN_ALIAS_ENTRIES = [
    DomainAliasEntry(
        aliases=["DT", "Dark Templar", "DarkTemplar"],
        query_terms=["DT", "Dark Templar", "DarkTemplar", "protoss_dark_templar"],
        entity_ids=["protoss_dark_templar"],
        base_agents=["UnitProfileAgent"],
        base_doc_types=["entity_overview", "entity_combat", "entity_tactical"],
        threat_terms=["anti_cloak", "cloaked unit", "detector", "reveal", "Scanner Sweep", "anti_cloak_response"],
        threat_intents=["anti_cloak_response", "counter_relation"],
        threat_agents=["ScenarioRouterAgent", "AbilityAgent", "CounterAgent"],
        threat_doc_types=["scenario_router", "scenario_candidates", "ability_effect", "ability_usage", "relation_counter"],
        threat_scenario_tags=["anti_cloak_response"],
    ),
    DomainAliasEntry(
        aliases=["BC", "Battlecruiser"],
        query_terms=["BC", "Battlecruiser", "terran_battlecruiser"],
        entity_ids=["terran_battlecruiser"],
        base_agents=["UnitProfileAgent"],
        base_doc_types=["entity_overview", "entity_combat", "entity_tactical"],
        threat_terms=["air army", "anti_air", "air_control", "capital_ship"],
        threat_intents=["air_control", "counter_relation"],
        threat_agents=["ScenarioRouterAgent", "CounterAgent", "UnitProfileAgent"],
        threat_doc_types=["scenario_router", "scenario_candidates", "entity_combat", "relation_counter"],
        threat_scenario_tags=["air_control"],
    ),
    DomainAliasEntry(
        aliases=["HT", "High Templar", "HighTemplar"],
        query_terms=["HT", "High Templar", "HighTemplar", "protoss_hightemplar"],
        entity_ids=["protoss_hightemplar"],
        base_agents=["UnitProfileAgent", "AbilityAgent"],
        base_doc_types=["entity_overview", "entity_abilities", "ability_effect", "ability_usage"],
    ),
    DomainAliasEntry(
        aliases=["storm", "Psionic Storm"],
        query_terms=["storm", "Psionic Storm", "protoss_hightemplar_ability_psionic_storm"],
        entity_ids=["protoss_hightemplar"],
        ability_ids=["protoss_hightemplar_ability_psionic_storm"],
        base_intents=["ability_effect"],
        base_agents=["AbilityAgent", "ScenarioRouterAgent"],
        base_doc_types=["ability_effect", "ability_usage", "scenario_candidates"],
        base_scenario_tags=["clumped_enemy_counter", "frontal_combat"],
    ),
    DomainAliasEntry(
        aliases=["scan", "Scanner Sweep"],
        query_terms=["scan", "Scanner Sweep", "terran_orbital_command_ability_scanner_sweep"],
        ability_ids=["terran_orbital_command_ability_scanner_sweep"],
        base_intents=["anti_cloak_response", "ability_effect"],
        base_agents=["AbilityAgent", "ScenarioRouterAgent"],
        base_doc_types=["ability_effect", "ability_usage", "scenario_router", "scenario_candidates"],
        base_scenario_tags=["anti_cloak_response"],
    ),
    DomainAliasEntry(
        aliases=["ling", "lings", "Zergling"],
        query_terms=["ling", "lings", "Zergling", "zerg_zergling"],
        entity_ids=["zerg_zergling"],
        base_agents=["UnitProfileAgent"],
        base_doc_types=["entity_overview", "entity_combat", "entity_tactical"],
    ),
    DomainAliasEntry(
        aliases=["banes", "Baneling"],
        query_terms=["banes", "Baneling", "zerg_baneling"],
        entity_ids=["zerg_baneling"],
        base_agents=["UnitProfileAgent", "CounterAgent"],
        base_doc_types=["entity_combat", "entity_tactical", "relation_counter"],
    ),
    DomainAliasEntry(
        aliases=["tank", "Siege Tank", "SiegeTank"],
        query_terms=["tank", "Siege Tank", "SiegeTank", "terran_siege_tank"],
        entity_ids=["terran_siege_tank"],
        base_agents=["UnitProfileAgent", "TechTreeAgent"],
        base_doc_types=["entity_overview", "entity_combat", "entity_cost_tech"],
    ),
]


THREAT_CONTEXT_KEYWORDS = [
    "counter",
    "against",
    "respond",
    "handle",
    "deal with",
    "facing",
    "opponent",
    "threat",
]

TECH_CONTEXT_KEYWORDS = [
    "build",
    "produce",
    "cost",
    "prerequisite",
    "require",
    "tech",
    "research",
]


class DomainAliasResolver:
    """StarCraft II 领域术语归一化器。

    它处理玩家常用缩写、俗称和英文简称，例如 DT、BC、HT。
    这个类不负责回答问题，只把自然语言补充成 RAG 更容易检索的标准线索。
    """

    def __init__(self, entries: list[DomainAliasEntry] | None = None) -> None:
        self.entries = entries or DOMAIN_ALIAS_ENTRIES

    def resolve(self, query: str) -> AliasResolution:
        resolution = AliasResolution()
        query_lower = query.lower()
        is_threat_context = self._has_context(query_lower, THREAT_CONTEXT_KEYWORDS)
        is_tech_context = self._has_context(query_lower, TECH_CONTEXT_KEYWORDS)

        if is_threat_context:
            resolution.context_flags.append("threat_context")
        if is_tech_context:
            resolution.context_flags.append("tech_context")

        for entry in self.entries:
            matched = [alias for alias in entry.aliases if self._alias_in_query(query, alias)]
            if not matched:
                continue

            resolution.matched_aliases.extend(matched)
            resolution.query_terms.extend(entry.query_terms)
            resolution.entity_ids.extend(entry.entity_ids)
            resolution.ability_ids.extend(entry.ability_ids)
            resolution.intent_candidates.extend(entry.base_intents)
            resolution.candidate_agents.extend(entry.base_agents)
            resolution.candidate_doc_types.extend(entry.base_doc_types)
            resolution.scenario_tags.extend(entry.base_scenario_tags)

            # “对面转 DT 怎么应对”这类威胁语境下，别名解析器主动补充反隐/克制线索。
            # “DT 怎么造”只会走科技树语境，不会强行加入反隐场景。
            if is_threat_context and entry.threat_terms:
                resolution.query_terms.extend(entry.threat_terms)
                resolution.intent_candidates.extend(entry.threat_intents)
                resolution.candidate_agents.extend(entry.threat_agents)
                resolution.candidate_doc_types.extend(entry.threat_doc_types)
                resolution.scenario_tags.extend(entry.threat_scenario_tags)

        resolution.matched_aliases = dedupe_keep_order(resolution.matched_aliases)
        resolution.query_terms = dedupe_keep_order(resolution.query_terms)
        resolution.entity_ids = dedupe_keep_order(resolution.entity_ids)
        resolution.ability_ids = dedupe_keep_order(resolution.ability_ids)
        resolution.intent_candidates = dedupe_keep_order(resolution.intent_candidates)
        resolution.candidate_agents = dedupe_keep_order(resolution.candidate_agents)
        resolution.candidate_doc_types = dedupe_keep_order(resolution.candidate_doc_types)
        resolution.scenario_tags = dedupe_keep_order(resolution.scenario_tags)
        resolution.context_flags = dedupe_keep_order(resolution.context_flags)
        return resolution

    @staticmethod
    def _has_context(query_lower: str, keywords: list[str]) -> bool:
        return any(keyword.lower() in query_lower for keyword in keywords)

    @staticmethod
    def _alias_in_query(query: str, alias: str) -> bool:
        # 短英文缩写必须按 token 边界匹配，避免 HT 误撞到其他英文单词片段。
        if re.fullmatch(r"[A-Za-z.]{1,4}", alias):
            compact_alias = re.escape(alias.replace(".", ""))
            compact_query = re.sub(r"\.", "", query)
            return bool(re.search(rf"(?<![A-Za-z0-9]){compact_alias}(?![A-Za-z0-9])", compact_query, flags=re.IGNORECASE))
        return alias.lower() in query.lower()
