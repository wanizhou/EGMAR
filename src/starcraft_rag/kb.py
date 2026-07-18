from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def normalize_key(value: Any) -> str:
    text = str(value or "").lower()
    return re.sub(r"[\s_\-\.:'\"/\\()\[\]{}]+", "", text)


GENERIC_ABILITY_ALIAS_KEYS = {
    "cloak",
    "detector",
    "land",
    "lift",
    "liftoff",
    "load",
    "unload",
}


def _query_alias_tokens(text: str) -> set[str]:
    return {normalize_key(token) for token in re.split(r"[\s,;；，。！？?]+", text) if normalize_key(token)}


def _ability_alias_matches(alias_key: str, query_key: str, query_tokens: set[str]) -> bool:
    if not alias_key:
        return False
    # 技能别名比实体别名更容易误伤：例如 anti_cloak_response 不能被当成 Cloak 技能。
    # 因此短词和通用词只允许“完整 token 命中”，较长技能名/技能 id 才允许子串命中。
    if alias_key in query_tokens:
        return True
    if alias_key in GENERIC_ABILITY_ALIAS_KEYS:
        return False
    if "ability" in alias_key and alias_key in query_key:
        return True
    return len(alias_key) >= 10 and alias_key in query_key


def _ability_name_aliases(value: Any) -> list[str]:
    if not value:
        return []
    text = str(value)
    aliases = [text]
    # 原始静态表中部分技能带 Effect_/Research_ 前缀，玩家提问通常会省略这些内部前缀。
    for prefix in ("Effect_", "Effect", "Research_", "Research"):
        if text.lower().startswith(prefix.lower()):
            aliases.append(text[len(prefix) :])
    return aliases


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path} line {line_no} is not valid JSON: {exc}") from exc
    return rows


class KBStore:
    """加载 runtime_kb，并集中维护各种 id 到 profile 的索引。"""

    def __init__(self, runtime_kb_dir: str | Path | None = None) -> None:
        my_knowledge_dir = Path(__file__).resolve().parents[1]
        self.runtime_kb_dir = Path(runtime_kb_dir) if runtime_kb_dir else my_knowledge_dir / "starcraft_kb" / "runtime_kb"

        self.entity_profiles = read_jsonl(self.runtime_kb_dir / "entity_profiles.jsonl")
        self.ability_profiles = read_jsonl(self.runtime_kb_dir / "ability_profiles.jsonl")
        self.relation_profiles = read_jsonl(self.runtime_kb_dir / "relation_profiles.jsonl")
        self.scenario_profiles = read_jsonl(self.runtime_kb_dir / "scenario_profiles.jsonl")
        self.rag_documents = read_jsonl(self.runtime_kb_dir / "rag_documents.jsonl")

        self.profiles_by_id: dict[str, dict[str, Any]] = {}
        self.entity_by_entity_id: dict[str, dict[str, Any]] = {}
        self.ability_by_ability_id: dict[str, dict[str, Any]] = {}
        self.relation_by_relation_id: dict[str, dict[str, Any]] = {}
        self.scenario_by_tag: dict[str, dict[str, Any]] = {}
        self.alias_to_entity_ids: dict[str, set[str]] = {}
        self.alias_to_ability_ids: dict[str, set[str]] = {}

        self._build_indexes()

    def _build_indexes(self) -> None:
        for profile in self.entity_profiles:
            self._index_profile(profile)
            entity_id = profile.get("entity_id")
            if entity_id and entity_id not in self.entity_by_entity_id:
                self.entity_by_entity_id[entity_id] = profile
            self._index_entity_aliases(profile)

        for profile in self.ability_profiles:
            self._index_profile(profile)
            ability_id = profile.get("ability_id")
            if ability_id and ability_id not in self.ability_by_ability_id:
                self.ability_by_ability_id[ability_id] = profile
            self._index_ability_aliases(profile)

        for profile in self.relation_profiles:
            self._index_profile(profile)
            relation_id = profile.get("relation_id")
            if relation_id and relation_id not in self.relation_by_relation_id:
                self.relation_by_relation_id[relation_id] = profile

        for profile in self.scenario_profiles:
            self._index_profile(profile)
            scenario_tag = profile.get("scenario_tag")
            if scenario_tag:
                self.scenario_by_tag[scenario_tag] = profile

    def _index_profile(self, profile: dict[str, Any]) -> None:
        profile_id = profile.get("profile_id")
        if profile_id and profile_id not in self.profiles_by_id:
            self.profiles_by_id[profile_id] = profile

    def _index_entity_aliases(self, profile: dict[str, Any]) -> None:
        entity_id = profile.get("entity_id")
        if not entity_id:
            return
        identity = profile.get("identity") or {}
        aliases = [entity_id, identity.get("name"), *(identity.get("aliases") or [])]
        for alias in aliases:
            key = normalize_key(alias)
            if key:
                self.alias_to_entity_ids.setdefault(key, set()).add(entity_id)

    def _index_ability_aliases(self, profile: dict[str, Any]) -> None:
        ability_id = profile.get("ability_id")
        if not ability_id:
            return
        # ability alias 只索引技能自身。owner 名称属于实体线索，不再映射到该单位的所有技能，
        # 否则“Dark Templar/反隐”这类问题会误命中过多 cloak/warp 类技能。
        aliases = [ability_id, *_ability_name_aliases(profile.get("ability_name"))]
        for alias in aliases:
            key = normalize_key(alias)
            if key:
                self.alias_to_ability_ids.setdefault(key, set()).add(ability_id)

    def resolve_entities_in_text(self, text: str) -> list[str]:
        query_key = normalize_key(text)
        found: list[str] = []
        for alias_key, entity_ids in self.alias_to_entity_ids.items():
            if alias_key and alias_key in query_key:
                found.extend(sorted(entity_ids))
        return sorted(set(found))

    def resolve_abilities_in_text(self, text: str) -> list[str]:
        query_key = normalize_key(text)
        query_tokens = _query_alias_tokens(text)
        found: list[str] = []
        for alias_key, ability_ids in self.alias_to_ability_ids.items():
            if _ability_alias_matches(alias_key, query_key, query_tokens):
                found.extend(sorted(ability_ids))
        return sorted(set(found))

    def get_profile(self, profile_id: str) -> dict[str, Any] | None:
        return self.profiles_by_id.get(profile_id)

    def get_profile_id_for_entity(self, entity_id: str) -> str | None:
        profile = self.entity_by_entity_id.get(entity_id)
        return profile.get("profile_id") if profile else None

    def get_profile_id_for_ability(self, ability_id: str) -> str | None:
        profile = self.ability_by_ability_id.get(ability_id)
        return profile.get("profile_id") if profile else None

    def get_profile_id_for_relation(self, relation_id: str) -> str | None:
        profile = self.relation_by_relation_id.get(relation_id)
        return profile.get("profile_id") if profile else None

    def get_profile_id_for_scenario(self, scenario_tag: str) -> str | None:
        profile = self.scenario_by_tag.get(scenario_tag)
        return profile.get("profile_id") if profile else None
