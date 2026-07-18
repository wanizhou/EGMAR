from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LLMResponse:
    text: str
    model: str
    metadata: dict


class BaseLLMProvider:
    """后续 DeepSeek/OpenAI/本地模型调用的统一入口。"""

    name = "BaseLLMProvider"

    def complete(self, messages: list[dict[str, str]], **kwargs) -> LLMResponse:
        raise NotImplementedError


class NullLLMProvider(BaseLLMProvider):
    name = "NullLLMProvider"

    def complete(self, messages: list[dict[str, str]], **kwargs) -> LLMResponse:
        return LLMResponse(text="", model=self.name, metadata={"note": "LLM provider not configured"})


class TransformersLocalProvider(BaseLLMProvider):
    """本地 Transformers 模型调用入口。

    模型采用懒加载，只有第一次 Router 调用时才会占用显存。
    """

    name = "TransformersLocalProvider"

    def __init__(
        self,
        model_path: str | Path,
        dtype: str = "float16",
        device_map: str = "auto",
        trust_remote_code: bool = True,
    ) -> None:
        self.model_path = str(model_path)
        self.dtype = dtype
        self.device_map = device_map
        self.trust_remote_code = trust_remote_code
        self._tokenizer: Any = None
        self._model: Any = None

    def _load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # 本地模型只在第一次调用时加载；dtype/device_map 保持可配置，便于后续换量化模型或多卡。
        dtype_map = {
            "float16": torch.float16,
            "fp16": torch.float16,
            "bfloat16": torch.bfloat16,
            "bf16": torch.bfloat16,
            "float32": torch.float32,
            "fp32": torch.float32,
        }
        torch_dtype = dtype_map.get(self.dtype.lower(), torch.float16)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_path, trust_remote_code=self.trust_remote_code)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            dtype=torch_dtype,
            device_map=self.device_map,
            trust_remote_code=self.trust_remote_code,
        )
        self._model.eval()

    def complete(self, messages: list[dict[str, str]], **kwargs) -> LLMResponse:
        self._load()
        import torch

        max_new_tokens = int(kwargs.get("max_new_tokens", 512))
        enable_thinking = bool(kwargs.get("enable_thinking", False))
        # 使用 tokenizer 的 chat_template 组装消息，避免手写不同模型的对话格式。
        text = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking,
        )
        inputs = self._tokenizer(
            [text], return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            # Router 需要稳定 JSON，因此默认关闭采样，让同一问题尽量得到可复现输出。
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                eos_token_id=self._tokenizer.eos_token_id,
            )
        generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]
        response = self._tokenizer.decode(
            generated_ids, skip_special_tokens=True)
        return LLMResponse(
            text=response.strip(),
            model=Path(self.model_path).name,
            metadata={"provider": self.name, "model_path": self.model_path},
        )


# You are the StarCraft II RAG Router. Convert the user query into candidate Agents, doc_types, and query_terms.
ROUTER_SYSTEM_PROMPT = """
You are the StarCraft II RAG Router, not the final answer model.
Convert the user query into retrieval hints: intent_candidates, candidate_agents, candidate_doc_types, query_terms, and scenario_tags.
Output only one JSON object. Do not output Markdown or explanations outside JSON.
The JSON must include: intent_candidates, candidate_agents, candidate_doc_types, query_terms, scenario_tags, confidence, reason.
The reason field must be a short English explanation of the routing decision.
entities, abilities, and scenario_tags may be empty. Do not invent unverified entity ids or ability ids.
If the query asks how to handle or counter X, prefer counter_relation, scenario_router, and scenario_candidates.
If the query asks how to build X, cost, prerequisite, or technology path, prefer entity_cost_tech.
If the query asks about ability, effect, control, or damage, prefer ability_effect and ability_usage.
Common SC2 abbreviations: DT usually means Dark Templar; BC usually means Battlecruiser; HT usually means High Templar; storm usually means Psionic Storm; scan usually means Scanner Sweep.
"""


ROUTER_FEW_SHOT_EXAMPLES = [
    {
        "query": "The opponent switched to DT. How should I respond?",
        "output": {
            "intent_candidates": ["anti_cloak_response", "counter_relation"],
            "candidate_agents": ["ScenarioRouterAgent", "AbilityAgent", "CounterAgent"],
            "candidate_doc_types": ["scenario_router", "scenario_candidates", "ability_effect", "relation_counter"],
            "query_terms": ["DT", "Dark Templar", "anti_cloak", "detector", "Scanner Sweep"],
            "scenario_tags": ["anti_cloak_response"],
            "confidence": 0.9,
            "reason": "DT usually means Dark Templar; the query asks for response, so anti-cloak and counter-relation hints are important.",
        },
    },
    {
        "query": "How do I build DT and what prerequisites are required?",
        "output": {
            "intent_candidates": ["tech_tree"],
            "candidate_agents": ["TechTreeAgent", "UnitProfileAgent"],
            "candidate_doc_types": ["entity_cost_tech", "entity_overview"],
            "query_terms": ["DT", "Dark Templar", "protoss_dark_templar", "requires_building", "cost"],
            "scenario_tags": ["tech_planning"],
            "confidence": 0.9,
            "reason": "The query asks for production and prerequisites, so tech-tree and cost documents should be prioritized.",
        },
    },
    {
        "query": "The opponent switched to BC. How should I handle it?",
        "output": {
            "intent_candidates": ["air_control", "counter_relation"],
            "candidate_agents": ["ScenarioRouterAgent", "CounterAgent", "UnitProfileAgent"],
            "candidate_doc_types": ["scenario_router", "scenario_candidates", "entity_combat", "relation_counter"],
            "query_terms": ["BC", "Battlecruiser", "terran_battlecruiser", "anti_air", "air_control"],
            "scenario_tags": ["air_control"],
            "confidence": 0.85,
            "reason": "BC usually means Battlecruiser, a heavy air threat, so air-control and counter-relation hints are useful.",
        },
    },
    # Additional examples can be added here if Router coverage is weak for a specific query family.
]

SYNTHESIZER_SYSTEM_PROMPT = """
You are the StarCraft II RAG answer synthesizer. Answer only from Agent evidence.
Distinguish processed raw facts from enriched rule-based inferences, and never state rule-based inferences as absolute conclusions.
"""

