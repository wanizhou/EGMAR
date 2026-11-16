from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import random
import re
import statistics
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


MODEL_POOL = [
    "deepseek-ai/DeepSeek-V4-Flash",
    "Qwen/Qwen3.6-35B-A3B",
    "Pro/zai-org/GLM-5.1",
    "MiniMaxAI/MiniMax-M2.5",
    "zai-org/GLM-5.2",
]

# 本地 pilot 临时使用；若设置 SILICONFLOW_API_KEY，则优先使用环境变量。
DEFAULT_API_KEY = ""
DEFAULT_SAMPLES_PER_MODEL_COMPLEXITY = 5
DEBUG_SAMPLE_COUNT = 1
REPORT_FILE_NAME = "qa_generation_metrics_v1_report.md"

QUESTION_META_PATTERNS = [
    r"\bknowledge base\b",
    r"\bcurrent kb\b",
    r"\bkb\b",
    r"\bevidence\b",
    r"\bevidence packet\b",
    r"\bprovided evidence\b",
    r"\bprofile\b",
    r"\bjson\b",
    r"\bfield\b",
    r"\bavailable facts\b",
    r"\bprovided facts\b",
    r"\bprovided data\b",
    r"\bexplicit facts\b",
    r"\btarget list\b",
]

ANSWER_META_PHRASES = [
    "according to the knowledge base",
    "the knowledge base",
    "knowledge base contains",
    "knowledge base links",
    "current kb",
    "the current kb",
    "the evidence indicates",
    "evidence indicates",
    "provided evidence",
    "evidence packet",
    "ability profile",
    "entity profile",
    "relation profile",
    "scenario profile",
    "the evidence",
    "available facts",
    "provided facts",
    "provided data",
    "explicit facts",
    "abilities field",
    "target list",
    "scenario context",
    "evidence",
    "profile",
    "supplied claims",
]

PUBLIC_TEXT_REPLACEMENTS = {
    "CyberneticsCore": "Cybernetics Core",
    "TwilightCouncil": "Twilight Council",
    "RoboticsFacility": "Robotics Facility",
    "RoboticsBay": "Robotics Bay",
    "Stargate": "Stargate",
    "WarpGate": "Warp Gate",
    "Warpprism": "Warp Prism",
    "WarpPrism": "Warp Prism",
    "WarpPrismPhasing": "Phasing Warp Prism",
    "VoidRay": "Void Ray",
    "DarkTemplar": "Dark Templar",
    "HighTemplar": "High Templar",
    "Mothershipcore": "Mothership Core",
    "PhotonCannon": "Photon Cannon",
    "Photoncannon": "Photon Cannon",
    "ShieldBattery": "Shield Battery",
    "SpineCrawler": "Spine Crawler",
    "SporeCrawler": "Spore Crawler",
    "WidowMine": "Widow Mine",
    "SiegeTank": "Siege Tank",
    "Hellbat": "Hellbat",
    "CommandCenter": "Command Center",
    "SupplyDepot": "Supply Depot",
    "OrbitalCommand": "Orbital Command",
    "StarportTechLab": "Starport Tech Lab",
    "FactoryTechLab": "Factory Tech Lab",
    "BarracksTechLab": "Barracks Tech Lab",
    "StarportReactor": "Starport Reactor",
    "FactoryReactor": "Factory Reactor",
    "BarracksReactor": "Barracks Reactor",
    "LurkerBurrowed": "Burrowed Lurker",
    "DisruptorPhased": "Phased Disruptor",
    "Broodlord": "Brood Lord",
    "LocustFlying": "Flying Locust",
    "PsionicTransfer": "Psionic Transfer",
    "Effect PsionicTransfer": "Psionic Transfer",
    "Effect Psionic Transfer": "Psionic Transfer",
    "WorkerAbilities": "worker abilities",
    "potentially_strong_against": "potentially strong against",
    "strong_against": "strong against",
    "anti_air": "anti-air",
    "anti_ground": "anti-ground",
    "anti_cloak": "anti-cloak",
    "area_of_effect": "area-of-effect",
}

PUBLIC_TEXT_REGEX_REPLACEMENTS = [
    (r"\bhas a potentially strong against relation with\b", "is marked as potentially strong against"),
    (r"\bhas a potentially strong relation against\b", "is marked as potentially strong against"),
    (r"\bpotentially strong against relation\b", "potentially strong relationship"),
    (r"\baccording to the relation data\b", "based on the available facts"),
    (r"\bthe evidence does not specify\b", "the available facts do not specify"),
    (r"\bthe evidence does not provide\b", "the available facts do not provide"),
    (r"\bthe evidence shows\b", "the available facts show"),
    (r"\bthe evidence also\b", "the available facts also"),
    (r"\bsource's bonus type\b", "the unit's bonus damage type"),
    (r"\btarget's own type profile\b", "the target's unit traits"),
    (r"\btype profile\b", "unit traits"),
    (r"\bin (?:a|the) combat profile\b", "in its combat characteristics"),
    (r"\bcombat profile\b", "combat characteristics"),
    (r"\bprovided data\b", "available facts"),
    (r"\bthe evidence (?:indicates|suggests|shows)\b", "the available facts indicate"),
    (r"\baoe\b", "area-of-effect"),
    (r"\bthe available facts (?:indicate|show) the available facts\b", "the available facts state"),
]

INTERNAL_DIRECT_TERMS = [
    "profile_id",
    "field_path",
    "evidence_packet",
    "entity_profile_",
    "ability_profile_",
    "relation_profile_",
    "scenario_profile_",
    "source_profile_id",
    "entity_id",
    "ability_id",
    "scenario_tag",
    "target_type",
    "relation_layer",
]
INTERNAL_SURFACE_PHRASES = [
    "listed in its profile",
    "listed in the profile",
    "shown in its profile",
    "shown in the profile",
    "profile lists",
    "profile says",
    "relation data",
    "combat profile",
    "type profile",
    "source's bonus type",
    "target's own type",
    "abilities field",
    "target list",
    "explicit facts",
    "available facts",
    "provided facts",
    "provided data",
    "scenario context",
    "type matching",
    "evidence",
    "profile",
    "supplied claims",
]
INTERNAL_CAMEL_ALLOWLIST = {"StarCraft"}

# 关系型增强事实较容易产生不自然的“单位克制建筑/附属建筑”样本，
# 因此仅保留少量经过目标层与实体类型校验的关系候选。

COMPLEXITIES = ["single_hop", "two_hop", "multi_hop", "ambiguous"]
EVIDENCE_LAYER_EXPLICIT = "explicit_fact"
EVIDENCE_LAYER_CONDITIONAL = "conditional_relation"
EVIDENCE_LAYER_DERIVED = "derived_hint"
QUALITY_VERIFIED = "verified"
QUALITY_SUSPECT = "suspect"
QUALITY_BLOCKED = "blocked"

# 这些 ID 已经通过 200 条 pilot 的回查确认存在跨单位错配或重复。
# 这里先隔离，不擅自修正原始静态表；后续有权威来源后再回到 processed 阶段修复。
KNOWN_BLOCKED_ENTITY_IDS = {"terran_hellbat", "terran_viking", "terran_marauder"}
KNOWN_BLOCKED_ABILITY_IDS = {
    "terran_reaper_ability_combat_drugs",
    "terran_hellbat_ability_lock_on",
}
DAMAGED_TEXT_PATTERNS = [
    r"\bqueencost\b",
    r"\bavailabledrains\b",
    r"\bavailablelocks\b",
    r"seconds\.required\b",
]
QA_DATASET_SCHEMA_VERSION = "qa_metrics_v2_structural_filter"
HAN_RE = re.compile(r"[\u4e00-\u9fff]")
CAMEL_CASE_RE = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b")
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")

COMPLEXITY_DEFINITIONS = {
    "single_hop": "The question is answered by exactly one verified field-level claim.",
    "two_hop": "The answer combines two connected verified claims, and both claims are necessary.",
    "multi_hop": "The answer follows a connected chain of at least three claims; removing a core claim makes the answer incomplete.",
    "ambiguous": "The question has a natural gameplay ambiguity such as target, mode, condition, or matchup context; the answer explains valid branches without referring to missing database fields.",
}

VALIDATION_THRESHOLDS = {
    "mean_answer_score": 8.0,
    "mean_groundedness_score": 8.0,
    "mean_complexity_confidence": 6.0,
    "min_answer_score": 7.0,
    "min_groundedness_score": 6.0,
    "min_accept_count": 3,
    "min_complexity_label_count": 2,
}


@dataclass
class RuntimeKB:
    rag_documents: list[dict[str, Any]]
    entity_profiles: list[dict[str, Any]]
    ability_profiles: list[dict[str, Any]]
    relation_profiles: list[dict[str, Any]]
    scenario_profiles: list[dict[str, Any]]
    profiles_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    entity_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    ability_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    blocked_entity_ids: set[str] = field(default_factory=set)
    blocked_ability_ids: set[str] = field(default_factory=set)
    blocked_profile_ids: set[str] = field(default_factory=set)
    quality_issues: list[dict[str, str]] = field(default_factory=list)
    quality_counts: dict[str, int] = field(default_factory=dict)
    entity_claim_cache: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    ability_claim_cache: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    relation_candidate_cache: dict[bool, list[dict[str, Any]]] = field(default_factory=dict)


@dataclass
class ValidatorResult:
    model: str
    answer_score: float
    groundedness_score: float
    complexity_confidence: float
    predicted_evidence_complexity: str
    accept: bool
    derived_hint_leak: bool
    source_quality_valid: bool
    all_sentences_supported: bool
    evidence_chain_connected: bool
    all_hops_necessary: bool
    single_claim_focus_valid: bool
    ambiguity_domain_valid: bool
    reason: str


@dataclass
class BuildStats:
    accepted_by_model: dict[str, int] = field(default_factory=dict)
    accepted_by_complexity: dict[str, int] = field(default_factory=dict)
    attempts_by_slot: dict[str, int] = field(default_factory=dict)
    rejected_reasons: dict[str, int] = field(default_factory=dict)
    model_failures: dict[str, int] = field(default_factory=dict)
    bge_dedupe_enabled: bool = False
    bge_dedupe_note: str = ""
    evidence_layer_uses: dict[str, int] = field(default_factory=dict)
    derived_hint_context_samples: int = 0
    conditional_relation_layers: dict[str, int] = field(default_factory=dict)
    derived_hint_claim_rejects: int = 0
    kb_quality_counts: dict[str, int] = field(default_factory=dict)
    accepted_packet_types: dict[str, int] = field(default_factory=dict)
    accepted_provenance: list[dict[str, Any]] = field(default_factory=list)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path} line {line_no} is not valid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def target_sample_count(samples_per_model_complexity: int) -> int:
    """根据模型数、复杂度类别数和每格样本数计算最终公开样本总数。"""

    return len(MODEL_POOL) * len(COMPLEXITIES) * samples_per_model_complexity


def output_path(total_count: int) -> Path:
    return Path(__file__).resolve().parent / f"qa_dataset_{total_count}_metrics_v1.jsonl"


def report_path() -> Path:
    return Path(__file__).resolve().parent / REPORT_FILE_NAME


def checkpoint_paths(total_count: int) -> tuple[Path, Path]:
    base = Path(__file__).resolve().parent / f"qa_dataset_{total_count}_metrics_v1"
    return base.with_suffix(".checkpoint.jsonl"), base.with_suffix(".checkpoint.meta.json")


def stats_to_dict(stats: BuildStats) -> dict[str, Any]:
    return {
        "accepted_by_model": stats.accepted_by_model,
        "accepted_by_complexity": stats.accepted_by_complexity,
        "attempts_by_slot": stats.attempts_by_slot,
        "rejected_reasons": stats.rejected_reasons,
        "model_failures": stats.model_failures,
        "evidence_layer_uses": stats.evidence_layer_uses,
        "derived_hint_context_samples": stats.derived_hint_context_samples,
        "conditional_relation_layers": stats.conditional_relation_layers,
        "derived_hint_claim_rejects": stats.derived_hint_claim_rejects,
        "kb_quality_counts": stats.kb_quality_counts,
        "accepted_packet_types": stats.accepted_packet_types,
        "accepted_provenance": stats.accepted_provenance,
    }


def stats_from_dict(data: dict[str, Any] | None) -> BuildStats:
    data = data or {}
    return BuildStats(
        accepted_by_model=dict(data.get("accepted_by_model") or {}),
        accepted_by_complexity=dict(data.get("accepted_by_complexity") or {}),
        attempts_by_slot=dict(data.get("attempts_by_slot") or {}),
        rejected_reasons=dict(data.get("rejected_reasons") or {}),
        model_failures=dict(data.get("model_failures") or {}),
        evidence_layer_uses=dict(data.get("evidence_layer_uses") or {}),
        derived_hint_context_samples=int(data.get("derived_hint_context_samples") or 0),
        conditional_relation_layers=dict(data.get("conditional_relation_layers") or {}),
        derived_hint_claim_rejects=int(data.get("derived_hint_claim_rejects") or 0),
        kb_quality_counts=dict(data.get("kb_quality_counts") or {}),
        accepted_packet_types=dict(data.get("accepted_packet_types") or {}),
        accepted_provenance=list(data.get("accepted_provenance") or []),
    )


