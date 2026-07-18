from __future__ import annotations

from pathlib import Path

from starcraft_rag.agents import AGENT_REGISTRY
from starcraft_rag.config import DEFAULT_MODEL_ROOT
from starcraft_rag.context import RAGContext
from starcraft_rag.kb import KBStore
from starcraft_rag.llm import BaseLLMProvider, TransformersLocalProvider
from starcraft_rag.resolver import AgentPlanner, KnowledgeResolver
from starcraft_rag.retriever import BaseRetriever, HybridRetriever, MetadataKeywordRetriever
from starcraft_rag.router import LLMRouter, RuleBasedRouter
from starcraft_rag.synthesizer import LLMAnswerSynthesizer, TemplateAnswerSynthesizer


class StarCraftRAGPipeline:
    """RAG 主流程。

    调试时建议从 answer() 开始单步执行；ctx 会按顺序累积中间结果。
    """

    def __init__(
        self,
        runtime_kb_dir: str | Path | None = None,
        retriever: BaseRetriever | None = None,
        router_mode: str = "local",
        llm_provider: BaseLLMProvider | None = None,
        model_path: str | Path | None = None,
        llm_max_new_tokens: int = 512,
        retriever_mode: str = "bge-m3",
        bge_model_path: str | Path | None = None,
        bge_score_mode: str = "hybrid",
        bge_batch_size: int = 16,
        bge_max_length: int = 512,
        bge_dense_weight: float = 0.65,
        bge_sparse_weight: float = 0.35,
        bge_metadata_weight: float = 0.18,
        bge_candidate_pool_size: int = 80,
        bge_use_fp16: bool = True,
        rebuild_vector_index: bool = False,
        agent_mode: str = "local",
        agent_llm_provider: BaseLLMProvider | None = None,
        agent_llm_max_new_tokens: int = 768,
        agent_claim_top_k: int = 8,
        agent_output_top_k: int = 5,
        synthesizer_mode: str = "local",
        synthesizer_llm_provider: BaseLLMProvider | None = None,
        synthesizer_llm_max_new_tokens: int = 768,
        synthesizer_evidence_top_k: int = 16,
        synthesizer_supporting_point_top_k: int = 5,
        top_k: int = 8,
    ) -> None:
        self.kb_store = KBStore(runtime_kb_dir)
        self.router = self._build_router(
            router_mode=router_mode,
            llm_provider=llm_provider,
            model_path=model_path,
            llm_max_new_tokens=llm_max_new_tokens,
        )
        self.retriever = retriever or self._build_retriever(
            retriever_mode=retriever_mode,
            bge_model_path=bge_model_path,
            bge_score_mode=bge_score_mode,
            bge_batch_size=bge_batch_size,
            bge_max_length=bge_max_length,
            bge_dense_weight=bge_dense_weight,
            bge_sparse_weight=bge_sparse_weight,
            bge_metadata_weight=bge_metadata_weight,
            bge_candidate_pool_size=bge_candidate_pool_size,
            bge_use_fp16=bge_use_fp16,
            rebuild_vector_index=rebuild_vector_index,
        )
        self.resolver = KnowledgeResolver(self.kb_store)
        self.planner = AgentPlanner(self.kb_store)
        self.agent_mode = agent_mode
        shared_agent_provider = self._build_agent_provider(
            agent_mode=agent_mode,
            agent_llm_provider=agent_llm_provider,
            router_provider=getattr(self.router, "provider", None),
            model_path=model_path,
        )
        self.agents = {
            name: cls(
                agent_mode=agent_mode,
                llm_provider=shared_agent_provider,
                llm_max_new_tokens=agent_llm_max_new_tokens,
                claim_top_k=agent_claim_top_k,
                output_top_k=agent_output_top_k,
            )
            for name, cls in AGENT_REGISTRY.items()
        }
        self.synthesizer = self._build_synthesizer(
            synthesizer_mode=synthesizer_mode,
            synthesizer_llm_provider=synthesizer_llm_provider,
            router_provider=getattr(self.router, "provider", None),
            agent_provider=shared_agent_provider,
            model_path=model_path,
            max_new_tokens=synthesizer_llm_max_new_tokens,
            evidence_top_k=synthesizer_evidence_top_k,
            supporting_point_top_k=synthesizer_supporting_point_top_k,
        )
        self.top_k = top_k

    def _build_synthesizer(
        self,
        synthesizer_mode: str,
        synthesizer_llm_provider: BaseLLMProvider | None,
        router_provider: BaseLLMProvider | None,
        agent_provider: BaseLLMProvider | None,
        model_path: str | Path | None,
        max_new_tokens: int,
        evidence_top_k: int,
        supporting_point_top_k: int,
    ) -> TemplateAnswerSynthesizer:
        mode = synthesizer_mode.lower()
        if mode == "template":
            return TemplateAnswerSynthesizer()
        if mode not in {"local", "local-llm"}:
            raise ValueError(f"Unknown synthesizer_mode: {synthesizer_mode}")

        provider = synthesizer_llm_provider
        if provider is None and isinstance(router_provider, TransformersLocalProvider):
            # Router 已经使用本地 Qwen 时，Synthesizer 复用同一个 provider，避免重复加载显存。
            provider = router_provider
        if provider is None and isinstance(agent_provider, TransformersLocalProvider):
            # 如果 Router 不是本地模型，但 Agent 已加载本地 Qwen，也复用 Agent provider。
            provider = agent_provider
        if provider is None:
            if not model_path:
                model_path = DEFAULT_MODEL_ROOT / "Qwen3-8B"
            provider = TransformersLocalProvider(model_path=model_path)

        return LLMAnswerSynthesizer(
            llm_provider=provider,
            max_new_tokens=max_new_tokens,
            evidence_top_k=evidence_top_k,
            supporting_point_top_k=supporting_point_top_k,
        )

    def _build_agent_provider(
        self,
        agent_mode: str,
        agent_llm_provider: BaseLLMProvider | None,
        router_provider: BaseLLMProvider | None,
        model_path: str | Path | None,
    ) -> BaseLLMProvider | None:
        mode = agent_mode.lower()
        if mode in {"rule", "none"}:
            return None
        if mode not in {"local", "local-llm"}:
            raise ValueError(f"Unknown agent_mode: {agent_mode}")
        if agent_llm_provider is not None:
            return agent_llm_provider
        if isinstance(router_provider, TransformersLocalProvider):
            # Router 与 Agent 都使用 Qwen3-8B 时复用同一个 provider，避免重复加载显存。
            return router_provider
        if not model_path:
            model_path = DEFAULT_MODEL_ROOT / "Qwen3-8B"
        return TransformersLocalProvider(model_path=model_path)

    def _build_retriever(
        self,
        retriever_mode: str,
        bge_model_path: str | Path | None,
        bge_score_mode: str,
        bge_batch_size: int,
        bge_max_length: int,
        bge_dense_weight: float,
        bge_sparse_weight: float,
        bge_metadata_weight: float,
        bge_candidate_pool_size: int,
        bge_use_fp16: bool,
        rebuild_vector_index: bool,
    ) -> BaseRetriever:
        mode = retriever_mode.lower()
        if mode in {"keyword", "metadata-keyword"}:
            return MetadataKeywordRetriever(self.kb_store)
        if mode in {"bge", "bge-m3", "hybrid", "hybrid-vector"}:
            # BGE-M3 路径只影响 Retriever；Router、Resolver 和 Agent 接口保持不变。
            return HybridRetriever(
                self.kb_store,
                model_path=bge_model_path,
                score_mode=bge_score_mode,
                batch_size=bge_batch_size,
                max_length=bge_max_length,
                dense_weight=bge_dense_weight,
                sparse_weight=bge_sparse_weight,
                metadata_weight=bge_metadata_weight,
                candidate_pool_size=bge_candidate_pool_size,
                use_fp16=bge_use_fp16,
                rebuild_index=rebuild_vector_index,
            )
        raise ValueError(f"Unknown retriever_mode: {retriever_mode}")

    def _build_router(
        self,
        router_mode: str,
        llm_provider: BaseLLMProvider | None,
        model_path: str | Path | None,
        llm_max_new_tokens: int,
    ):
        mode = router_mode.lower()
        if mode == "rule":
            # 最轻量路径：完全不调用 LLM，适合快速回归和定位检索/Agent 逻辑问题。
            return RuleBasedRouter(self.kb_store)
        if mode in {"local", "local-llm"}:
            if llm_provider is None:
                if not model_path:
                    # 默认读取项目内的 Qwen3-8B；模型实际加载发生在第一次 Router 调用时。
                    model_path = DEFAULT_MODEL_ROOT / "Qwen3-8B"
                llm_provider = TransformersLocalProvider(model_path=model_path)
            # 本地 LLM 只增强 Router 意图判断，后续检索、profile 回连和 Agent 执行流程保持不变。
            return LLMRouter(self.kb_store, provider=llm_provider, max_new_tokens=llm_max_new_tokens)
        raise ValueError(f"Unknown router_mode: {router_mode}")

    def answer(self, query: str, top_k: int | None = None) -> RAGContext:
        ctx = RAGContext(query=query)  # 创建本次查询的上下文对象，后续所有中间结果都会逐步写入 ctx。
        ctx.plan = self.router.route(query)  # 调用 Router，把自然语言问题转换成 QueryPlan，例如候选 Agent、doc_type、关键词和场景标签。
        ctx.documents = self.retriever.retrieve(ctx.plan, top_k=top_k or self.top_k)  # 根据 QueryPlan 检索 rag_documents.jsonl，得到最相关的 RAG 文档入口。
        ctx.knowledge_hits = self.resolver.resolve(ctx.documents)  # 将命中的 RAG 文档回连到 runtime profiles，生成带 profile_refs 的 KnowledgeHit。
        ctx.agent_tasks = self.planner.plan(ctx)  # 根据 KnowledgeHit 中的 Agent 提示和 profile_refs，规划每个 Agent 需要读取哪些 profile。

        for task in ctx.agent_tasks:  # 逐个处理 AgentPlanner 生成的 AgentTask。
            agent = self.agents.get(task.agent_name)  # 根据任务里的 agent_name，从已注册的 Agent 实例表中取出对应 Agent。
            if not agent:  # 如果任务要求的 Agent 没有注册，跳过该任务，避免运行时报错。
                continue  # 继续处理下一个 AgentTask。
            ctx.agent_results.append(agent.run(task, self.kb_store, ctx.plan))  # 执行 Agent，让它读取 profiles 并返回结构化证据 AgentEvidence。

        ctx.used_profiles = sorted({pid for result in ctx.agent_results for pid in result.used_profiles})  # 汇总所有 Agent 实际使用过的 profile_id，并去重排序。
        ctx.warnings = [warning for result in ctx.agent_results for warning in result.warnings]  # 汇总所有 Agent 产生的 warning，例如 profile 类型不匹配或缺失。
        ctx.answer = self.synthesizer.synthesize(ctx)  # 调用 Synthesizer，把 AgentEvidence 合成为最终回答。
        return ctx  # 返回完整 RAGContext，包含 query、plan、documents、knowledge_hits、agent_tasks、agent_results 和 answer。

