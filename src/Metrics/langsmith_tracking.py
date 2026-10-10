"""LangSmith-traced RAG pipeline with token, cost, and latency tracking.

Each stage (retrieve, rerank, generate) is wrapped in ``@traceable`` so it
appears as a nested span in LangSmith. LangSmith times every span automatically;
on top of that we attach token usage and estimated USD cost to the LLM span.

Tracing is controlled by the standard LangSmith environment variables
(LANGSMITH_TRACING, LANGSMITH_API_KEY, LANGSMITH_PROJECT). If tracing is off,
these functions still run normally and simply record nothing.
"""

import os
import time

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langsmith import traceable

from src.prompt import PROMPT

load_dotenv()
os.environ.setdefault("LANGSMITH_PROJECT", "swiftvisa")

# USD per 1,000,000 tokens. Update as provider pricing changes.
MODEL_PRICING = {
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
}


def estimate_cost(model_name, input_tokens, output_tokens):
    """Return (input_cost, output_cost, total_cost) in USD for a model call."""
    pricing = MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})
    input_cost = input_tokens / 1_000_000 * pricing["input"]
    output_cost = output_tokens / 1_000_000 * pricing["output"]
    return input_cost, output_cost, input_cost + output_cost


def _token_usage(message):
    """Extract (input_tokens, output_tokens) from a LangChain AIMessage."""
    usage = getattr(message, "usage_metadata", None) or {}
    if usage:
        return int(usage.get("input_tokens", 0)), int(usage.get("output_tokens", 0))

    # Fallback for providers that only fill response_metadata.
    token_usage = (getattr(message, "response_metadata", {}) or {}).get("token_usage", {})
    return int(token_usage.get("prompt_tokens", 0)), int(token_usage.get("completion_tokens", 0))


@traceable(name="retrieve", run_type="retriever")
def traced_retrieve(query, k=3):
    """Similarity search over the FAISS vector store."""
    from src.retriver import visa_retriver_instance

    return visa_retriver_instance.similarity_search(query, k=k)


@traceable(name="rerank", run_type="chain")
def traced_rerank(query, docs):
    """Cross-encoder reranking. Returns [(score, doc), ...]."""
    from src.reranker import predict_reranker

    return predict_reranker(query, docs)


@traceable(name="generate", run_type="llm")
def traced_generate(prompt):
    """LLM generation with token usage and estimated cost."""
    from src.llm_model import llm

    start = time.perf_counter()
    message = llm.invoke(prompt)
    latency_s = time.perf_counter() - start

    model_name = getattr(llm, "model_name", None) or getattr(llm, "model", "")
    input_tokens, output_tokens = _token_usage(message)
    input_cost, output_cost, total_cost = estimate_cost(model_name, input_tokens, output_tokens)

    return {
        "answer": message.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_cost_usd": total_cost,
        "generation_latency_s": latency_s,
    }


@traceable(name="swiftvisa_pipeline", run_type="chain")
def traced_pipeline(query, k=3):
    """Full RAG pipeline: retrieve -> rerank -> generate.

    Returns a dict with the answer, reranked docs, and per-call telemetry
    (tokens, cost, latency). All stages appear as nested spans in LangSmith.
    """
    start = time.perf_counter()

    docs = traced_retrieve(query, k=k)
    reranked_docs = traced_rerank(query, docs)
    top_document = reranked_docs[0][1].page_content if reranked_docs else ""

    prompt = PromptTemplate.from_template(PROMPT).format(
        user_input=query,
        retrieved_documents=top_document,
    )
    generation = traced_generate(prompt)

    telemetry = {k: v for k, v in generation.items() if k != "answer"}
    telemetry["pipeline_latency_s"] = time.perf_counter() - start

    return {
        "query": query,
        "answer": generation["answer"],
        "reranked_docs": reranked_docs,
        "telemetry": telemetry,
    }