def checkpoint_config(args: argparse.Namespace, target_count: int, samples_per_slot: int) -> dict[str, Any]:
    """生成用于 resume 校验的稳定配置，避免不同参数的中间文件被误用。"""

    return {
        "model_pool": MODEL_POOL,
        "complexities": COMPLEXITIES,
        "samples_per_model_complexity": samples_per_slot,
        "target_count": target_count,
        "seed": args.seed,
        "runtime_kb": str(Path(args.runtime_kb).resolve()),
        "skip_bge_dedupe": bool(args.skip_bge_dedupe),
        "qa_dataset_schema_version": QA_DATASET_SCHEMA_VERSION,
    }


def checkpoint_meta_matches(saved_meta: dict[str, Any], expected_config: dict[str, Any]) -> bool:
    return all(saved_meta.get(key) == value for key, value in expected_config.items())


def write_checkpoint(total_count: int, rows: list[dict[str, Any]], stats: BuildStats, config: dict[str, Any]) -> None:
    checkpoint_file, checkpoint_meta_file = checkpoint_paths(total_count)
    write_jsonl(checkpoint_file, rows)
    meta = {**config, "stats": stats_to_dict(stats)}
    checkpoint_meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_checkpoint(total_count: int, expected_config: dict[str, Any]) -> tuple[list[dict[str, Any]], BuildStats] | None:
    checkpoint_file, checkpoint_meta_file = checkpoint_paths(total_count)
    if not checkpoint_file.exists() and not checkpoint_meta_file.exists():
        return None
    if not checkpoint_file.exists() or not checkpoint_meta_file.exists():
        raise SystemExit(f"Incomplete checkpoint found. Remove {checkpoint_file} and {checkpoint_meta_file}, or rerun with --no-resume.")
    saved_meta = json.loads(checkpoint_meta_file.read_text(encoding="utf-8"))
    if not checkpoint_meta_matches(saved_meta, expected_config):
        raise SystemExit(f"Checkpoint config mismatch. Remove {checkpoint_file} and {checkpoint_meta_file}, or rerun with --no-resume.")
    rows = read_jsonl(checkpoint_file)
    validate_public_dataset(rows, expected_count=None)
    return rows, stats_from_dict(saved_meta.get("stats"))


def remove_checkpoint(total_count: int) -> None:
    for path in checkpoint_paths(total_count):
        if path.exists():
            path.unlink()


def compact(value: Any, limit: int = 360) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def normalize_question(text: str) -> str:
    lowered = str(text or "").lower()
    table = str.maketrans("", "", string.punctuation)
    return " ".join(lowered.translate(table).split())


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output")
    return json.loads(cleaned[start : end + 1])


def normalize_complexity(value: Any) -> str:
    """把模型可能输出的 single-hop / Single Hop 等变体归一到固定标签。"""

    text = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    for item in COMPLEXITIES:
        if text == item or item in text:
            return item
    return text


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value or "").strip().lower()
    return text in {"true", "yes", "y", "1", "accept", "accepted"}


def parse_score(value: Any) -> float:
    """兼容 8、8.0、"8/10"、"score: 8" 等常见评分输出。"""

    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value or ""))
    if not match:
        return 0.0
    return float(match.group(0))


def has_question_meta_expression(text: str) -> bool:
    """检查问题是否暴露 KB / evidence / profile 等元表述。"""

    lowered = str(text or "").lower()
    return any(re.search(pattern, lowered) for pattern in QUESTION_META_PATTERNS)


def has_answer_meta_expression(text: str) -> bool:
    """检查答案是否使用明显的“根据知识库/证据”类元表述。"""

    lowered = str(text or "").lower()
    return any(phrase in lowered for phrase in ANSWER_META_PHRASES)


