"""LangSmith evaluation harness for the SwiftVisa RAG pipeline.

Runs the traced pipeline over the versioned LangSmith dataset and scores each
example with:

  Retrieval metrics  - precision@k / recall@k / hit_rate@k / MRR@k, by comparing
                       the retrieved (country, visa_type) against the expected
                       labels (RetrievalMetric).
  Generation metrics - keyword coverage (lexical, offline) and LLM-judged
                       faithfulness + answer relevance (LLMJudgeMetric).
  Telemetry          - total tokens, total cost (USD), and pipeline latency are
                       attached as feedback scores so they show up alongside
                       quality metrics in LangSmith.

Usage:
    python -m src.Metrics.evalution

Requires LANGSMITH_API_KEY and GROQ_API_KEY in the environment.
"""

import os

from dotenv import load_dotenv
from langsmith import evaluate

from src.Metrics.Generation_Metric import LexicalMetric, LLMJudgeMetric
from src.Metrics.langsmith_tracking import traced_pipeline
from src.Metrics.Retrival_metric import RetrievalMetric

load_dotenv()

os.environ.setdefault("LANGSMITH_PROJECT", "swiftvisa")

DATASET_NAME = "swiftvisa-eval"
DEFAULT_K = 3


# --------------------------------------------------------------------------- #
# Target: the system under test. Receives dataset inputs, returns the output   #
# that evaluators will score. This runs the fully traced pipeline.             #
# --------------------------------------------------------------------------- #
def pipeline_target(inputs):
    result = traced_pipeline(inputs["query"], k=DEFAULT_K)
    reranked = result["reranked_docs"]

    retrieved_country = retrieved_visa = None
    if reranked:
        top_meta = reranked[0][1].metadata
        retrieved_country = top_meta.get("country")
        retrieved_visa = top_meta.get("visa_type")

    return {
        "answer": result["answer"],
        "retrieved_country": retrieved_country,
        "retrieved_visa_type": retrieved_visa,
        "retrieved_labels": [
            (doc.metadata.get("country"), doc.metadata.get("visa_type"))
            for _, doc in reranked
        ],
        "retrieved_context": "\n\n".join(doc.page_content for _, doc in reranked),
        "telemetry": result["telemetry"],
    }


# --------------------------------------------------------------------------- #
# Retrieval evaluators                                                         #
# --------------------------------------------------------------------------- #
def _retrieval_metric(outputs, reference_outputs):
    expected = (
        reference_outputs.get("expected_country"),
        reference_outputs.get("expected_visa_type"),
    )
    retrieved = outputs.get("retrieved_labels", [])
    return RetrievalMetric(
        retrieved_ids=retrieved,
        ground_truth_ids=[expected],
        k=DEFAULT_K,
    )


def retrieval_precision(outputs, reference_outputs):
    return {"key": "precision@k", "score": _retrieval_metric(outputs, reference_outputs).precision_at_k()}


def retrieval_recall(outputs, reference_outputs):
    return {"key": "recall@k", "score": _retrieval_metric(outputs, reference_outputs).recall_at_k()}


def retrieval_hit_rate(outputs, reference_outputs):
    return {"key": "hit_rate@k", "score": _retrieval_metric(outputs, reference_outputs).hit_rate_at_k()}


def retrieval_mrr(outputs, reference_outputs):
    return {"key": "mrr@k", "score": _retrieval_metric(outputs, reference_outputs).mrr_at_k()}


# --------------------------------------------------------------------------- #
# Generation evaluators                                                        #
# --------------------------------------------------------------------------- #
def keyword_coverage(outputs, reference_outputs):
    keywords = reference_outputs.get("expected_keywords", [])
    lexical = LexicalMetric(prediction=outputs.get("answer", ""), reference="")
    return {"key": "keyword_coverage", "score": lexical.keyword_coverage(keywords)}


def faithfulness(outputs, reference_outputs):
    from src.llm_model import llm

    judge = LLMJudgeMetric(llm)
    result = judge.faithfulness(outputs.get("retrieved_context", ""), outputs.get("answer", ""))
    return {"key": "faithfulness", "score": result["score"], "comment": result["reason"]}


def answer_relevance(inputs, outputs):
    from src.llm_model import llm

    judge = LLMJudgeMetric(llm)
    result = judge.answer_relevance(inputs.get("query", ""), outputs.get("answer", ""))
    return {"key": "answer_relevance", "score": result["score"], "comment": result["reason"]}


# --------------------------------------------------------------------------- #
# Telemetry evaluators (token / cost / latency as feedback scores)             #
# --------------------------------------------------------------------------- #
def total_tokens(outputs):
    return {"key": "total_tokens", "score": outputs.get("telemetry", {}).get("total_tokens", 0)}


def total_cost_usd(outputs):
    return {"key": "total_cost_usd", "score": outputs.get("telemetry", {}).get("total_cost_usd", 0.0)}


def pipeline_latency(outputs):
    return {"key": "pipeline_latency_s", "score": outputs.get("telemetry", {}).get("pipeline_latency_s", 0.0)}


EVALUATORS = [
    retrieval_precision,
    retrieval_recall,
    retrieval_hit_rate,
    retrieval_mrr,
    keyword_coverage,
    faithfulness,
    answer_relevance,
    total_tokens,
    total_cost_usd,
    pipeline_latency,
]


def run_evaluation(dataset_name=DATASET_NAME, experiment_prefix="swiftvisa-eval"):
    """Run the LangSmith evaluation experiment and return the results handle."""
    return evaluate(
        pipeline_target,
        data=dataset_name,
        evaluators=EVALUATORS,
        experiment_prefix=experiment_prefix,
        metadata={"k": DEFAULT_K},
    )


if __name__ == "__main__":
    results = run_evaluation()
    print("Evaluation submitted to LangSmith.")
    print(results)
