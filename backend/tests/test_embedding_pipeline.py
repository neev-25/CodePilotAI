from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.embedding_rate_limiter import (
    EmbeddingConfigurationError,
    estimate_tokens,
    rate_limiter,
)
from app.ai.embeddings import EmbeddingModel, EmbeddingQuotaError
from app.ai.vector_store import VectorStore
from app.database.database import Base
from app.services.indexing_job_service import IndexingJobService


def configure_embedding_model(monkeypatch, provider):
    monkeypatch.setattr(
        "app.ai.embeddings.GoogleGenerativeAIEmbeddings",
        lambda **kwargs: provider,
    )
    monkeypatch.setattr(
        "app.ai.embeddings.rate_limiter.reserve",
        lambda token_count, **kwargs: None,
    )
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_BATCH_SIZE", 2)
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_BATCH_DELAY", 0)
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_MAX_RETRIES", 1)
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_INITIAL_BACKOFF", 0.1)
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_MAX_BACKOFF", 1)
    return EmbeddingModel()


def test_token_estimate_and_budget_guard_are_explicit(monkeypatch):
    assert estimate_tokens("abcdefgh") == 3
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_TOKENS_PER_MINUTE", 2)

    with pytest.raises(EmbeddingConfigurationError, match="exceeds the configured"):
        rate_limiter.reserve(3)


def test_embedding_batches_keep_input_order_and_skip_empty_input(monkeypatch):
    class FakeProvider:
        def __init__(self):
            self.batches = []

        def embed_documents(self, texts):
            self.batches.append(list(texts))
            return [[float(text)] for text in texts]

    provider = FakeProvider()
    model = configure_embedding_model(monkeypatch, provider)

    assert model.encode([]) == []
    assert model.encode(["1", "2", "3", "4", "5"]) == [
        [1.0],
        [2.0],
        [3.0],
        [4.0],
        [5.0],
    ]
    assert provider.batches == [["1", "2"], ["3", "4"], ["5"]]


def test_embedding_retries_429_using_google_retry_delay(monkeypatch):
    class FakeProvider:
        def __init__(self):
            self.calls = 0

        def embed_documents(self, texts):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("429 RESOURCE_EXHAUSTED retryDelay': '0.25s'")
            return [[1.0] for _ in texts]

    provider = FakeProvider()
    model = configure_embedding_model(monkeypatch, provider)
    delays = []
    monkeypatch.setattr("app.ai.embeddings.time.sleep", delays.append)

    assert model.encode(["source"]) == [[1.0]]
    assert provider.calls == 2
    assert delays == [0.25]


def test_embedding_stops_after_maximum_retry_count(monkeypatch):
    class FakeProvider:
        calls = 0

        def embed_documents(self, texts):
            self.calls += 1
            raise RuntimeError("429 RESOURCE_EXHAUSTED")

    provider = FakeProvider()
    model = configure_embedding_model(monkeypatch, provider)
    monkeypatch.setattr("app.ai.embeddings.time.sleep", lambda _: None)

    with pytest.raises(EmbeddingQuotaError, match="after 1 retries"):
        model.encode(["source"])
    assert provider.calls == 2


def test_permanent_embedding_error_is_not_retried(monkeypatch):
    class FakeProvider:
        calls = 0

        def embed_documents(self, texts):
            self.calls += 1
            raise RuntimeError("403 invalid API key")

    provider = FakeProvider()
    model = configure_embedding_model(monkeypatch, provider)

    with pytest.raises(RuntimeError, match="invalid API key"):
        model.encode(["source"])
    assert provider.calls == 1


def test_embedding_timeout_is_retried(monkeypatch):
    class FakeProvider:
        calls = 0

        def embed_documents(self, texts):
            self.calls += 1
            if self.calls == 1:
                raise TimeoutError("request timed out")
            return [[2.0] for _ in texts]

    provider = FakeProvider()
    model = configure_embedding_model(monkeypatch, provider)
    monkeypatch.setattr("app.ai.embeddings.time.sleep", lambda _: None)

    assert model.encode(["source"]) == [[2.0]]
    assert provider.calls == 2


def test_indexing_releases_initial_session_and_finalizes_with_fresh_sessions(monkeypatch):
    class FakeSession:
        def __init__(self, values=()):
            self.values = iter(values)
            self.closed = False

        def get(self, _model, _record_id):
            return next(self.values)

        def commit(self):
            pass

        def close(self):
            self.closed = True

    job = SimpleNamespace(
        status="PENDING",
        message="",
        result_json=None,
        completed_at=None,
    )
    repository = SimpleNamespace(local_path="repo", status="PENDING")
    initial_session = FakeSession((job, repository))
    cache_session = FakeSession()
    final_session = FakeSession((job, repository))
    sessions = iter((initial_session, cache_session, final_session))
    monkeypatch.setattr(
        "app.services.indexing_job_service.SessionLocal",
        lambda: next(sessions),
    )
    monkeypatch.setattr(
        "app.services.indexing_job_service.AnalysisCacheService.invalidate_repository",
        lambda _db, _repository_id: None,
    )

    def index(repository_id, repository_path, *, job_id, progress):
        assert initial_session.closed
        assert repository_id == 7
        assert repository_path == "repo"
        assert job_id == 11
        assert callable(progress)
        return {"indexed_files": 2}

    monkeypatch.setattr(
        "app.services.indexing_job_service.IndexingService.index",
        index,
    )

    IndexingJobService.run(job_id=11, repository_id=7)

    assert initial_session.closed
    assert cache_session.closed
    assert final_session.closed
    assert repository.status == "INDEXED"
    assert job.status == "COMPLETED"
    assert job.result_json == '{"state": "completed", "indexed_files": 2}'


def test_embedding_count_mismatch_fails_clearly(monkeypatch):
    class FakeProvider:
        def embed_documents(self, texts):
            return []

    model = configure_embedding_model(monkeypatch, FakeProvider())
    with pytest.raises(RuntimeError, match="different number"):
        model.encode(["one"])


def test_partial_vector_batches_resume_without_reembedding_saved_chunks(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine)
    monkeypatch.setattr(
        "app.ai.vector_store.engine",
        SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
    )
    monkeypatch.setattr("app.ai.vector_store.SessionLocal", test_session)
    monkeypatch.setattr("app.core.config.settings.EMBEDDING_BATCH_SIZE", 1)

    class FakeEmbeddingModel:
        calls = []
        fail_once = True

        def __init__(self):
            self.batch_size = 1

        def iter_encode(self, texts, **kwargs):
            self.calls.append(list(texts))
            total = len(texts)
            for index, value in enumerate(texts, start=1):
                yield index, total, [[float(index)]], 1
                if self.fail_once:
                    type(self).fail_once = False
                    raise RuntimeError("simulated interruption")

        def encode(self, texts):
            return [[1.0] for _ in texts]

        def embed_query(self, text):
            return [1.0]

    monkeypatch.setattr("app.ai.vector_store.EmbeddingModel", FakeEmbeddingModel)
    chunks = [
        {
            "path": "main.py",
            "start_line": index,
            "end_line": index,
            "content": f"chunk-{index}",
        }
        for index in range(1, 4)
    ]

    store = VectorStore()
    with pytest.raises(RuntimeError, match="simulated interruption"):
        store.add_chunks(9, chunks)

    assert store.repository_count(9) == 1
    store.add_chunks(9, chunks)

    assert store.repository_count(9) == 3
    assert FakeEmbeddingModel.calls == [
        ["chunk-1", "chunk-2", "chunk-3"],
        ["chunk-2", "chunk-3"],
    ]
    test_engine.dispose()
