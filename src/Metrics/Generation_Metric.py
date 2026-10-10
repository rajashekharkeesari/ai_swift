"""Generation evaluation metrics for the SwiftVisa RAG pipeline.

Two families of metrics are provided:

1. LexicalMetric  - deterministic, dependency-free overlap metrics that compare
   a generated answer against a reference answer (token F1, exact match,
   ROUGE-L style LCS, keyword coverage).
2. LLMJudgeMetric - uses the project's Groq LLM to score faithfulness and
   answer relevance (the metrics that cannot be measured by overlap alone).
"""

import json
import re


def _tokenize(text):
    """Lowercase and split text into word tokens."""
    return re.findall(r"\w+", (text or "").lower())


class LexicalMetric:
    """Overlap-based comparison of a generated answer to a reference answer.

    Args:
        prediction: The generated answer.
        reference: The gold / expected answer.
    """

    def __init__(self, prediction, reference):
        self.prediction = prediction or ""
        self.reference = reference or ""
        self._pred_tokens = _tokenize(self.prediction)
        self._ref_tokens = _tokenize(self.reference)

    def exact_match(self):
        """1.0 if normalized prediction equals normalized reference, else 0.0."""
        return 1.0 if self.prediction.strip().lower() == self.reference.strip().lower() else 0.0

    def token_f1(self):
        """Token-overlap F1 between prediction and reference."""
        if not self._pred_tokens or not self._ref_tokens:
            return 0.0

        common = 0
        ref_counts = {}
        for tok in self._ref_tokens:
            ref_counts[tok] = ref_counts.get(tok, 0) + 1
        for tok in self._pred_tokens:
            if ref_counts.get(tok, 0) > 0:
                common += 1
                ref_counts[tok] -= 1

        if common == 0:
            return 0.0

        precision = common / len(self._pred_tokens)
        recall = common / len(self._ref_tokens)
        return 2 * precision * recall / (precision + recall)

    def rouge_l(self):
        """ROUGE-L style F1 based on the longest common subsequence."""
        if not self._pred_tokens or not self._ref_tokens:
            return 0.0

        lcs = self._lcs_length(self._pred_tokens, self._ref_tokens)
        if lcs == 0:
            return 0.0

        precision = lcs / len(self._pred_tokens)
        recall = lcs / len(self._ref_tokens)
        return 2 * precision * recall / (precision + recall)

    def keyword_coverage(self, keywords):
        """Fraction of the given keywords that appear in the prediction."""
        if not keywords:
            return 0.0
        pred_lower = self.prediction.lower()
        hits = sum(1 for kw in keywords if kw.lower() in pred_lower)
        return hits / len(keywords)

    @staticmethod
    def _lcs_length(a, b):
        """Length of the longest common subsequence of two token lists."""
        rows, cols = len(a) + 1, len(b) + 1
        table = [[0] * cols for _ in range(rows)]
        for i in range(1, rows):
            for j in range(1, cols):
                if a[i - 1] == b[j - 1]:
                    table[i][j] = table[i - 1][j - 1] + 1
                else:
                    table[i][j] = max(table[i - 1][j], table[i][j - 1])
        return table[-1][-1]

    def as_dict(self, keywords=None):
        """Return all lexical metrics as a dictionary."""
        result = {
            "exact_match": self.exact_match(),
            "token_f1": self.token_f1(),
            "rouge_l": self.rouge_l(),
        }
        if keywords is not None:
            result["keyword_coverage"] = self.keyword_coverage(keywords)
        return result


class LLMJudgeMetric:
    """Use an LLM to score generation quality that overlap metrics cannot capture.

    - faithfulness: is the answer grounded in the retrieved context?
    - answer_relevance: does the answer actually address the question?

    Args:
        llm: A chat model with an ``.invoke(prompt)`` method returning an object
            with a ``.content`` attribute (e.g. the project's Groq ``llm``).
    """

    _FAITHFULNESS_PROMPT = (
        "You are evaluating a RAG system.\n"
        "Given the CONTEXT and the ANSWER, rate how well the answer is supported "
        "by the context, with no unsupported claims.\n"
        "Return ONLY a JSON object: {{\"score\": <float 0..1>, \"reason\": <string>}}\n\n"
        "CONTEXT:\n{context}\n\nANSWER:\n{answer}"
    )

    _RELEVANCE_PROMPT = (
        "You are evaluating a RAG system.\n"
        "Given the QUESTION and the ANSWER, rate how directly the answer "
        "addresses the question.\n"
        "Return ONLY a JSON object: {{\"score\": <float 0..1>, \"reason\": <string>}}\n\n"
        "QUESTION:\n{question}\n\nANSWER:\n{answer}"
    )

    def __init__(self, llm):
        self.llm = llm

    def faithfulness(self, context, answer):
        """Score (0..1) of how grounded the answer is in the context."""
        prompt = self._FAITHFULNESS_PROMPT.format(context=context, answer=answer)
        return self._score(prompt)

    def answer_relevance(self, question, answer):
        """Score (0..1) of how well the answer addresses the question."""
        prompt = self._RELEVANCE_PROMPT.format(question=question, answer=answer)
        return self._score(prompt)

    def _score(self, prompt):
        """Invoke the LLM and parse a {score, reason} JSON response."""
        raw = self.llm.invoke(prompt).content
        return self._parse_score(raw)

    @staticmethod
    def _parse_score(raw):
        """Extract {'score': float, 'reason': str} from a model response."""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {"score": 0.0, "reason": f"Could not parse response: {raw[:200]}"}
        try:
            data = json.loads(match.group(0))
            score = float(data.get("score", 0.0))
            score = max(0.0, min(1.0, score))
            return {"score": score, "reason": data.get("reason", "")}
        except (ValueError, json.JSONDecodeError):
            return {"score": 0.0, "reason": f"Could not parse response: {raw[:200]}"}
