"""
Tests for the RAG evaluation framework.

All tests are pure offline — no live LLM or vector database calls.
"""
import pytest
from app.services.rag_evaluation_service import RagEvaluator
from tests.rag_fixtures import GOLDEN_DATASET


# ──────────────────────────────────────────────
# Context Precision
# ──────────────────────────────────────────────

class TestContextPrecision:
    def test_perfect_precision(self):
        """All docs contain a word from the expected answer → 1.0."""
        docs = ["the quick brown fox", "fox jumped over the lazy dog"]
        score = RagEvaluator.context_precision("fox", docs)
        assert score == 1.0

    def test_zero_precision(self):
        """No docs contain any word from the expected answer → 0.0."""
        docs = ["unrelated text here", "another unrelated sentence"]
        score = RagEvaluator.context_precision("authentication token jwt", docs)
        assert score == 0.0

    def test_partial_precision(self):
        """Half docs relevant → 0.5."""
        docs = ["VectorStore PostgreSQL pgvector", "completely different content"]
        score = RagEvaluator.context_precision("VectorStore", docs)
        assert score == 0.5

    def test_empty_docs(self):
        """No retrieved docs → vacuous 1.0."""
        score = RagEvaluator.context_precision("anything", [])
        assert score == 1.0


# ──────────────────────────────────────────────
# Faithfulness
# ──────────────────────────────────────────────

class TestFaithfulness:
    def test_full_faithfulness(self):
        """Generated answer tokens all present in context → 1.0."""
        context = ["The GeminiClient retries on 500 and 503 errors with a delay."]
        answer = "GeminiClient retries on 500 errors"
        score = RagEvaluator.faithfulness(answer, context)
        assert score == 1.0

    def test_hallucination(self):
        """Generated answer mentions things absent from context → low score."""
        context = ["The repository stores code in the file system."]
        answer = "The system uses AWS Lambda with DynamoDB and SQS"
        score = RagEvaluator.faithfulness(answer, context)
        assert score < 0.3

    def test_string_context(self):
        """faithfulness accepts a raw string as context."""
        context = "VectorStore uses PostgreSQL pgvector for embeddings"
        answer = "VectorStore PostgreSQL"
        score = RagEvaluator.faithfulness(answer, context)
        assert score == 1.0

    def test_empty_answer(self):
        """Empty generated answer → vacuous 1.0."""
        score = RagEvaluator.faithfulness("", ["some context"])
        assert score == 1.0


# ──────────────────────────────────────────────
# Answer Similarity
# ──────────────────────────────────────────────

class TestAnswerSimilarity:
    def test_exact_match(self):
        """Identical strings → Jaccard == 1.0."""
        answer = "The collection is named codepilot"
        score = RagEvaluator.answer_similarity(answer, answer)
        assert score == 1.0

    def test_completely_different(self):
        """Completely disjoint character sets → score < 0.5."""
        score = RagEvaluator.answer_similarity("abc", "xyz")
        assert score < 0.5

    def test_partial_overlap(self):
        """Partial overlap → score between 0 and 1."""
        score = RagEvaluator.answer_similarity("hello world", "hello there")
        assert 0.0 < score < 1.0

    def test_both_empty(self):
        """Both empty → 1.0."""
        score = RagEvaluator.answer_similarity("", "")
        assert score == 1.0


# ──────────────────────────────────────────────
# evaluate() composite
# ──────────────────────────────────────────────

class TestEvaluateComposite:
    def test_all_scores_in_range(self):
        """evaluate() output must be in [0.0, 1.0] for any reasonable input."""
        result = RagEvaluator.evaluate(
            question="Where is the collection created?",
            expected_answer="VectorStore stores embeddings in the PostgreSQL repository_embeddings table",
            retrieved_docs=[
                "class VectorStore:\n"
                "    def __init__(self):\n"
                "        self.store = repository_embeddings in PostgreSQL\n"
            ],
            generated_answer=(
                "PostgreSQL repository_embeddings stores vectors in VectorStore."
            ),
        )
        for key, score in result.items():
            assert 0.0 <= score <= 1.0, f"{key} out of range: {score}"

    def test_keys_present(self):
        """evaluate() must return all three keys."""
        result = RagEvaluator.evaluate("q", "a", ["ctx"], "gen")
        assert set(result.keys()) == {"context_precision", "faithfulness", "answer_similarity"}

    def test_mocked_rag_pipeline_end_to_end(self, mocker):
        """
        Mock SearchService and GeminiClient; verify that RagEvaluator can score
        the output correctly.
        """
        from app.services.search_service import SearchService
        from app.ai.llm import GeminiClient

        fixture = GOLDEN_DATASET[0]
        fake_search_result = {
            "documents": [fixture["context_docs"]],
            "metadatas": [[{"path": "vector_store.py", "start": 1, "end": 15}]],
        }
        mocker.patch.object(SearchService, "search", return_value=fake_search_result)
        mocker.patch.object(GeminiClient, "generate", return_value=fixture["expected_answer"])

        # Mimic what RAGService.ask() does (without hitting live services)
        search_results = SearchService.search(fixture["question"], repository_id=1)
        documents = search_results["documents"][0]
        generated = GeminiClient().generate("mock-prompt")

        result = RagEvaluator.evaluate(
            question=fixture["question"],
            expected_answer=fixture["expected_answer"],
            retrieved_docs=documents,
            generated_answer=generated,
        )

        assert result["context_precision"] > 0.5
        assert result["faithfulness"] > 0.5
        assert result["answer_similarity"] == 1.0  # identical strings


# ──────────────────────────────────────────────
# Golden dataset parametrized
# ──────────────────────────────────────────────

@pytest.mark.parametrize("fixture", GOLDEN_DATASET, ids=[f["question"][:40] for f in GOLDEN_DATASET])
def test_golden_dataset_precision_above_zero(fixture):
    """Context precision should be > 0 for every golden entry (context is relevant)."""
    score = RagEvaluator.context_precision(fixture["expected_answer"], fixture["context_docs"])
    assert score > 0.0, f"Context precision is 0 for: {fixture['question']}"
