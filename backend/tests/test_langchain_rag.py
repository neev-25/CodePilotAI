from langchain_core.messages import AIMessage
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.chunker import CodeChunker
from app.ai.llm import GeminiClient
from app.ai.vector_store import VectorStore
from app.database.database import Base
from app.services.rag_service import RAGService
from app.services.search_service import SearchService


def test_code_chunker_uses_langchain_splitter_and_preserves_line_metadata(monkeypatch):
    monkeypatch.setattr(CodeChunker, "CHUNK_SIZE", 24)
    monkeypatch.setattr(CodeChunker, "OVERLAP", 5)
    content = "line one\nline two\nline three\nline four"

    chunks = CodeChunker.chunk({"path": "src/example.py", "content": content})

    assert len(chunks) > 1
    assert chunks[0]["path"] == "src/example.py"
    assert chunks[0]["start_line"] == 1
    assert chunks[1]["start_line"] > chunks[0]["start_line"]
    assert all(chunk["start_line"] <= chunk["end_line"] for chunk in chunks)


def test_postgres_vector_store_supports_incremental_repository_operations(monkeypatch):
    sqlite_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=sqlite_engine)
    test_session = sessionmaker(bind=sqlite_engine)

    class FakeEmbeddingModel:
        def encode(self, texts):
            return [[1.0, 0.0, 0.0] for _ in texts]

        def embed_query(self, text):
            return [1.0, 0.0, 0.0]

        @property
        def batch_size(self):
            return 5

        def iter_encode(self, texts, **kwargs):
            yield 1, 1, self.encode(texts), len(texts)

    monkeypatch.setattr("app.ai.vector_store.EmbeddingModel", FakeEmbeddingModel)
    monkeypatch.setattr(
        "app.ai.vector_store.engine",
        SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
    )
    monkeypatch.setattr("app.ai.vector_store.SessionLocal", test_session)

    store = VectorStore()
    chunks = [
        {
            "path": "src/app.py",
            "start_line": 1,
            "end_line": 1,
            "content": "def answer(): pass",
        }
    ]

    store.add_chunks(repository_id=7, chunks=chunks)
    assert store.repository_count(7) == 1

    previous_ids = store.file_chunk_ids(7, {"src/app.py"})
    updated_chunks = [
        {
            **chunks[0],
            "content": "def answer(): return 42",
        }
    ]
    updated_ids = store.add_chunks(repository_id=7, chunks=updated_chunks)
    store.delete_ids([chunk_id for chunk_id in previous_ids if chunk_id not in updated_ids])
    assert store.repository_count(7) == 1

    store.delete_file_chunks(7, {"src/app.py"})
    assert store.repository_count(7) == 0

    store.add_chunks(repository_id=7, chunks=chunks)
    assert store.repository_chunk_ids(7)
    store.delete_repository(7)
    assert store.repository_count(7) == 0
    sqlite_engine.dispose()


def test_vector_store_rejects_sqlite_for_embeddings(monkeypatch):
    monkeypatch.setattr(
        "app.ai.vector_store.engine",
        SimpleNamespace(dialect=SimpleNamespace(name="sqlite")),
    )

    with pytest.raises(RuntimeError, match="require PostgreSQL"):
        VectorStore()


def test_vector_store_returns_existing_search_response_shape(monkeypatch):
    class FakeQuery:
        def filter(self, *args):
            return self

        def order_by(self, *args):
            return self

        def limit(self, *args):
            return self

        def all(self):
            return [
                (
                    SimpleNamespace(
                        content="def answer(): pass",
                        path="src/app.py",
                        start_line=2,
                        end_line=2,
                    ),
                    0.25,
                )
            ]

    class FakeSession:
        def query(self, *args):
            return FakeQuery()

        def close(self):
            pass

    class FakeEmbeddingModel:
        def encode(self, texts):
            return []

        def embed_query(self, text):
            return [1.0, 0.0, 0.0]

    monkeypatch.setattr(
        "app.ai.vector_store.engine",
        SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
    )
    monkeypatch.setattr("app.ai.vector_store.SessionLocal", FakeSession)
    monkeypatch.setattr("app.ai.vector_store.EmbeddingModel", FakeEmbeddingModel)

    results = VectorStore().search(repository_id=7, query="answer function")

    assert results == {
        "documents": [["def answer(): pass"]],
        "metadatas": [[{"path": "src/app.py", "start": 2, "end": 2}]],
        "distances": [[0.25]],
    }


def test_rag_service_preserves_answer_and_source_contract(mocker):
    mocker.patch.object(
        SearchService,
        "search",
        return_value={
            "documents": [["def answer(): pass"]],
            "metadatas": [[{"path": r"src\app.py", "start": 2, "end": 2}]],
        },
    )
    mocker.patch(
        "app.services.rag_service.GeminiClient.generate",
        return_value="The answer is in app.py.",
    )

    result = RAGService.ask("Where is answer defined?", repository_id=7)

    assert result == {
        "answer": "The answer is in app.py.",
        "sources": [
            {
                "file": "src/app.py",
                "start_line": 2,
                "end_line": 2,
                "snippet": "def answer(): pass",
            }
        ],
    }


def test_gemini_client_fails_over_between_langchain_models(mocker):
    attempted_models = []

    class FakeChatModel:
        def __init__(self, **options):
            self.model = options["model"]

        def invoke(self, prompt):
            attempted_models.append(self.model)
            if self.model == "primary":
                raise RuntimeError("429 RESOURCE_EXHAUSTED")
            return AIMessage(content="response")

    mocker.patch("app.ai.llm.ChatGoogleGenerativeAI", FakeChatModel)
    mocker.patch.object(GeminiClient, "FALLBACK_MODELS", ["primary", "fallback"])

    assert GeminiClient().generate("prompt") == "response"
    assert attempted_models == ["primary", "fallback"]


def test_gemini_client_uses_current_stable_flash_models():
    assert GeminiClient.FALLBACK_MODELS == [
        "gemini-3.8-flash",
        "gemini-3.6-flash",
    ]


def test_gemini_client_fails_over_when_a_configured_model_is_not_found(mocker):
    attempted_models = []

    class FakeChatModel:
        def __init__(self, **options):
            self.model = options["model"]

        def invoke(self, prompt):
            attempted_models.append(self.model)
            if self.model == "primary":
                raise RuntimeError("404 NOT_FOUND")
            return AIMessage(content="response")

    mocker.patch("app.ai.llm.ChatGoogleGenerativeAI", FakeChatModel)
    mocker.patch.object(GeminiClient, "FALLBACK_MODELS", ["primary", "fallback"])

    assert GeminiClient().generate("prompt") == "response"
    assert attempted_models == ["primary", "fallback"]