def normalize_public_text(text: str) -> str:
    """把 runtime KB 的内部写法转成更适合公开 QA 的自然名称。"""

    normalized = str(text or "")
    for source, target in sorted(PUBLIC_TEXT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = re.sub(rf"\b{re.escape(source)}\b", target, normalized, flags=re.IGNORECASE)
    for pattern, replacement in PUBLIC_TEXT_REGEX_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    def confidence_label(match: re.Match[str]) -> str:
        value = float(match.group(1))
        label = "high" if value >= 0.9 else "moderate" if value >= 0.7 else "low"
        return f"{label} confidence"

    # 数值 confidence 是规则增强过程的实现痕迹；公开 QA 保留定性不确定性即可。
    normalized = re.sub(
        r"\b(?:the )?confidence(?: level)?(?: for (?:this )?(?:relation|counter))?\s+(?:is|of|at)\s*(0(?:\.\d+)?)\b",
        confidence_label,
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\bwith\s+(0(?:\.\d+)?)\s+confidence\b",
        lambda match: f"with {confidence_label(match)}",
        normalized,
        flags=re.IGNORECASE,
    )
    return " ".join(normalized.split())


def reject_internal_surface_form(question: str, answer: str) -> tuple[bool, str]:
    """检查公开问题/答案中是否仍残留 CamelCase、snake_case 或 profile/id 类内部标识。"""

    text = f"{question} {answer}"
    lowered = text.lower()
    for phrase in INTERNAL_SURFACE_PHRASES:
        if phrase in lowered:
            return True, phrase
    for term in INTERNAL_DIRECT_TERMS:
        if term in lowered:
            return True, term
    for match in SNAKE_CASE_RE.finditer(text):
        token = match.group(0)
        if token.lower() not in {"area_of_effect"}:
            return True, token
    for match in CAMEL_CASE_RE.finditer(text):
        token = match.group(0)
        if token not in INTERNAL_CAMEL_ALLOWLIST:
            return True, token
    return False, ""


def response_format_unsupported(exc: Exception) -> bool:
    """只在接口明确不支持 JSON response_format 时降级，避免超时后再发第二个慢请求。"""

    text = str(exc).lower()
    if "json mode is not supported" in text or "code': 20024" in text or '"code": 20024' in text:
        return True
    return "response_format" in text and any(token in text for token in ["unsupported", "not support", "invalid", "unknown"])


def add_quality_issue(kb: RuntimeKB, issue_type: str, object_id: str, detail: str) -> None:
    """记录 QA 质量门禁发现的问题，避免直接修改 runtime KB 原始文件。"""

    kb.quality_issues.append({"issue_type": issue_type, "object_id": object_id, "detail": detail})
    kb.quality_counts[issue_type] = kb.quality_counts.get(issue_type, 0) + 1


def audit_runtime_kb(kb: RuntimeKB) -> None:
    """在生成 QA 前隔离重复主键、损坏文本和已确认的跨单位错配。"""

    entity_counts = Counter(str(row.get("entity_id") or "") for row in kb.entity_profiles)
    ability_counts = Counter(str(row.get("ability_id") or "") for row in kb.ability_profiles)

    for entity_id, count in entity_counts.items():
        if entity_id and count > 1:
            kb.blocked_entity_ids.add(entity_id)
            add_quality_issue(kb, "duplicate_entity_id", entity_id, f"appears {count} times")
    for ability_id, count in ability_counts.items():
        if ability_id and count > 1:
            kb.blocked_ability_ids.add(ability_id)
            add_quality_issue(kb, "duplicate_ability_id", ability_id, f"appears {count} times")

    for entity_id in sorted(KNOWN_BLOCKED_ENTITY_IDS):
        if entity_id in kb.entity_by_id:
            kb.blocked_entity_ids.add(entity_id)
            add_quality_issue(kb, "known_corrupted_entity", entity_id, "quarantined after pilot audit")
    for ability_id in sorted(KNOWN_BLOCKED_ABILITY_IDS):
        if ability_id in kb.ability_by_id:
            kb.blocked_ability_ids.add(ability_id)
            add_quality_issue(kb, "known_corrupted_ability", ability_id, "quarantined after pilot audit")

    for ability in kb.ability_profiles:
        ability_id = str(ability.get("ability_id") or "")
        owner_id = str((ability.get("owner") or {}).get("entity_id") or "")
        effect_text = str((ability.get("base_ability") or {}).get("effect_text") or "")
        if owner_id not in kb.entity_by_id:
            kb.blocked_ability_ids.add(ability_id)
            add_quality_issue(kb, "ability_owner_unresolved", ability_id, owner_id or "missing owner")
        if any(re.search(pattern, effect_text, flags=re.IGNORECASE) for pattern in DAMAGED_TEXT_PATTERNS):
            kb.blocked_ability_ids.add(ability_id)
            add_quality_issue(kb, "damaged_ability_text", ability_id, compact(effect_text, 120))

    # 被隔离实体的技能也不能绕过 owner 再进入 QA。
    for ability in kb.ability_profiles:
        ability_id = str(ability.get("ability_id") or "")
        owner_id = str((ability.get("owner") or {}).get("entity_id") or "")
        if owner_id in kb.blocked_entity_ids:
            kb.blocked_ability_ids.add(ability_id)
            add_quality_issue(kb, "blocked_ability_owner", ability_id, owner_id)

    for row in kb.entity_profiles:
        if row.get("entity_id") in kb.blocked_entity_ids and row.get("profile_id"):
            kb.blocked_profile_ids.add(str(row["profile_id"]))
    for row in kb.ability_profiles:
        if row.get("ability_id") in kb.blocked_ability_ids and row.get("profile_id"):
            kb.blocked_profile_ids.add(str(row["profile_id"]))


def entity_is_qa_eligible(kb: RuntimeKB, row: dict[str, Any] | None) -> bool:
    return bool(row and row.get("entity_id") and row.get("entity_id") not in kb.blocked_entity_ids)


def ability_is_qa_eligible(kb: RuntimeKB, row: dict[str, Any] | None) -> bool:
    if not row or row.get("ability_id") in kb.blocked_ability_ids:
        return False
    return entity_is_qa_eligible(kb, related_entity_profile(kb, (row.get("owner") or {}).get("entity_id")))


def load_runtime_kb(runtime_dir: Path) -> RuntimeKB:
    kb = RuntimeKB(
        rag_documents=read_jsonl(runtime_dir / "rag_documents.jsonl"),
        entity_profiles=read_jsonl(runtime_dir / "entity_profiles.jsonl"),
        ability_profiles=read_jsonl(runtime_dir / "ability_profiles.jsonl"),
        relation_profiles=read_jsonl(runtime_dir / "relation_profiles.jsonl"),
        scenario_profiles=read_jsonl(runtime_dir / "scenario_profiles.jsonl"),
    )
    for row in [*kb.entity_profiles, *kb.ability_profiles, *kb.relation_profiles, *kb.scenario_profiles]:
        profile_id = row.get("profile_id")
        if profile_id:
            kb.profiles_by_id[profile_id] = row
    kb.entity_by_id = {row.get("entity_id", ""): row for row in kb.entity_profiles if row.get("entity_id")}
    kb.ability_by_id = {row.get("ability_id", ""): row for row in kb.ability_profiles if row.get("ability_id")}
    audit_runtime_kb(kb)
    return kb


def summarize_entity(row: dict[str, Any]) -> dict[str, Any]:
    """将实体 profile 拆成显式事实与规则增强提示，避免两者在 prompt 中混为一谈。"""

    identity = row.get("identity") or {}
    attrs = row.get("attributes") or {}
    enrich = row.get("local_enrichment") or {}
    tactical = row.get("tactical_profile") or {}
    costs = row.get("costs") or []
    abilities = row.get("abilities") or []
    return {
        "profile_type": "entity_profile",
        "name": identity.get("name"),
        "race": identity.get("race"),
        "entity_type": identity.get("entity_type"),
        "explicit_facts": {
            "target": attrs.get("target", []),
            "target_self": attrs.get("target_self", []),
            "type_self": attrs.get("type_self", []),
            "type_anti": attrs.get("type_anti", []),
            "survival": attrs.get("survival", {}),
            "weapons": [
                {
                    "target": item.get("target", []),
                    "attack": item.get("attack"),
                    "attack_bonus": item.get("attack_bonus"),
                    "anti_type": item.get("anti_type", []),
                    "attack_range": item.get("attack_range"),
                    "cooldown": item.get("cooldown"),
                }
                for item in (attrs.get("weapons") or [])[:2]
            ],
            "costs": [
                {
                    "mineral": item.get("mineral"),
                    "gas": item.get("gas"),
                    "supply": item.get("supply"),
                    "produce_time": item.get("produce_time"),
                    "produce_from": item.get("produce_from_entity_ids") or item.get("produce_from"),
                }
                for item in costs[:2]
            ],
            "abilities": [
                {"ability_name": item.get("ability_name"), "effect_text": compact(item.get("effect_text"), 180)}
                for item in abilities[:3]
            ],
            "tech_tree": row.get("tech_tree") or {},
            "action_conditions": (row.get("action_conditions") or [])[:4],
            "upgrades": (row.get("upgrades") or [])[:4],
        },
        "derived_hints": {
            "combat_roles": enrich.get("combat_roles", []),
            "strengths": enrich.get("strengths", []),
            "weaknesses": enrich.get("weaknesses", []),
            "scenario_tags": enrich.get("scenario_tags", []),
            "micro_notes": tactical.get("micro_notes", [])[:4],
        },
    }


def summarize_ability(row: dict[str, Any]) -> dict[str, Any]:
    """技能的原始效果与规则推导效果分层返回，防止推导标签变成确定机制。"""

    owner = row.get("owner") or {}
    base = row.get("base_ability") or {}
    enrich = row.get("local_enrichment") or {}
    return {
        "profile_type": "ability_profile",
        "ability_name": row.get("ability_name"),
        "owner": owner.get("name") or owner.get("entity_id"),
        "owner_race": owner.get("race"),
        "explicit_facts": {
            "base_effect": compact(base.get("effect_text") or base.get("text"), 320),
            "metrics": base.get("metrics", {}),
        },
        "derived_hints": {
            "ability_effects": enrich.get("ability_effects", []),
            "constraints": enrich.get("constraints", []),
            "scenario_tags": enrich.get("scenario_tags", []),
        },
    }


def summarize_relation(row: dict[str, Any]) -> dict[str, Any]:
    """关系 profile 一律视为条件线索，而非可直接断言的游戏真值。"""

    source = row.get("source") or {}
    target = row.get("target") or {}
    return {
        "profile_type": "relation_profile",
        "conditional_relation": {
            "relation": row.get("relation"),
            "relation_layer": row.get("relation_layer"),
            "confidence": row.get("confidence"),
            "source_name": source.get("name") or source.get("entity_id"),
            "source_types": source.get("type_self", []),
            "target_name": target.get("name") or target.get("entity_id") or target.get("target_type"),
            "target_types": target.get("type_self", []),
            "basis": compact(row.get("basis") or row.get("reason") or row.get("text"), 320),
        },
    }


def summarize_scenario(row: dict[str, Any]) -> dict[str, Any]:
    """场景标签仅提供检索和提问上下文，不能单独证明单位机制或战术结果。"""

    entities = row.get("matched_entities") or []
    abilities = row.get("matched_abilities") or []
    relations = row.get("matched_relations") or []
    return {
        "profile_type": "scenario_profile",
        "scenario_context": {
            "scenario_tag": row.get("scenario_tag"),
            "description": compact(row.get("description") or row.get("text"), 260),
            "trigger_roles": row.get("trigger_roles", []),
            "trigger_effects": row.get("trigger_effects", []),
            "recommended_kbs": row.get("recommended_kbs", []),
            "matched_entities": entities[:6],
            "matched_abilities": abilities[:6],
            "matched_relation_count": len(relations),
        },
    }


def summarize_profile(row: dict[str, Any]) -> dict[str, Any]:
    profile_type = row.get("profile_type")
    if profile_type == "entity_profile":
        return summarize_entity(row)
    if profile_type == "ability_profile":
        return summarize_ability(row)
    if profile_type == "relation_profile":
        return summarize_relation(row)
    if profile_type == "scenario_profile":
        return summarize_scenario(row)
    return {"profile_type": profile_type, "text": compact(row.get("text"), 400)}


def make_claim(
    source_profile_id: str,
    subject_id: str,
    subject_name: str,
    field_path: str,
    predicate: str,
    value: Any,
    *,
    evidence_layer: str = EVIDENCE_LAYER_EXPLICIT,
) -> dict[str, Any]:
    """把 profile 字段转换成可追踪的最小 claim，供复杂度构造和 validator 使用。"""

    safe_path = re.sub(r"[^a-z0-9]+", "_", field_path.lower()).strip("_")
    return {
        "claim_id": f"{subject_id}::{safe_path}",
        "source_profile_id": source_profile_id,
        "subject_id": subject_id,
        "subject_name": subject_name,
        "field_path": field_path,
        "predicate": predicate,
        "value": value,
        "evidence_layer": evidence_layer,
        "quality_status": QUALITY_VERIFIED,
    }


def entity_claims(kb: RuntimeKB, row: dict[str, Any]) -> list[dict[str, Any]]:
    """从实体 profile 提取原子事实；已隔离技能不会随实体再次进入证据包。"""

    if not entity_is_qa_eligible(kb, row):
        return []
    identity = row.get("identity") or {}
    attrs = row.get("attributes") or {}
    entity_id = str(row.get("entity_id") or "")
    if entity_id in kb.entity_claim_cache:
        return kb.entity_claim_cache[entity_id]
    profile_id = str(row.get("profile_id") or f"entity_profile_{entity_id}")
    name = str(identity.get("name") or entity_id)
    claims: list[dict[str, Any]] = []

    for metric, value in (attrs.get("survival") or {}).items():
        if value is not None:
            claims.append(make_claim(profile_id, entity_id, name, f"attributes.survival.{metric}", metric, value))
    if attrs.get("energy") not in (None, 0):
        claims.append(make_claim(profile_id, entity_id, name, "attributes.energy", "energy", attrs.get("energy")))
    for field_name in ["target", "target_self", "type_self"]:
        value = attrs.get(field_name) or []
        if value:
            claims.append(make_claim(profile_id, entity_id, name, f"attributes.{field_name}", field_name, value))
    for index, weapon in enumerate(attrs.get("weapons") or []):
        if not weapon or not weapon.get("target"):
            continue
        value = {
            "target": weapon.get("target") or [],
            "damage": weapon.get("attack"),
            "bonus_damage": weapon.get("attack_bonus"),
            "bonus_against": weapon.get("anti_type") or [],
            "range": weapon.get("attack_range"),
            "cooldown": weapon.get("cooldown"),
        }
        claims.append(make_claim(profile_id, entity_id, name, f"attributes.weapons[{index}]", "weapon", value))
    for index, cost in enumerate(row.get("costs") or []):
        value = {
            "minerals": cost.get("mineral"),
            "gas": cost.get("gas"),
            "supply": cost.get("supply"),
            "production_time": cost.get("produce_time"),
            "produced_from_entity_ids": cost.get("produce_from_entity_ids") or [],
        }
        claims.append(make_claim(profile_id, entity_id, name, f"costs[{index}]", "production_cost", value))
    for index, ability in enumerate(row.get("abilities") or []):
        if ability.get("ability_id") in kb.blocked_ability_ids:
            continue
        if ability.get("effect_text"):
            claims.append(
                make_claim(
                    profile_id,
                    entity_id,
                    name,
                    f"abilities[{index}]",
                    "ability",
                    {"name": ability.get("ability_name"), "effect": compact(ability.get("effect_text"), 260)},
                )
            )
    for index, edge in enumerate((row.get("tech_tree") or {}).get("incoming_edges") or []):
        head = str(edge.get("head") or "")
        if head and head not in kb.blocked_entity_ids and edge.get("relation"):
            claims.append(
                make_claim(
                    profile_id,
                    entity_id,
                    name,
                    f"tech_tree.incoming_edges[{index}]",
                    "incoming_tech_edge",
                    {"head_entity_id": head, "relation": edge.get("relation"), "tail_entity_id": edge.get("tail")},
                )
            )
    # 同一个 profile 会被多个 packet builder 重复访问，缓存可显著降低批量生成开销。
    unique_claims = {claim["claim_id"]: claim for claim in claims}
    kb.entity_claim_cache[entity_id] = list(unique_claims.values())
    return kb.entity_claim_cache[entity_id]


def explicit_activation_constraints(effect: str) -> list[str]:
    """从技能原文提取明确限制，避免把“always available”误读成额外推断。"""

    lowered = effect.lower()
    constraints: list[str] = []
    if re.search(r"\b(?:cost|costs)\b[^.]{0,80}\b\d+(?:\.\d+)?\s+energy\b|\b\d+(?:\.\d+)?\s+energy\b[^.]{0,40}\b(?:cost|costs)\b", lowered):
        constraints.append("energy_cost")
    if re.search(r"\b(?:cooldown|cool down)\b", lowered):
        constraints.append("cooldown")
    if re.search(r"\b(?:requires|require|only be used|can only|must be|only while|after researching)\b", lowered):
        constraints.append("state_or_prerequisite")
    if re.search(r"\b(?:target|range|within)\b", lowered):
        constraints.append("target_or_range")
    return constraints


def ability_claims(kb: RuntimeKB, row: dict[str, Any]) -> list[dict[str, Any]]:
    """技能 claim 只保留显式 effect_text 和 metrics，不使用规则推导效果。"""

    if not ability_is_qa_eligible(kb, row):
        return []
    ability_id = str(row.get("ability_id") or "")
    if ability_id in kb.ability_claim_cache:
        return kb.ability_claim_cache[ability_id]
    profile_id = str(row.get("profile_id") or f"ability_profile_{ability_id}")
    ability_name = str(row.get("ability_name") or ability_id)
    owner = row.get("owner") or {}
    base = row.get("base_ability") or {}
    effect = compact(base.get("effect_text") or base.get("text"), 420)
    if not effect:
        return []
    constraints = explicit_activation_constraints(effect)
    kb.ability_claim_cache[ability_id] = [
        make_claim(
            profile_id,
            ability_id,
            ability_name,
            "base_ability",
            "ability_effect",
            {
                "owner_entity_id": owner.get("entity_id"),
                "owner_name": owner.get("name"),
                "effect": effect,
                "metrics": base.get("metrics") or {},
                # 只保存文本中明确写出的限制；"always available" 不代表没有资源或状态条件。
                "explicit_activation_constraints": constraints,
            },
        )
    ]
    return kb.ability_claim_cache[ability_id]


def claim_item(role: str, claim: dict[str, Any], *, context_only: bool = False) -> dict[str, Any]:
    return {
        "role": role,
        "evidence_layer": claim.get("evidence_layer", EVIDENCE_LAYER_EXPLICIT),
        "context_only": context_only,
        "claims": [claim],
    }


def doc_source_profile(kb: RuntimeKB, doc: dict[str, Any]) -> dict[str, Any] | None:
    return kb.profiles_by_id.get(doc.get("source_profile_id", ""))


def related_entity_profile(kb: RuntimeKB, entity_id: str | None) -> dict[str, Any] | None:
    if not entity_id:
        return None
    return kb.entity_by_id.get(entity_id)


def profile_id_values(items: Any, key: str) -> set[str]:
    values: set[str] = set()
    for item in as_list(items):
        if isinstance(item, dict) and item.get(key):
            values.add(str(item[key]))
        elif isinstance(item, str):
            values.add(item)
    return values


def combat_weapons_against_target(source: dict[str, Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    """返回能实际攻击目标层级的武器；不再信任可能过度聚合的实体级 target 字段。"""

    target_layers = set((target.get("attributes") or {}).get("target_self") or [])
    if not target_layers:
        return []
    return [
        weapon
        for weapon in ((source.get("attributes") or {}).get("weapons") or [])
        if weapon.get("attack") not in (None, 0)
        and target_layers.intersection(set(weapon.get("target") or []))
    ]


def entity_targeting_is_weapon_consistent(entity: dict[str, Any]) -> bool:
    """核对单位级攻击目标与有效武器目标，防止二者冲突时生成自相矛盾的公开问答。"""

    declared_targets = set((entity.get("attributes") or {}).get("target") or [])
    weapon_targets = {
        layer
        for weapon in ((entity.get("attributes") or {}).get("weapons") or [])
        if weapon.get("attack") not in (None, 0)
        for layer in (weapon.get("target") or [])
    }
    # 非战斗实体没有可比较的攻击目标；这里只限制同时声明了两类信息的战斗单位。
    return not declared_targets or not weapon_targets or declared_targets == weapon_targets


def relation_is_gameplay_plausible(kb: RuntimeKB, relation: dict[str, Any], allow_structure_targets: bool = False) -> bool:
    """只保留可由具体武器攻击到目标、且端点可回连的关系，避免伪反制结论。"""

    source_id = (relation.get("source") or {}).get("entity_id")
    target_id = (relation.get("target") or {}).get("entity_id")
    source = related_entity_profile(kb, source_id)
    target = related_entity_profile(kb, target_id)
    if not entity_is_qa_eligible(kb, source) or not entity_is_qa_eligible(kb, target):
        return False

    # 聚合 target 与某把武器可能冲突，例如实体称可对空、具体武器却只能对地。
    # 反制链必须以具体、可造成伤害的武器为准。
    if not combat_weapons_against_target(source, target):
        return False

    target_type = (target.get("identity") or {}).get("entity_type")
    return allow_structure_targets or target_type == "unit"


def eligible_relation_profiles(kb: RuntimeKB, allow_structure_targets: bool = False) -> list[dict[str, Any]]:
    if allow_structure_targets in kb.relation_candidate_cache:
        return kb.relation_candidate_cache[allow_structure_targets]
    kb.relation_candidate_cache[allow_structure_targets] = [
        row
        for row in kb.relation_profiles
        if relation_is_gameplay_plausible(kb, row, allow_structure_targets=allow_structure_targets)
    ]
    return kb.relation_candidate_cache[allow_structure_targets]


def evidence_item(
    role: str,
    summary: dict[str, Any],
    evidence_layer: str,
    *,
    context_only: bool = False,
    doc_type: str | None = None,
) -> dict[str, Any]:
    """按证据层向模型暴露最小必要摘要，避免推导提示污染显式事实。"""

    profile = {
        key: value
        for key, value in summary.items()
        if key not in {"explicit_facts", "derived_hints", "conditional_relation", "scenario_context"}
    }
    if evidence_layer == EVIDENCE_LAYER_EXPLICIT:
        profile["explicit_facts"] = summary.get("explicit_facts", {})
    elif evidence_layer == EVIDENCE_LAYER_CONDITIONAL:
        profile["conditional_relation"] = summary.get("conditional_relation", {})
    elif evidence_layer == EVIDENCE_LAYER_DERIVED:
        profile["derived_hints"] = summary.get("derived_hints", summary.get("scenario_context", {}))
    else:
        raise ValueError(f"Unknown evidence layer: {evidence_layer}")
    item: dict[str, Any] = {
        "role": role,
        "evidence_layer": evidence_layer,
        "context_only": context_only,
        "profile": profile,
    }
    if doc_type:
        item["doc_type"] = doc_type
    return item


def relation_item(relation: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        **evidence_item(role, summarize_relation(relation), EVIDENCE_LAYER_CONDITIONAL),
        "caution": "This is a potentially useful relation, not a guaranteed game outcome.",
    }


def relation_claim(relation: dict[str, Any]) -> dict[str, Any]:
    source = relation.get("source") or {}
    target = relation.get("target") or {}
    relation_id = str(relation.get("relation_id") or relation.get("profile_id") or "relation")
    return make_claim(
        str(relation.get("profile_id") or relation_id),
        relation_id,
        f"{source.get('name') or source.get('entity_id')} -> {target.get('name') or target.get('entity_id')}",
        "conditional_relation",
        "potential_matchup",
        {
            "source_entity_id": source.get("entity_id"),
            "source_name": source.get("name") or source.get("entity_id"),
            "target_entity_id": target.get("entity_id"),
            "target_name": target.get("name") or target.get("entity_id"),
            "relation": relation.get("relation"),
            "basis": compact(relation.get("basis") or relation.get("reason") or relation.get("text"), 260),
            "relation_layer": relation.get("relation_layer"),
        },
        evidence_layer=EVIDENCE_LAYER_CONDITIONAL,
    )


def packet_claim_ids(items: list[dict[str, Any]]) -> list[str]:
    return [
        str(claim.get("claim_id"))
        for item in items
        for claim in item.get("claims") or []
        if claim.get("claim_id")
    ]


def entity_identity_claim(kb: RuntimeKB, entity_id: str) -> dict[str, Any] | None:
    """为科技链补充实体显示名；该 claim 只用于连接 ID 与可读答案。"""

    entity = related_entity_profile(kb, entity_id)
    if not entity_is_qa_eligible(kb, entity):
        return None
    identity = entity.get("identity") or {}
    return make_claim(
        str(entity.get("profile_id") or f"entity_profile_{entity_id}"),
        entity_id,
        str(identity.get("name") or entity_id),
        "identity.name",
        "identity",
        {"name": identity.get("name"), "entity_type": identity.get("entity_type"), "race": identity.get("race")},
    )


AUTO_TRUSTED_TECH_RELATION = "requires_building"


def normalize_tech_edge(edge: dict[str, Any]) -> dict[str, str] | None:
    """把明确的建筑前置边统一为 prerequisite -> dependent。

    静态表的 unlock、unit prerequisite 与生产来源字段混有大量推导关系；第一版公开
    QA 只使用 `requires_building`，以高精度换取较少但结构更可靠的科技链。
    """

    relation = str(edge.get("relation") or "")
    head = str(edge.get("head") or "")
    tail = str(edge.get("tail") or "")
    if not head or not tail or head == tail:
        return None
    if relation != AUTO_TRUSTED_TECH_RELATION:
        return None
    prerequisite_id, dependent_id = tail, head
    return {
        "edge_id": str(edge.get("edge_id") or f"{relation}:{head}:{tail}"),
        "relation": relation,
        "prerequisite_entity_id": prerequisite_id,
        "dependent_entity_id": dependent_id,
    }


def is_auto_trusted_building_edge(
    prerequisite: dict[str, Any],
    dependent: dict[str, Any],
    raw_edge: dict[str, Any],
) -> bool:
    """自动筛选结构一致的建筑前置边，不依赖人工了解具体游戏规则。"""

    prerequisite_identity = prerequisite.get("identity") or {}
    dependent_identity = dependent.get("identity") or {}
    prerequisite_type = str(prerequisite_identity.get("entity_type") or "").lower()
    dependent_type = str(dependent_identity.get("entity_type") or "").lower()
    prerequisite_race = str(prerequisite_identity.get("race") or "").lower()
    dependent_race = str(dependent_identity.get("race") or "").lower()
    return bool(
        raw_edge.get("source_field") == "require_building"
        and prerequisite_type == "building"
        and dependent_type in {"building", "unit"}
        and prerequisite_race
        and prerequisite_race == dependent_race
    )


def normalized_tech_edge_claims(kb: RuntimeKB) -> list[dict[str, Any]]:
    """只读取通过自动结构审计的建筑前置边，生成可追溯 claim。"""

    claims: list[dict[str, Any]] = []
    seen_edge_ids: set[str] = set()
    for entity in kb.entity_profiles:
        for edge in ((entity.get("tech_tree") or {}).get("incoming_edges") or []):
            normalized = normalize_tech_edge(edge)
            if not normalized or normalized["edge_id"] in seen_edge_ids:
                continue
            seen_edge_ids.add(normalized["edge_id"])
            prerequisite = related_entity_profile(kb, normalized["prerequisite_entity_id"])
            dependent = related_entity_profile(kb, normalized["dependent_entity_id"])
            if not entity_is_qa_eligible(kb, prerequisite) or not entity_is_qa_eligible(kb, dependent):
                continue
            if not is_auto_trusted_building_edge(prerequisite, dependent, edge):
                continue
            dependent_identity = dependent.get("identity") or {}
            claims.append(
                make_claim(
                    str(dependent.get("profile_id") or f"entity_profile_{normalized['dependent_entity_id']}"),
                    normalized["dependent_entity_id"],
                    str(dependent_identity.get("name") or normalized["dependent_entity_id"]),
                    f"tech_tree.edge[{normalized['edge_id']}]",
                    "tech_prerequisite",
                    normalized,
                )
            )
    return claims


def single_atomic_claims(kb: RuntimeKB) -> list[dict[str, Any]]:
    """把复合武器/成本字段拆成单值事实，保证 single_hop 只考察一个事实点。"""

    atomic: list[dict[str, Any]] = []
    for entity in kb.entity_profiles:
        for claim in entity_claims(kb, entity):
            predicate = str(claim.get("predicate") or "")
            if predicate in {"health", "shield", "armor", "speed"}:
                atomic.append(claim)
            elif predicate == "target" and len(claim.get("value") or []) == 1:
                atomic.append(claim)
            elif predicate == "weapon":
                value = claim.get("value") or {}
                for key, label in [("damage", "weapon_damage"), ("range", "weapon_range"), ("cooldown", "weapon_cooldown")]:
                    if value.get(key) is not None:
                        atomic.append(
                            make_claim(
                                claim["source_profile_id"],
                                claim["subject_id"],
                                claim["subject_name"],
                                f"{claim['field_path']}.{key}",
                                label,
                                value[key],
                            )
                        )
                if value.get("bonus_damage") not in (None, 0) and len(value.get("bonus_against") or []) == 1:
                    atomic.append(
                        make_claim(
                            claim["source_profile_id"],
                            claim["subject_id"],
                            claim["subject_name"],
                            f"{claim['field_path']}.bonus_damage",
                            "weapon_bonus_damage",
                            {"damage": value["bonus_damage"], "against": value["bonus_against"][0]},
                        )
                    )
            elif predicate == "production_cost":
                for key, label in [
                    ("minerals", "mineral_cost"),
                    ("gas", "gas_cost"),
                    ("supply", "supply_cost"),
                    ("production_time", "production_time"),
                ]:
                    value = (claim.get("value") or {}).get(key)
                    if value is not None:
                        atomic.append(
                            make_claim(
                                claim["source_profile_id"],
                                claim["subject_id"],
                                claim["subject_name"],
                                f"{claim['field_path']}.{key}",
                                label,
                                value,
                            )
                        )
    for ability in kb.ability_profiles:
        for claim in ability_claims(kb, ability):
            effect = str((claim.get("value") or {}).get("effect") or "")
            # 只接受不包含多个条件、数值分支或并列机制的简洁技能效果。
            if len(effect.split()) <= 28 and not re.search(r"\b(?:also|after|while|requires|cooldown|cost)\b", effect, re.IGNORECASE):
                atomic.append(claim)
    return atomic


def tech_edge_claims(kb: RuntimeKB, entity: dict[str, Any], relations: set[str]) -> list[dict[str, Any]]:
    return [
        claim
        for claim in entity_claims(kb, entity)
        if claim.get("predicate") == "incoming_tech_edge"
        and str((claim.get("value") or {}).get("relation") or "") in relations
    ]


def scenario_entity_ids(scenario: dict[str, Any]) -> set[str]:
    return profile_id_values(scenario.get("matched_entities"), "entity_id")


def scenario_ability_ids(scenario: dict[str, Any]) -> set[str]:
    return profile_id_values(scenario.get("matched_abilities"), "ability_id")


def ability_matches_scenario(ability: dict[str, Any], scenario: dict[str, Any], entity_ids: set[str], ability_ids: set[str]) -> bool:
    owner_id = (ability.get("owner") or {}).get("entity_id")
    ability_id = ability.get("ability_id")
    scenario_tags = set((ability.get("local_enrichment") or {}).get("scenario_tags") or [])
    return bool(
        owner_id in entity_ids
        or ability_id in ability_ids
        or scenario.get("scenario_tag") in scenario_tags
    )


def relation_matches_scenario(relation: dict[str, Any], entity_ids: set[str]) -> bool:
    source_id = (relation.get("source") or {}).get("entity_id")
    target_id = (relation.get("target") or {}).get("entity_id")
    return source_id in entity_ids or target_id in entity_ids


def build_single_hop_packet(kb: RuntimeKB, rng: random.Random) -> dict[str, Any]:
    """单跳只给模型一个 verified claim，防止答案顺手扩写整份 profile。"""

    candidates = single_atomic_claims(kb)
    if not candidates:
        raise ValueError("No verified claims are available for single_hop generation")
    claim = rng.choice(candidates)
    items = [claim_item("primary_claim", claim)]
    return {
        "target_complexity": "single_hop",
        "packet_type": "single_verified_claim",
        "required_claim_ids": packet_claim_ids(items),
        "evidence_items": items,
    }


def build_two_hop_packet(kb: RuntimeKB, rng: random.Random) -> dict[str, Any]:
    """双跳只使用技能与所属实体的显式属性，不再生成策略性反制结论。"""

    ability_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for ability in kb.ability_profiles:
        ability_rows = ability_claims(kb, ability)
        owner = related_entity_profile(kb, (ability.get("owner") or {}).get("entity_id"))
        owner_rows = [
            claim
            for claim in entity_claims(kb, owner or {})
            if claim.get("predicate") in {"health", "shield", "armor", "target", "weapon", "production_cost"}
        ]
        if ability_rows and owner_rows:
            ability_pairs.append((ability_rows[0], rng.choice(owner_rows)))

    if ability_pairs:
        first, second = rng.choice(ability_pairs)
        packet_type = "ability_owner_attribute"
    else:
        raise ValueError("No connected two-hop claim pair is available")

    items = [claim_item("first_hop", first), claim_item("second_hop", second)]
    packet = {
        "target_complexity": "two_hop",
        "packet_type": packet_type,
        "required_claim_ids": packet_claim_ids(items),
        "chain_edges": [{"from": first["claim_id"], "to": second["claim_id"], "relation": "directly_connected"}],
        "evidence_items": items,
    }
    return packet


def build_multi_hop_packet(kb: RuntimeKB, rng: random.Random) -> dict[str, Any]:
    """从自动审计通过的建筑前置边构造多跳问题，不使用克制关系或单位解锁建筑。"""

    production_chains: list[list[dict[str, Any]]] = []
    building_chains: list[list[dict[str, Any]]] = []
    normalized_edges = normalized_tech_edge_claims(kb)
    for entity in kb.entity_profiles:
        if not entity_is_qa_eligible(kb, entity):
            continue
        for cost_claim in [claim for claim in entity_claims(kb, entity) if claim.get("predicate") == "production_cost"]:
            producer_ids = (cost_claim.get("value") or {}).get("produced_from_entity_ids") or []
            for producer_id in producer_ids:
                producer = related_entity_profile(kb, str(producer_id))
                # 建筑链只追踪由建筑生产的对象；Probe、SCV、Larva 等来源另作生产事实处理。
                if str(((producer or {}).get("identity") or {}).get("entity_type") or "").lower() != "building":
                    continue
                for producer_edge in normalized_edges:
                    edge_value = producer_edge.get("value") or {}
                    # 只有“producer 的前置”才能接在“entity 由 producer 生产”之后。
                    if str(edge_value.get("dependent_entity_id") or "") != str(producer_id):
                        continue
                    prerequisite_id = str(edge_value.get("prerequisite_entity_id") or "")
                    identity = entity_identity_claim(kb, prerequisite_id)
                    if identity:
                        production_chains.append([cost_claim, producer_edge, identity])

    for downstream_edge in normalized_edges:
        downstream_value = downstream_edge.get("value") or {}
        prerequisite_id = str(downstream_value.get("prerequisite_entity_id") or "")
        for upstream_edge in normalized_edges:
            upstream_value = upstream_edge.get("value") or {}
            # 两条边必须共享中间建筑，形成连续的 building -> building -> dependent 路径。
            if str(upstream_value.get("dependent_entity_id") or "") != prerequisite_id:
                continue
            root_id = str(upstream_value.get("prerequisite_entity_id") or "")
            identity = entity_identity_claim(kb, root_id)
            if identity:
                building_chains.append([downstream_edge, upstream_edge, identity])

    available_templates: list[tuple[str, list[list[dict[str, Any]]], str]] = []
    if production_chains:
        available_templates.append(
            ("production_tech_chain", production_chains, "Explain only the recorded building production route and prerequisite chain.")
        )
    if building_chains:
        available_templates.append(
            ("building_tech_chain", building_chains, "Explain only the connected building prerequisite chain in the supplied direction.")
        )
    if not available_templates:
        raise ValueError("No connected multi-hop claim chain is available")
    packet_type, candidate_chains, caution = rng.choice(available_templates)
    claims = rng.choice(candidate_chains)

    items = [claim_item(f"hop_{index}", claim) for index, claim in enumerate(claims, start=1)]
    packet = {
        "target_complexity": "multi_hop",
        "packet_type": packet_type,
        "required_claim_ids": packet_claim_ids(items),
        "chain_edges": [
            {"from": claims[0]["claim_id"], "to": claims[1]["claim_id"], "relation": "supports_next_hop"},
            {"from": claims[1]["claim_id"], "to": claims[2]["claim_id"], "relation": "supports_final_conclusion"},
        ],
        "all_hops_required": True,
        "evidence_items": items,
    }
    packet["chain_caution"] = caution
    return packet


def build_ambiguous_packet(
    kb: RuntimeKB,
    rng: random.Random,
) -> dict[str, Any]:
    """构造技能条件或目标层级歧义，不再生成策略性反制问题。"""

    options: list[tuple[str, list[dict[str, Any]], str]] = []
    for ability in kb.ability_profiles:
        aclaims = ability_claims(kb, ability)
        owner = related_entity_profile(kb, (ability.get("owner") or {}).get("entity_id"))
        constraints = list((aclaims[0].get("value") or {}).get("explicit_activation_constraints") or []) if aclaims else []
        owner_claims = [claim for claim in entity_claims(kb, owner or {}) if claim.get("predicate") == "energy"]
        if aclaims and constraints:
            claims = [aclaims[0]]
            if "energy_cost" in constraints and owner_claims:
                claims.append(rng.choice(owner_claims))
            options.append(
                (
                    "activation_condition_ambiguity",
                    claims,
                    "Ask only about an activation restriction explicitly stated in the ability text. Do not infer hidden costs, cooldowns, prerequisites, or energy requirements from missing information or from an always-available label.",
                )
            )
    for entity in kb.entity_profiles:
        if not entity_targeting_is_weapon_consistent(entity):
            continue
        claims = entity_claims(kb, entity)
        target_claims = [claim for claim in claims if claim.get("predicate") == "target" and len(claim.get("value") or []) == 1]
        weapon_claims = [
            claim
            for claim in claims
            if claim.get("predicate") == "weapon"
            and set((claim.get("value") or {}).get("target") or []) == set(target_claims[0].get("value") or [])
        ] if target_claims else []
        if target_claims and weapon_claims:
            options.append(
                (
                    "target_applicability_ambiguity",
                    [target_claims[0], rng.choice(weapon_claims)],
                    "Ask whether the unit can attack an enemy when the target's ground-or-air layer is not specified. Explain the supported target layer and the condition that must be clarified. Do not ask about counter strength, combat advantage, or survival.",
                )
            )
    if not options:
        raise ValueError("No natural ambiguous claim packet is available")
    # 先按子类型均匀抽样，再选择具体对象，避免 relation 候选数量过多而垄断 ambiguous。
    options_by_type: dict[str, list[tuple[str, list[dict[str, Any]], str]]] = {}
    for option in options:
        options_by_type.setdefault(option[0], []).append(option)
    packet_type = rng.choice(sorted(options_by_type))
    _, claims, instruction = rng.choice(options_by_type[packet_type])
    items = [claim_item(f"ambiguity_fact_{index}", claim) for index, claim in enumerate(claims, start=1)]
    return {
        "target_complexity": "ambiguous",
        "packet_type": packet_type,
        "ambiguity_instruction": instruction,
        "ambiguity_type": packet_type,
        "requires_boundary_answer": True,
        "required_claim_ids": packet_claim_ids(items),
        "evidence_items": items,
    }


def build_evidence_packet(
    kb: RuntimeKB,
    complexity: str,
    seed: str,
) -> dict[str, Any]:
    rng = random.Random(seed)
    if complexity == "single_hop":
        return build_single_hop_packet(kb, rng)
    if complexity == "two_hop":
        return build_two_hop_packet(kb, rng)
    if complexity == "multi_hop":
        return build_multi_hop_packet(kb, rng)
    if complexity == "ambiguous":
        return build_ambiguous_packet(kb, rng)
    raise ValueError(f"Unknown evidence_complexity: {complexity}")


class OpenAICompatibleChat:
    def __init__(self, api_key: str, base_url: str, timeout: float = 90.0, api_retries: int = 1) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.api_retries = max(1, api_retries)
        self.failure_streak: dict[str, int] = {model: 0 for model in MODEL_POOL}
        self.no_json_mode_models: set[str] = set()

    def complete(self, model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float, json_mode: bool = True) -> str:
        # Pilot 批量生成更适合“失败换候选”，而不是在同一个慢请求上反复等待。
        for attempt in range(1, self.api_retries + 1):
            try:
                # 生成与验证阶段都要求结构化 JSON；若某个模型接口不支持 response_format，
                # 则退回普通 chat completion，仍由 prompt 和本地 JSON 抽取兜底。
                kwargs: dict[str, Any] = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                # Qwen reasoning 模型在部分接口上会先输出 reasoning_content，content 可能为空。
                # 关闭 thinking 后更适合本任务的严格 JSON 生成和验证。
                if "qwen" in model.lower():
                    kwargs["extra_body"] = {"enable_thinking": False}
                if json_mode and model not in self.no_json_mode_models:
                    kwargs["response_format"] = {"type": "json_object"}
                try:
                    response = self.client.chat.completions.create(**kwargs)
                except Exception as exc:
                    if not json_mode or not response_format_unsupported(exc):
                        raise
                    self.no_json_mode_models.add(model)
                    kwargs.pop("response_format", None)
                    response = self.client.chat.completions.create(**kwargs)
                self.failure_streak[model] = 0
                return (response.choices[0].message.content or "").strip()
            except Exception:
                self.failure_streak[model] = self.failure_streak.get(model, 0) + 1
                if self.failure_streak[model] >= 3:
                    raise RuntimeError(f"Model API failed three consecutive times: {model}") from None
                if attempt == self.api_retries:
                    raise
                time.sleep(1.5 * attempt)
        raise RuntimeError(f"Model API failed: {model}")


def generator_messages(complexity: str, evidence_packet: dict[str, Any]) -> list[dict[str, str]]:
    special_requirements = []
    if complexity == "single_hop":
        special_requirements.extend(
            [
                "For single_hop, answer only the requested claim. Use one or two concise sentences and do not add unrelated attributes from general game knowledge.",
            ]
        )
    if complexity == "multi_hop":
        special_requirements.extend(
            [
                "For multi_hop, combine multiple evidence items only when the answer needs them.",
                "For multi_hop, do not invent tactical synergy between separate evidence items.",
                "For multi_hop, if the facts are separate, present them as separate supported facts rather than claiming they work together.",
                "For multi_hop, only describe cooperation, combo value, or strategic interaction when it is explicitly supported by the provided facts.",
                "A scenario context may explain why the question is relevant, but it cannot by itself prove damage, range, area-of-effect, teleportation, mobility, or a combat outcome.",
                "Follow chain_edges in order. Every required_claim_id must be necessary for the final answer.",
                "Do not make arbitrary numeric comparisons across unrelated dimensions such as shields versus mineral cost.",
                "The question must express one connected reasoning task, not several independent questions joined with and.",
                "Follow chain_caution when it is present; do not convert a tech edge or conditional relation into an unsupported game fact.",
                "For building_tech_chain and production_tech_chain, describe only the supplied building prerequisite path; do not introduce unit morphs, unit unlockers, or extra buildings.",
            ]
        )
    if complexity == "ambiguous":
        special_requirements.extend(
            [
                "For ambiguous, the question should be naturally under-specified rather than impossible.",
                "For ambiguous, explain concrete gameplay branches or conditions instead of discussing missing records.",
                "Do not use phrases such as available facts, provided data, evidence, profile, field, database, or knowledge base.",
                "For ambiguous, do not force a best unit, best counter, exact ranking, or guaranteed outcome unless the facts explicitly establish it.",
                "Follow ambiguity_type exactly: activation_condition_ambiguity is about explicit activation conditions; target_applicability_ambiguity is about the target's ground-or-air layer.",
                "Do not ask about combat advantage, survival, or counter strength for activation_condition_ambiguity or target_applicability_ambiguity.",
                "For activation_condition_ambiguity, use only restrictions explicitly written in the supplied ability text. Never infer hidden costs, unstated cooldowns, or possible energy requirements.",
                "Do not repeat an always-available label in the public answer; explain the explicit cost, cooldown, target, state, or prerequisite instead.",
            ]
        )
    if evidence_packet.get("relation_caution"):
        special_requirements.extend(
            [
                "This packet contains a rule-derived relation. Describe it as potentially useful or conditionally favorable, never as a guaranteed counter.",
                "Do not expose implementation wording such as relation data, relation layer, source bonus type, target type profile, or numeric confidence values.",
            ]
        )
    system = (
        "You are constructing an English StarCraft II QA benchmark from a fixed set of field-level claims. "
        "Use only the claims in the input packet. Do not use external StarCraft II knowledge. "
        "Output exactly one JSON object with keys: question, reference_answer, evidence_complexity. "
        "Do not output Markdown, comments, or extra text."
    )
    user = {
        "target_evidence_complexity": complexity,
        "complexity_definitions": COMPLEXITY_DEFINITIONS,
        "requirements": [
            "question and reference_answer must be English.",
            "question must be answerable from the supplied claims.",
            "reference_answer must be supported by the supplied claims and must not invent units, numbers, or mechanisms.",
            "Every factual sentence must be supported by at least one required_claim_id, but never expose claim IDs or field paths in public text.",
            "Except for single_hop, reference_answer should contain two to four complete sentences.",
            "question must use natural StarCraft II wording and must not mention knowledge base, KB, evidence, evidence packet, profile, JSON, or field.",
            "Use natural public display names instead of internal names such as CamelCase unit IDs, snake_case relation IDs, or profile identifiers.",
            "reference_answer must not mention evidence, profiles, fields, data availability, claims, JSON, or a knowledge base.",
            "Each evidence item has an evidence_layer. Only explicit_fact may support definite mechanics, numbers, attack capabilities, skill effects, or production requirements.",
            "derived_hint is a rule-derived hint. It may provide background, candidate selection, or a qualified interpretation, but must never be rewritten as a definite game mechanic or tactical outcome.",
            "An item with context_only=true is contextual only and cannot by itself support a statement about damage, attack range, area-of-effect, teleportation, movement, or a unit's actual ability.",
            "conditional_relation may only support wording such as potentially, conditionally, or not guaranteed. It must never support best counter, guaranteed counter, will beat, or a certain outcome.",
            "Do not create a strategic matchup, counter, or combat-effectiveness conclusion. Describe only direct recorded attributes, costs, effects, targets, or prerequisites.",
            "Do not infer teleportation from a mobility hint, area-of-effect damage from a combat role, or multi-line attack from a scenario tag.",
            "Return the exact evidence_complexity label requested by target_evidence_complexity.",
        ] + special_requirements,
        "required_json_shape": {
            "question": "one English question",
            "reference_answer": "two to four English sentences grounded in the evidence_packet",
            "evidence_complexity": complexity,
        },
        "evidence_packet": evidence_packet,
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]


def validator_messages(candidate: dict[str, Any], evidence_packet: dict[str, Any]) -> list[dict[str, str]]:
    system = (
        "You are a strict validator for an English StarCraft II QA benchmark. "
        "Judge only from the provided evidence_packet. Do not use external StarCraft II knowledge. "
        "Output exactly one JSON object. Do not output Markdown, comments, or extra text."
    )
    user = {
        "complexity_definitions": COMPLEXITY_DEFINITIONS,
        "candidate": {
            "question": candidate.get("question"),
            "reference_answer": candidate.get("reference_answer"),
            "evidence_complexity": candidate.get("evidence_complexity"),
        },
        "evidence_packet": evidence_packet,
        "output_schema": {
            "answer_score": "0-10 score: does reference_answer correctly answer the question?",
            "groundedness_score": "0-10 score: is reference_answer supported by evidence_packet?",
            "complexity_confidence": "0-10 score: does the proposed evidence_complexity match the definitions?",
            "predicted_evidence_complexity": "single_hop | two_hop | multi_hop | ambiguous",
            "accept": "true only if the QA should be kept",
            "derived_hint_leak": "true only when the candidate turns derived_hint, conditional_relation, or context_only evidence into an unsupported definite game fact",
            "source_quality_valid": "true only if every used claim has quality_status=verified and the answer does not rely on a quarantined or damaged source",
            "all_sentences_supported": "true only if every factual sentence is supported by the supplied claims and no extra game fact is introduced",
            "evidence_chain_connected": "true only if the required claims form the chain declared by chain_edges; use true for single_hop",
            "all_hops_necessary": "true only if every required claim is needed to answer the question; use true for single_hop",
            "single_claim_focus_valid": "true only if a single_hop question and answer stay within exactly one atomic claim; use true for other complexity labels",
            "ambiguity_domain_valid": "true only if the ambiguous question matches its ambiguity_type and does not force a utility ability into a combat/counter/survival question; use true for other labels",
            "reason": "short English reason",
        },
        "important": [
            "Even when you reject the candidate, you must still output the complete JSON object.",
            "Use numeric scores, not prose labels.",
            "Use a JSON boolean for accept.",
            "Prefer candidates with natural StarCraft II wording; questions should not mention knowledge base, KB, evidence, profile, JSON, or field.",
            "Answers should avoid obvious meta phrasing such as according to the knowledge base or the evidence indicates.",
            "Reject any public text containing evidence, profile, field, available facts, provided data, target list, explicit facts, or scenario context.",
            "Reject candidates that expose internal CamelCase names, snake_case relation names, or profile/id-like implementation terms when a natural public name should be used.",
            "Reject candidates that turn a potentially strong or rule-derived relation into a guaranteed counter claim.",
            "Only explicit_fact evidence can support a definite mechanic, number, attack capability, production requirement, or skill effect.",
            "Reject a candidate when a derived_hint or context_only scenario is rewritten as a direct fact, such as turning a mobility tag into teleportation, a role into area-of-effect damage, or a scenario tag into a guaranteed tactical effect.",
            "Treat conditional_relation as uncertain even when its endpoints are explicit; it cannot prove a best counter, guaranteed win, or certain outcome.",
            "Reject candidates that justify a matchup with implementation wording such as relation data, source bonus type, target type profile, or raw numeric confidence values.",
            "For multi_hop candidates, penalize unsupported tactical synergy between separate facts; separate facts should not be described as a combo unless that combo is directly supported.",
            "For multi_hop candidates, reject independent subquestions joined together, arbitrary cross-unit numeric comparisons, or answers that remain complete after a required claim is removed.",
            "For single_hop candidates, reject an answer that introduces a second independent attribute, cost, prerequisite, weapon metric, or ability effect beyond the one atomic claim.",
            "For ambiguous candidates, require natural gameplay branches or missing matchup conditions; reject answers framed as missing database fields or unavailable records.",
            "For activation_condition_ambiguity, reject combat advantage, counter, and survival questions; the answer must discuss activation restrictions such as energy, cooldown, target, or prerequisites.",
            "For activation_condition_ambiguity, reject inferred hidden costs, unstated cooldowns, or speculative energy requirements. An always-available label is not proof that a restriction exists or does not exist.",
            "For target_applicability_ambiguity, reject counter and survival questions; the answer must discuss the target's ground-or-air layer.",
            "For ambiguous matchup questions, a general statement that army size, upgrades, positioning, and player control may affect the outcome is an allowed uncertainty boundary, not an unsupported game fact. Reject only if the answer invents a specific value, mechanic, or outcome for those conditions.",
            "For ambiguous candidates, do not require a single definitive answer when the question is intentionally under-specified.",
        ],
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]


def reject_reason(reason: str, stats: BuildStats) -> str:
    stats.rejected_reasons[reason] = stats.rejected_reasons.get(reason, 0) + 1
    return reason


def log_progress(stage: str, message: str, current: int | None = None, total: int | None = None) -> None:
    """统一输出中间进度，便于长时间 API 调用时定位卡点。"""

    progress = f"progress={current}/{total} | " if current is not None and total is not None else ""
    print(f"[{stage}] {progress}{message}", flush=True)


def clean_candidate(
    data: dict[str, Any],
    target_complexity: str,
    stats: BuildStats,
    *,
    packet_type: str = "",
) -> tuple[dict[str, Any] | None, str]:
    # 不同模型偶尔会把 reference_answer 写成 answer；这里仅做字段兼容，
    # 最终公开文件仍统一输出 reference_answer。
    question = compact(normalize_public_text(data.get("question") or data.get("query")), 280)
    answer = compact(normalize_public_text(data.get("reference_answer") or data.get("answer")), 1200)
    complexity = normalize_complexity(data.get("evidence_complexity"))
    if complexity != target_complexity:
        return None, reject_reason("generator_complexity_mismatch", stats)
    if not question or not answer:
        return None, reject_reason("missing_question_or_answer", stats)
    if HAN_RE.search(question) or HAN_RE.search(answer):
        return None, reject_reason("non_english_text", stats)
    if has_question_meta_expression(question):
        return None, reject_reason("meta_expression_question_reject", stats)
    if has_answer_meta_expression(answer):
        return None, reject_reason("meta_expression_answer_reject", stats)
    if len(question) < 12 or len(answer) < 40:
        return None, reject_reason("too_short", stats)
    answer_sentences = [part for part in re.split(r"(?<=[.!?])\s+", answer) if part.strip()]
    if target_complexity == "single_hop" and (len(answer_sentences) > 2 or len(answer.split()) > 80):
        return None, reject_reason("single_hop_answer_not_focused", stats)
    if target_complexity == "multi_hop":
        lowered = f"{question} {answer}".lower()
        dimension_groups = [
            {"mineral", "minerals", "gas", "cost"},
            {"health", "shield", "shields", "armor"},
            {"seconds", "time", "cooldown"},
        ]
        used_groups = sum(any(token in lowered for token in group) for group in dimension_groups)
        if (" compare" in lowered or " higher than" in lowered or " lower than" in lowered) and used_groups > 1:
            return None, reject_reason("unrelated_dimension_comparison", stats)
    if target_complexity == "ambiguous":
        lowered = f"{question} {answer}".lower()
        combat_framing = r"\b(?:combat advantage|survival in combat|reliable counter|counter to|win engagements?)\b"
        if packet_type in {"activation_condition_ambiguity", "target_applicability_ambiguity"} and re.search(combat_framing, lowered):
            return None, reject_reason("ambiguous_domain_mismatch", stats)
        if packet_type == "activation_condition_ambiguity":
            # 允许“未明确说明”这类边界表达，但仍拒绝把未知条件写成隐藏机制或推测性能量要求。
            unsupported_inference = (
                r"\b(?:hidden|unstated|unlisted)\s+(?:cost|cooldown|prerequisite|requirement)\b"
                r"|\b(?:may|might)\s+require\s+energy\b"
            )
            if re.search(unsupported_inference, lowered):
                return None, reject_reason("unsupported_activation_inference", stats)
    strategic_conclusion = r"\b(?:reliable counter|strong against|effective against|combat advantage|favorable matchup)\b"
    if re.search(strategic_conclusion, f"{question} {answer}", re.IGNORECASE):
        return None, reject_reason("strategy_conclusion_reject", stats)
    return {
        "question": question,
        "reference_answer": answer,
        "evidence_complexity": complexity,
    }, ""


def parse_validator_result(model: str, text: str) -> ValidatorResult:
    data = extract_json_object(text)
    return ValidatorResult(
        model=model,
        answer_score=parse_score(data.get("answer_score", 0)),
        groundedness_score=parse_score(data.get("groundedness_score", 0)),
        complexity_confidence=parse_score(data.get("complexity_confidence", 0)),
        predicted_evidence_complexity=normalize_complexity(data.get("predicted_evidence_complexity")),
        accept=parse_bool(data.get("accept", False)),
        derived_hint_leak=parse_bool(data.get("derived_hint_leak", False)),
        source_quality_valid=parse_bool(data.get("source_quality_valid", False)),
        all_sentences_supported=parse_bool(data.get("all_sentences_supported", False)),
        evidence_chain_connected=parse_bool(data.get("evidence_chain_connected", False)),
        all_hops_necessary=parse_bool(data.get("all_hops_necessary", False)),
        single_claim_focus_valid=parse_bool(data.get("single_claim_focus_valid", False)),
        ambiguity_domain_valid=parse_bool(data.get("ambiguity_domain_valid", False)),
        reason=compact(data.get("reason"), 240),
    )


class QuestionDeduper:
    def __init__(self, model_path: Path, skip_bge: bool, stats: BuildStats) -> None:
        self.questions: list[str] = []
        self.normalized: set[str] = set()
        self.bge_model: Any | None = None
        self.embeddings: list[Any] = []
        if skip_bge:
            stats.bge_dedupe_enabled = False
            stats.bge_dedupe_note = "BGE-M3 semantic dedupe disabled; exact and near string matching were used."
            return
        try:
            from FlagEmbedding import BGEM3FlagModel

            if model_path.exists():
                self.bge_model = BGEM3FlagModel(str(model_path), use_fp16=True)
                stats.bge_dedupe_enabled = True
                stats.bge_dedupe_note = "BGE-M3 semantic dedupe enabled; exact and near string matching were also used."
            else:
                stats.bge_dedupe_note = "BGE-M3 semantic dedupe unavailable; exact and near string matching were used."
        except Exception as exc:
            stats.bge_dedupe_enabled = False
            stats.bge_dedupe_note = "BGE-M3 semantic dedupe unavailable; exact and near string matching were used."

    def is_duplicate(self, question: str) -> bool:
        norm = normalize_question(question)
        if norm in self.normalized:
            return True
        for existing in self.questions:
            ratio = SequenceMatcher(None, norm, normalize_question(existing)).ratio()
            if ratio >= 0.92:
                return True
        if self.bge_model is not None and self.embeddings:
            output = self.bge_model.encode(
                [question],
                batch_size=1,
                max_length=256,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False,
            )
            vector = output["dense_vecs"][0]
            for existing_vector in self.embeddings:
                similarity = float(vector @ existing_vector)
                if similarity >= 0.95:
                    return True
        return False

    def add(self, question: str) -> None:
        self.questions.append(question)
        self.normalized.add(normalize_question(question))
        if self.bge_model is not None:
            output = self.bge_model.encode(
                [question],
                batch_size=1,
                max_length=256,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False,
            )
            self.embeddings.append(output["dense_vecs"][0])


def validator_accepts(results: list[ValidatorResult], target_complexity: str, stats: BuildStats) -> tuple[bool, str]:
    """Pilot 阶段使用中等强度验证：保留答案和证据底线，放宽复杂度标签一致性。"""

    if len(results) < 3:
        return False, reject_reason("validator_count_less_than_three", stats)
    answer_scores = [item.answer_score for item in results]
    grounded_scores = [item.groundedness_score for item in results]
    complexity_scores = [item.complexity_confidence for item in results]
    accept_count = sum(1 for item in results if item.accept)
    label_count = sum(1 for item in results if item.predicted_evidence_complexity == target_complexity)
    derived_hint_leak_count = sum(1 for item in results if item.derived_hint_leak)
    source_quality_count = sum(1 for item in results if item.source_quality_valid)
    supported_count = sum(1 for item in results if item.all_sentences_supported)
    connected_count = sum(1 for item in results if item.evidence_chain_connected)
    necessary_count = sum(1 for item in results if item.all_hops_necessary)
    single_focus_count = sum(1 for item in results if item.single_claim_focus_valid)
    ambiguity_domain_count = sum(1 for item in results if item.ambiguity_domain_valid)
    # 至少两个验证模型发现“推导提示被写成确定事实”时，优先拒绝。
    # 这项检查独立于一般 groundedness 分数，便于在报告里定位该类风险。
    if derived_hint_leak_count >= 2:
        stats.derived_hint_claim_rejects += 1
        return False, reject_reason("derived_hint_written_as_fact", stats)
    if source_quality_count < 3:
        return False, reject_reason("source_quality_invalid", stats)
    if supported_count < 3:
        return False, reject_reason("unsupported_answer_sentence", stats)
    if target_complexity in {"two_hop", "multi_hop"} and connected_count < 2:
        return False, reject_reason("evidence_chain_not_connected", stats)
    if target_complexity in {"two_hop", "multi_hop"} and necessary_count < 2:
        return False, reject_reason("evidence_hops_not_necessary", stats)
    if target_complexity == "single_hop" and single_focus_count < 3:
        return False, reject_reason("single_claim_not_focused", stats)
    if target_complexity == "ambiguous" and ambiguity_domain_count < 3:
        return False, reject_reason("ambiguous_domain_invalid", stats)
    if statistics.mean(answer_scores) < VALIDATION_THRESHOLDS["mean_answer_score"]:
        return False, reject_reason("low_mean_answer_score", stats)
    if statistics.mean(grounded_scores) < VALIDATION_THRESHOLDS["mean_groundedness_score"]:
        return False, reject_reason("low_mean_groundedness_score", stats)
    if statistics.mean(complexity_scores) < VALIDATION_THRESHOLDS["mean_complexity_confidence"]:
        return False, reject_reason("low_mean_complexity_confidence", stats)
    if min(answer_scores) < VALIDATION_THRESHOLDS["min_answer_score"]:
        return False, reject_reason("low_min_answer_score", stats)
    if min(grounded_scores) < VALIDATION_THRESHOLDS["min_groundedness_score"]:
        return False, reject_reason("low_min_groundedness_score", stats)
    if accept_count < VALIDATION_THRESHOLDS["min_accept_count"]:
        return False, reject_reason("insufficient_validator_accepts", stats)
    if label_count < VALIDATION_THRESHOLDS["min_complexity_label_count"]:
        return False, reject_reason("complexity_vote_mismatch", stats)
    return True, ""


def record_evidence_layer_usage(stats: BuildStats, evidence_packet: dict[str, Any]) -> None:
    """在样本被接受后记录内部证据层使用情况；这些统计不进入公开 JSONL。"""

    has_context_only_derived = False
    for item in evidence_packet.get("evidence_items") or []:
        layer = str(item.get("evidence_layer") or "unknown")
        stats.evidence_layer_uses[layer] = stats.evidence_layer_uses.get(layer, 0) + 1
        if layer == EVIDENCE_LAYER_DERIVED and item.get("context_only"):
            has_context_only_derived = True
        if layer == EVIDENCE_LAYER_CONDITIONAL:
            relation_claim_value = ((item.get("claims") or [{}])[0].get("value") or {}) if item.get("claims") else {}
            relation_layer = str(
                relation_claim_value.get("relation_layer")
                or ((item.get("profile") or {}).get("conditional_relation") or {}).get("relation_layer")
                or "unknown"
            )
            stats.conditional_relation_layers[relation_layer] = (
                stats.conditional_relation_layers.get(relation_layer, 0) + 1
            )
    if has_context_only_derived:
        stats.derived_hint_context_samples += 1


def record_packet_provenance(stats: BuildStats, sample_id: str, evidence_packet: dict[str, Any]) -> None:
    """把最小证据链写进报告/checkpoint，公开 QA 行仍保持原字段。"""

    packet_type = str(evidence_packet.get("packet_type") or "unknown")
    stats.accepted_packet_types[packet_type] = stats.accepted_packet_types.get(packet_type, 0) + 1
    stats.accepted_provenance.append(
        {
            "sample_id": sample_id,
            "packet_type": packet_type,
            "required_claim_ids": list(evidence_packet.get("required_claim_ids") or []),
            "chain_edges": list(evidence_packet.get("chain_edges") or []),
        }
    )


def write_report(path: Path, rows: list[dict[str, Any]], stats: BuildStats) -> None:
    # 公开数据集保留生成与验证模型，便于后续按模型来源回溯样本。
    # 验证分数、证据包和内部 claim ID 仍只保留在构建过程，不写入 JSONL。
    by_model = {model: stats.accepted_by_model.get(model, 0) for model in MODEL_POOL}
    by_complexity = {item: sum(1 for row in rows if row["evidence_complexity"] == item) for item in COMPLEXITIES}
    lines = [
        "# QA Generation Report",
        "",
        "本报告用于说明 StarCraft II QA 数据集的生成情况，包括样本分布、验证阈值、候选尝试次数、拒绝原因和模型调用失败情况。",
        "公开数据集文件保留 id、question、reference_answer、evidence_complexity、generator_model 和 validator_models，供结果溯源与复杂度分组评测使用。",
        "",
        "## Summary",
        "",
        "本节概括最终保留样本数量以及是否启用 BGE-M3 语义去重。若未启用 BGE-M3，则脚本只使用完全重复和近似字符串相似度做去重。",
        "",
        f"- Total retained samples: {len(rows)}",
        f"- BGE-M3 semantic dedupe: {'enabled' if stats.bge_dedupe_enabled else 'disabled'}",
        f"- BGE-M3 note: {stats.bge_dedupe_note}",
        "- Strategy relation packets: disabled; the generator does not create counter or matchup conclusions.",
        "- Evidence-layer policy: single_hop uses explicit facts only; scenario profiles are context-only; rule-derived relations remain conditional.",
        "- Tech policy: multi-hop tech packets use same-race requires_building edges with building prerequisites only.",
        "- Ability policy: activation ambiguity uses only explicit costs, cooldowns, targets, states, or prerequisites from ability text.",
        "- Quality-gate policy: duplicate, damaged, and known-corrupted profiles are quarantined before evidence packets are sampled.",
        "",
        "## Runtime KB Quality Gate",
        "",
        "本节记录 QA 生成前发现并隔离的 runtime KB 问题。被隔离对象仍保留在 runtime KB 原文件中，但不会进入本次 QA 证据包。",
        "",
        "| issue type | quarantined count |",
        "|---|---:|",
    ]
    for issue_type, count in sorted(stats.kb_quality_counts.items()):
        lines.append(f"| `{issue_type}` | {count} |")
    lines.extend([
        "",
        "## Validation Thresholds",
        "",
        "本节记录模型验证阶段使用的保留阈值。候选问题需要在答案质量、证据支撑度、复杂度标签一致性等方面达到这些门槛。",
        "",
        "| metric | threshold |",
        "|---|---:|",
    ])
    for metric, value in VALIDATION_THRESHOLDS.items():
        lines.append(f"| `{metric}` | {value} |")
    lines.extend([
        "",
        "## Retained By Generator",
        "",
        "本节统计每个模型作为 generator 最终贡献的样本数。目标数量由 --samples-per-model-complexity 控制。",
        "",
        "| generator_model | count |",
        "|---|---:|",
    ])
    for model, count in by_model.items():
        lines.append(f"| `{model}` | {count} |")
    lines.extend([
        "",
        "## Retained By Evidence Complexity",
        "",
        "本节统计不同 evidence_complexity 类型的问题数量。每类目标数量由模型数量和 --samples-per-model-complexity 共同决定。",
        "",
        "| evidence_complexity | count |",
        "|---|---:|",
    ])
    for complexity, count in by_complexity.items():
        lines.append(f"| `{complexity}` | {count} |")
    lines.extend([
        "",
        "## Evidence Layer Usage",
        "",
        "本节只记录内部构建时使用的证据类型，不会写入公开 JSONL。`explicit_fact` 是可直接支撑单位属性、数值、技能效果、生产或科技条件的原始事实；`conditional_relation` 是必须保留不确定性的关系线索；`derived_hint` 只用于场景或边界上下文，不能单独写成确定游戏机制。",
        "",
        "| evidence layer | accepted item uses |",
        "|---|---:|",
    ])
    for layer in [EVIDENCE_LAYER_EXPLICIT, EVIDENCE_LAYER_CONDITIONAL, EVIDENCE_LAYER_DERIVED]:
        lines.append(f"| `{layer}` | {stats.evidence_layer_uses.get(layer, 0)} |")
    lines.extend([
        "",
        f"- Accepted samples with context-only derived hints: {stats.derived_hint_context_samples}",
        f"- Candidates rejected because derived hints were written as definite facts: {stats.derived_hint_claim_rejects}",
        "",
        "### Conditional Relation Layers",
        "",
        "该表说明被接受样本使用的条件关系来自哪个关系层。无论来源层如何，公开答案都必须使用潜在或条件性的措辞。",
        "",
        "| relation layer | accepted conditional relations |",
        "|---|---:|",
    ])
    for layer, count in sorted(stats.conditional_relation_layers.items()):
        lines.append(f"| `{layer}` | {count} |")
    lines.extend([
        "",
        "## Accepted Packet Types",
        "",
        "本节说明最终样本使用了哪一种证据链模板。模板只负责保证 claim 连通性，不作为公开数据字段。",
        "",
        "| packet type | count |",
        "|---|---:|",
    ])
    for packet_type, count in sorted(stats.accepted_packet_types.items()):
        lines.append(f"| `{packet_type}` | {count} |")
    lines.extend([
        "",
        "## Attempt Counts",
        "",
        "本节统计每个“生成模型 + 复杂度类型”组合尝试了多少个候选样本。尝试次数越高，说明该组合更容易被本地规则或验证模型拒绝。",
        "",
        "| slot | attempts |",
        "|---|---:|",
    ])
    for slot, count in sorted(stats.attempts_by_slot.items()):
        lines.append(f"| `{slot}` | {count} |")
    lines.extend([
        "",
        "## Rejection Reasons",
        "",
        "本节统计候选样本被拒绝的原因，例如生成格式错误、验证分数不足、问题含有元表述或重复问题等。",
        "",
        "| reason | count |",
        "|---|---:|",
    ])
    for reason, count in sorted(stats.rejected_reasons.items()):
        lines.append(f"| `{reason}` | {count} |")
    lines.extend([
        "",
        "## Model Call Or JSON Failures",
        "",
        "本节统计模型 API 调用失败或模型输出无法解析为合法 JSON 的次数。该统计用于定位不稳定模型，不会写入公开 JSONL。",
        "",
        "| model | count |",
        "|---|---:|",
    ])
    for model, count in sorted(stats.model_failures.items()):
        lines.append(f"| `{model}` | {count} |")
    lines.extend([
        "",
        "## Evidence Provenance",
        "",
        "本节保留每条公开样本对应的内部 claim 链，便于复核 evidence_complexity；claim ID 和 field path 不会写入公开 JSONL。",
        "",
        "| sample_id | packet_type | required_claim_ids |",
        "|---|---|---|",
    ])
    for item in stats.accepted_provenance:
        claim_text = ", ".join(f"`{claim_id}`" for claim_id in item.get("required_claim_ids") or [])
        lines.append(f"| `{item.get('sample_id')}` | `{item.get('packet_type')}` | {claim_text} |")
    lines.extend([
        "",
        "## Final Samples",
        "",
        "本节列出最终保留样本的 ID、复杂度标签和对应生成模型，便于快速检查数据集是否配平。",
        "",
        "| id | evidence_complexity | generator_model |",
        "|---|---|---|",
    ])
    for row in rows:
        lines.append(f"| `{row['id']}` | `{row['evidence_complexity']}` | `{row['generator_model']}` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_candidate_parallel(
    client: OpenAICompatibleChat,
    validator_models: list[str],
    candidate: dict[str, Any],
    evidence_packet: dict[str, Any],
    max_tokens: int,
) -> tuple[list[ValidatorResult], list[str]]:
    """并行调用 4 个验证模型，减少单个候选样本的等待时间。"""

    def run_one(model: str) -> tuple[str, ValidatorResult | None]:
        raw = client.complete(
            model,
            validator_messages(candidate, evidence_packet),
            max_tokens=max_tokens,
            temperature=0.0,
        )
        return model, parse_validator_result(model, raw)

    results: list[ValidatorResult] = []
    failed_models: list[str] = []
    with ThreadPoolExecutor(max_workers=len(validator_models)) as executor:
        futures = {executor.submit(run_one, model): model for model in validator_models}
        for future in as_completed(futures):
            model = futures[future]
            try:
                _, result = future.result()
                if result is not None:
                    results.append(result)
            except Exception:
                failed_models.append(model)
    return results, failed_models


def generate_dataset(args: argparse.Namespace) -> tuple[list[dict[str, Any]], BuildStats]:
    # 本地 pilot 暂时允许使用代码内置 key；如果设置了环境变量，则优先使用环境变量。
    api_key = os.environ.get(args.api_key_env) or DEFAULT_API_KEY
    if not api_key:
        raise SystemExit(f"Missing API key: set {args.api_key_env} or configure DEFAULT_API_KEY")

    samples_per_slot = 1 if args.debug_one else args.samples_per_model_complexity
    target_count = DEBUG_SAMPLE_COUNT if args.debug_one else target_sample_count(samples_per_slot)
    config = checkpoint_config(args, target_count, samples_per_slot)
    final_output = output_path(target_count)

    checkpoint_data: tuple[list[dict[str, Any]], BuildStats] | None = None
    if not args.debug_one:
        if final_output.exists():
            raise SystemExit(f"{final_output} already exists and will not be overwritten.")
        if args.no_resume:
            remove_checkpoint(target_count)
        else:
            checkpoint_data = load_checkpoint(target_count, config)

    kb = load_runtime_kb(Path(args.runtime_kb))
    retained, stats = checkpoint_data if checkpoint_data else ([], BuildStats())
    stats.kb_quality_counts = dict(kb.quality_counts)
    deduper = QuestionDeduper(Path(args.bge_model_path), skip_bge=args.skip_bge_dedupe, stats=stats)
    for row in retained:
        deduper.add(row["question"])
    client = OpenAICompatibleChat(api_key=api_key, base_url=args.base_url, timeout=args.timeout, api_retries=args.api_retries)
    sample_no = len(retained) + 1
    internal_surface_reject_streak: dict[str, int] = {model: 0 for model in MODEL_POOL}
    log_progress(
        "START",
        f"target={target_count}, samples_per_model_complexity={samples_per_slot}, "
        f"runtime_kb={args.runtime_kb}, bge_dedupe={'off' if args.skip_bge_dedupe else 'on'}",
        len(retained),
        target_count,
    )
    if checkpoint_data:
        log_progress("RESUME", f"loaded {len(retained)} checkpoint samples", len(retained), target_count)
    if len(retained) >= target_count:
        log_progress("DONE", f"checkpoint already has target_count={target_count}", len(retained), target_count)
        return retained, stats

    for generator_model in MODEL_POOL:
        validator_models = [model for model in MODEL_POOL if model != generator_model]
        log_progress("MODEL", f"generator={generator_model}, validators={len(validator_models)}", len(retained), target_count)
        for complexity in COMPLEXITIES:
            slot = f"{generator_model}::{complexity}"
            existing_in_slot = sum(
                1
                for row in retained
                if row["generator_model"] == generator_model and row["evidence_complexity"] == complexity
            )
            if existing_in_slot > samples_per_slot:
                raise RuntimeError(f"Checkpoint has too many samples for {slot}: {existing_in_slot} > {samples_per_slot}")
            if existing_in_slot == samples_per_slot:
                log_progress("SLOT", f"{slot} skipped; checkpoint already has {existing_in_slot}/{samples_per_slot}", len(retained), target_count)
                continue
            log_progress("SLOT", f"{slot} started; target_slot_samples={samples_per_slot}, existing={existing_in_slot}", len(retained), target_count)
            for slot_sample_no in range(existing_in_slot + 1, samples_per_slot + 1):
                accepted = False
                log_progress("SLOT_SAMPLE", f"{slot} | sample={slot_sample_no}/{samples_per_slot}", len(retained), target_count)
                for round_no in range(1, args.max_rounds + 1):
                    for attempt_no in range(1, args.max_candidates_per_round + 1):
                        stats.attempts_by_slot[slot] = stats.attempts_by_slot.get(slot, 0) + 1
                        attempt_count = stats.attempts_by_slot[slot]
                        log_progress(
                            "TRY",
                            f"{slot} | sample={slot_sample_no}/{samples_per_slot}, "
                            f"round={round_no}, candidate={attempt_no}, attempt={attempt_count}",
                            len(retained),
                            target_count,
                        )
                        seed = f"{args.seed}|{generator_model}|{complexity}|{slot_sample_no}|{round_no}|{attempt_no}"
                        evidence_packet = build_evidence_packet(kb, complexity, seed)
                        log_progress("GENERATE", f"{slot} | calling generator", len(retained), target_count)
                        try:
                            raw = client.complete(
                                generator_model,
                                generator_messages(complexity, evidence_packet),
                                max_tokens=args.generator_max_tokens,
                                temperature=args.generator_temperature,
                            )
                            candidate_data = extract_json_object(raw)
                        except Exception as exc:
                            stats.model_failures[generator_model] = stats.model_failures.get(generator_model, 0) + 1
                            reject_reason("generator_call_or_json_failed", stats)
                            log_progress("REJECT", f"{slot} | generator_call_or_json_failed | {type(exc).__name__}: {compact(exc, 180)}", len(retained), target_count)
                            continue
                        candidate, reason = clean_candidate(
                            candidate_data,
                            complexity,
                            stats,
                            packet_type=str(evidence_packet.get("packet_type") or ""),
                        )
                        if candidate is None:
                            internal_surface_reject_streak[generator_model] = 0
                            log_progress("REJECT", f"{slot} | {reason}", len(retained), target_count)
                            if not args.debug_one and stats.attempts_by_slot[slot] % args.report_interval == 0:
                                write_report(report_path(), retained, stats)
                            continue
                        has_internal_surface, internal_token = reject_internal_surface_form(
                            candidate["question"],
                            candidate["reference_answer"],
                        )
                        if has_internal_surface:
                            streak = internal_surface_reject_streak.get(generator_model, 0) + 1
                            internal_surface_reject_streak[generator_model] = streak
                            reject_reason("internal_surface_form_reject", stats)
                            log_progress(
                                "REJECT",
                                f"{slot} | internal_surface_form_reject | token={internal_token} | streak={streak}",
                                len(retained),
                                target_count,
                            )
                            if not args.debug_one and stats.attempts_by_slot[slot] % args.report_interval == 0:
                                write_report(report_path(), retained, stats)
                            continue
                        else:
                            internal_surface_reject_streak[generator_model] = 0
                        if deduper.is_duplicate(candidate["question"]):
                            reject_reason("duplicate_question", stats)
                            log_progress("REJECT", f"{slot} | duplicate_question | question={compact(candidate['question'], 120)}", len(retained), target_count)
                            if not args.debug_one and stats.attempts_by_slot[slot] % args.report_interval == 0:
                                write_report(report_path(), retained, stats)
                            continue

                        log_progress("CANDIDATE", f"{slot} | question={compact(candidate['question'], 160)}", len(retained), target_count)
                        log_progress("VALIDATE", f"{slot} | calling {len(validator_models)} validators", len(retained), target_count)
                        validator_results, failed_models = validate_candidate_parallel(
                            client,
                            validator_models,
                            candidate,
                            evidence_packet,
                            args.validator_max_tokens,
                        )
                        log_progress(
                            "VALIDATE",
                            f"{slot} | valid={len(validator_results)}, failed={len(failed_models)}"
                            + (f", failed_models={','.join(failed_models)}" if failed_models else ""),
                            len(retained),
                            target_count,
                        )
                        if validator_results:
                            log_progress(
                                "VOTES",
                                f"{slot} | accept={sum(item.accept for item in validator_results)}/{len(validator_results)}, "
                                f"source_quality={sum(item.source_quality_valid for item in validator_results)}, "
                                f"supported={sum(item.all_sentences_supported for item in validator_results)}, "
                                f"connected={sum(item.evidence_chain_connected for item in validator_results)}, "
                                f"necessary={sum(item.all_hops_necessary for item in validator_results)}",
                                len(retained),
                                target_count,
                            )
                        if failed_models:
                            for validator_model in failed_models:
                                stats.model_failures[validator_model] = stats.model_failures.get(validator_model, 0) + 1
                            # Pilot 阶段允许 1 个 validator API/JSON 失败；
                            # 只要仍有至少 3 个有效验证结果，就继续进入评分逻辑。
                            if len(validator_results) < 3:
                                reject_reason("validator_call_or_json_failed", stats)
                                log_progress("REJECT", f"{slot} | validator_call_or_json_failed | valid={len(validator_results)}", len(retained), target_count)
                                if not args.debug_one and stats.attempts_by_slot[slot] % args.report_interval == 0:
                                    write_report(report_path(), retained, stats)
                                continue
                        ok, validation_reason = validator_accepts(validator_results, complexity, stats)
                        if not ok:
                            log_progress("REJECT", f"{slot} | {validation_reason}", len(retained), target_count)
                            if not args.debug_one and stats.attempts_by_slot[slot] % args.report_interval == 0:
                                write_report(report_path(), retained, stats)
                            continue

                        # 仅公开成功返回有效 JSON 评估的模型，避免把 API/JSON 失败模型误写为实际 validator。
                        successful_validator_models = {
                            result.model for result in validator_results
                        }
                        row = {
                            "id": f"sc2qa_{sample_no:06d}",
                            "question": candidate["question"],
                            "reference_answer": candidate["reference_answer"],
                            "evidence_complexity": candidate["evidence_complexity"],
                            # 记录本条样本的生成模型及成功参与验证的模型；
                            # 不记录评分和原始验证输出，避免公开无关的内部过程数据。
                            "generator_model": generator_model,
                            "validator_models": [
                                model for model in validator_models
                                if model in successful_validator_models
                            ],
                        }
                        deduper.add(row["question"])
                        retained.append(row)
                        sample_no += 1
                        accepted = True
                        stats.accepted_by_model[generator_model] = stats.accepted_by_model.get(generator_model, 0) + 1
                        stats.accepted_by_complexity[complexity] = stats.accepted_by_complexity.get(complexity, 0) + 1
                        record_evidence_layer_usage(stats, evidence_packet)
                        record_packet_provenance(stats, row["id"], evidence_packet)
                        log_progress("ACCEPT", f"{row['id']} | {complexity} | generator={generator_model}", len(retained), target_count)
                        if not args.debug_one:
                            write_checkpoint(target_count, retained, stats, config)
                            write_report(report_path(), retained, stats)
                        if len(retained) >= target_count:
                            log_progress("DONE", f"retained={len(retained)}", len(retained), target_count)
                            return retained, stats
                        break
                    if accepted:
                        break
                if not accepted:
                    if not args.debug_one:
                        write_report(report_path(), retained, stats)
                    log_progress("FAILED", f"{slot} | sample={slot_sample_no}/{samples_per_slot}, attempts={stats.attempts_by_slot.get(slot, 0)}", len(retained), target_count)
                    raise RuntimeError(f"Failed to generate accepted sample {slot_sample_no}/{samples_per_slot} for {slot}")
    return retained, stats


def validate_public_dataset(rows: list[dict[str, Any]], expected_count: int | None) -> None:
    base_keys = {
        "id", "question", "reference_answer", "evidence_complexity",
        "generator_model", "validator_models",
    }
    if expected_count is not None and len(rows) != expected_count:
        raise ValueError(f"Expected {expected_count} samples, got {len(rows)}")
    for row in rows:
        if frozenset(row) != frozenset(base_keys):
            raise ValueError(f"Unexpected public fields in {row.get('id')}: {sorted(row)}")
        if HAN_RE.search(json.dumps(row, ensure_ascii=False)):
            raise ValueError(f"Non-English text detected in {row.get('id')}")
        if has_question_meta_expression(row["question"]):
            raise ValueError(f"Meta expression detected in question of {row.get('id')}")
        if has_answer_meta_expression(row["reference_answer"]):
            raise ValueError(f"Meta expression detected in reference_answer of {row.get('id')}")
        if row["evidence_complexity"] not in COMPLEXITIES:
            raise ValueError(f"Invalid evidence_complexity in {row.get('id')}")
        if row["generator_model"] not in MODEL_POOL:
            raise ValueError(f"Unknown generator_model in {row.get('id')}")
        expected_validators = {model for model in MODEL_POOL if model != row["generator_model"]}
        validators = row["validator_models"]
        if (
            not isinstance(validators, list)
            or len(validators) < 3
            or len(validators) != len(set(validators))
            or not set(validators).issubset(expected_validators)
        ):
            raise ValueError(f"Unexpected validator_models in {row.get('id')}")
        forbidden = ["SiliconFlow", "siliconflow", "api.siliconflow", "provider", "base_url", "api_key", "question_type", "annotation_note"]
        body = json.dumps(row, ensure_ascii=False)
        if any(token in body for token in forbidden):
            raise ValueError(f"Forbidden public output token detected in {row.get('id')}")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    default_runtime = project_root / "my_knowledge" / "starcraft_kb" / "runtime_kb"
    default_bge = project_root / "my_knowledge" / "starcraft_rag" / "LLM" / "bge-m3"

    parser = argparse.ArgumentParser(description="Generate a StarCraft II QA dataset with rotating LLM generators and validators.")
    parser.add_argument("--runtime-kb", default=str(default_runtime))
    parser.add_argument("--api-key-env", default="SILICONFLOW_API_KEY")
    parser.add_argument("--base-url", default="https://api.siliconflow.cn/v1")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--api-retries", type=int, default=1)
    parser.add_argument("--seed", default="20260706")
    parser.add_argument(
        "--samples-per-model-complexity",
        type=int,
        default=DEFAULT_SAMPLES_PER_MODEL_COMPLEXITY,
        help="Accepted samples to keep for each generator model and evidence_complexity pair.",
    )
    parser.add_argument("--max-rounds", type=int, default=3)
    parser.add_argument("--max-candidates-per-round", type=int, default=10)
    parser.add_argument("--generator-temperature", type=float, default=0.7)
    parser.add_argument("--generator-max-tokens", type=int, default=520)
    parser.add_argument("--validator-max-tokens", type=int, default=320)
    parser.add_argument("--report-interval", type=int, default=5)
    parser.add_argument("--bge-model-path", default=str(default_bge))
    parser.add_argument("--skip-bge-dedupe", action="store_true")
    parser.add_argument("--no-resume", action="store_true", help="Ignore and remove existing checkpoint files before generation.")
    parser.add_argument("--debug-one", action="store_true", help="Run one in-memory QA generation test without writing final output files.")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    if args.samples_per_model_complexity < 1:
        raise SystemExit("--samples-per-model-complexity must be >= 1")
    rows, stats = generate_dataset(args)
    expected_count = DEBUG_SAMPLE_COUNT if args.debug_one else target_sample_count(args.samples_per_model_complexity)
    validate_public_dataset(rows, expected_count=expected_count)
    if args.debug_one:
        print(json.dumps(rows[0], ensure_ascii=False, indent=2))
        print("Debug one-sample run completed; final output files were not modified.")
        return
    final_output = output_path(expected_count)
    final_report = report_path()
    write_jsonl(final_output, rows)
    write_report(final_report, rows, stats)
    remove_checkpoint(expected_count)
    print(f"Wrote {len(rows)} samples to {final_output}")
    print(f"Wrote report to {final_report}")


if __name__ == "__main__":
    main()
