"""Retrieval evaluation metrics for the SwiftVisa RAG pipeline.

Given the IDs returned by the retriever and the set of relevant (ground-truth)
IDs for a query, these metrics measure how good the retrieval step is.
"""


class RetrievalMetric:
    """Compute standard top-k retrieval metrics for a single query.

    Args:
        retrieved_ids: IDs returned by the retriever, ordered best-first.
        ground_truth_ids: IDs that are actually relevant for the query.
        k: Cut-off rank; only the first ``k`` retrieved IDs are considered.
    """

    def __init__(self, retrieved_ids, ground_truth_ids, k):
        self.retrieved_ids = list(retrieved_ids)
        self.ground_truth = set(ground_truth_ids)
        self.k = k

    @property
    def _top_k(self):
        return self.retrieved_ids[: self.k]

    def _relevant_hits(self):
        """Number of top-k retrieved IDs that are relevant."""
        return sum(1 for doc_id in self._top_k if doc_id in self.ground_truth)

    def precision_at_k(self):
        """Fraction of the top-k retrieved documents that are relevant."""
        if self.k == 0:
            return 0.0
        return self._relevant_hits() / self.k

    def recall_at_k(self):
        """Fraction of all relevant documents found within the top-k."""
        if not self.ground_truth:
            return 0.0
        return self._relevant_hits() / len(self.ground_truth)

    def hit_rate_at_k(self):
        """1.0 if at least one relevant document is in the top-k, else 0.0."""
        return 1.0 if self._relevant_hits() > 0 else 0.0

    def mrr_at_k(self):
        """Mean Reciprocal Rank: 1 / rank of the first relevant document."""
        for rank, doc_id in enumerate(self._top_k, start=1):
            if doc_id in self.ground_truth:
                return 1.0 / rank
        return 0.0

    def as_dict(self):
        """Return all metrics as a dictionary."""
        return {
            "k": self.k,
            "precision@k": self.precision_at_k(),
            "recall@k": self.recall_at_k(),
            "hit_rate@k": self.hit_rate_at_k(),
            "mrr@k": self.mrr_at_k(),
        }
