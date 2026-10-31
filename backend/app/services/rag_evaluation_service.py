"""
Offline RAG evaluation engine.

All metrics are pure-Python — no live LLM or vector database calls needed.

Metrics
-------
context_precision  : fraction of retrieved docs that contain the expected answer
faithfulness       : fraction of answer tokens that appear in the retrieved context
answer_similarity  : character-level Jaccard similarity between expected and generated answer
"""
from __future__ import annotations


import string

_PUNCT = set(string.punctuation)


def _token_set(text: str) -> set[str]:
    """Lower-case word tokens, stripping surrounding punctuation and filtering empty strings."""
    tokens = set()
    for w in text.split():
        cleaned = w.lower().strip(string.punctuation)
        if cleaned:
            tokens.add(cleaned)
    return tokens


class RagEvaluator:

    @staticmethod
    def context_precision(expected_answer: str, retrieved_docs: list[str]) -> float:
        """
        Proportion of retrieved documents that contain at least one word
        from the expected answer.

        Returns 1.0 if retrieved_docs is empty (vacuous truth, nothing was wrong).
        """
        if not retrieved_docs:
            return 1.0
        answer_tokens = _token_set(expected_answer)
        hits = sum(
            1
            for doc in retrieved_docs
            if _token_set(doc) & answer_tokens  # non-empty intersection
        )
        return hits / len(retrieved_docs)

    @staticmethod
    def faithfulness(generated_answer: str, retrieved_docs: str | list[str]) -> float:
        """
        Fraction of generated-answer tokens that appear in the retrieved context.

        `retrieved_docs` may be a list of strings or a single string.
        Returns 1.0 if the generated answer is empty.
        """
        if isinstance(retrieved_docs, list):
            context = " ".join(retrieved_docs)
        else:
            context = retrieved_docs

        answer_tokens = _token_set(generated_answer)
        if not answer_tokens:
            return 1.0

        context_tokens = _token_set(context)
        supported = answer_tokens & context_tokens
        return len(supported) / len(answer_tokens)

    @staticmethod
    def answer_similarity(expected_answer: str, generated_answer: str) -> float:
        """
        Character-level Jaccard similarity between expected and generated answers.

        Returns 1.0 if both strings are empty.
        """
        exp = set(expected_answer.lower())
        gen = set(generated_answer.lower())
        if not exp and not gen:
            return 1.0
        intersection = exp & gen
        union = exp | gen
        return len(intersection) / len(union)

    @classmethod
    def evaluate(
        cls,
        question: str,  # noqa: ARG003 — kept for API symmetry
        expected_answer: str,
        retrieved_docs: list[str],
        generated_answer: str,
    ) -> dict[str, float]:
        """
        Compute all three metrics and return a result dict.

        All scores are in [0.0, 1.0].
        """
        return {
            "context_precision": cls.context_precision(expected_answer, retrieved_docs),
            "faithfulness": cls.faithfulness(generated_answer, retrieved_docs),
            "answer_similarity": cls.answer_similarity(expected_answer, generated_answer),
        }
