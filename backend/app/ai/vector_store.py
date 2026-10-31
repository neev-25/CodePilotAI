import hashlib
from collections.abc import Callable, Sequence

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.ai.embeddings import EmbeddingModel
from app.core.config import settings
from app.core.logger import logger
from app.database.database import SessionLocal, engine
from app.models.vector_embedding import VectorEmbedding


class VectorStore:
    def __init__(self) -> None:
        if engine.dialect.name != "postgresql":
            raise RuntimeError(
                "Repository embeddings require PostgreSQL with the pgvector extension. "
                "Set DATABASE_URL to a PostgreSQL or Neon connection string."
            )
        self.embeddings = EmbeddingModel()

    @staticmethod
    def _chunk_id(repository_id: int, chunk: dict) -> str:
        digest = hashlib.sha256(
            (
                f"{chunk['path']}:{chunk['start_line']}:"
                f"{chunk['end_line']}:{chunk['content']}"
            ).encode()
        ).hexdigest()
        return f"repo_{repository_id}_{digest}"

    def add_chunks(
        self,
        repository_id: int,
        chunks: Sequence[dict],
        *,
        job_id: int | None = None,
        progress: Callable[[dict], None] | None = None,
    ) -> list[str]:
        if not chunks:
            return []

        ids = [self._chunk_id(repository_id, chunk) for chunk in chunks]
        db = SessionLocal()
        try:
            existing_ids = set()
            for offset in range(0, len(ids), 1000):
                existing_ids.update(
                    chunk_id
                    for (chunk_id,) in db.query(VectorEmbedding.id)
                    .filter(VectorEmbedding.id.in_(ids[offset : offset + 1000]))
                    .all()
                )
        finally:
            db.close()

        pending = [
            (chunk, chunk_id)
            for chunk, chunk_id in zip(chunks, ids)
            if chunk_id not in existing_ids
        ]
        if progress:
            progress(
                {
                    "state": "embedding",
                    "embedded_chunks": len(existing_ids),
                    "total_chunks": len(chunks),
                    "pending_chunks": len(pending),
                    "message": (
                        f"Resuming: reusing {len(existing_ids)} saved chunks; "
                        f"{len(pending)} remain."
                    ),
                }
            )

        def save_batch(rows: list[dict]) -> None:
            db = SessionLocal()
            try:
                insert = (
                    postgresql_insert
                    if db.get_bind().dialect.name == "postgresql"
                    else sqlite_insert
                )
                statement = insert(VectorEmbedding).values(rows)
                db.execute(
                    statement.on_conflict_do_update(
                        index_elements=[VectorEmbedding.id],
                        set_={
                            "repository_id": statement.excluded.repository_id,
                            "path": statement.excluded.path,
                            "start_line": statement.excluded.start_line,
                            "end_line": statement.excluded.end_line,
                            "content": statement.excluded.content,
                            "embedding": statement.excluded.embedding,
                        },
                    )
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        texts = [chunk["content"] for chunk, _ in pending]
        completed_chunks = len(existing_ids)
        for batch_number, total_batches, vectors, tokens in self.embeddings.iter_encode(
            texts,
            repository_id=repository_id,
            job_id=job_id,
            progress=progress,
        ):
            offset = (batch_number - 1) * settings.EMBEDDING_BATCH_SIZE
            batch_chunks = pending[offset : offset + len(vectors)]
            expected_batch_size = min(
                settings.EMBEDDING_BATCH_SIZE,
                len(pending) - offset,
            )
            if len(vectors) != expected_batch_size:
                raise RuntimeError(
                    "Embedding batch did not match its source chunks."
                )
            rows = [
                {
                    "id": chunk_id,
                    "repository_id": repository_id,
                    "path": chunk["path"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"],
                    "embedding": embedding,
                }
                for (chunk, chunk_id), embedding in zip(batch_chunks, vectors)
            ]
            if len(rows) != len(vectors):
                raise RuntimeError("Embedding batch did not match its source chunks.")
            save_batch(rows)
            completed_chunks += len(rows)
            logger.info(
                "Embedding batch saved: repository_id=%s job_id=%s batch=%s/%s "
                "chunks=%s estimated_tokens=%s embedded_chunks=%s total_chunks=%s",
                repository_id,
                job_id,
                batch_number,
                total_batches,
                len(rows),
                tokens,
                completed_chunks,
                len(chunks),
            )
            if progress:
                progress(
                    {
                        "state": "embedding",
                        "batch": batch_number,
                        "total_batches": total_batches,
                        "batch_chunks": len(rows),
                        "estimated_tokens": tokens,
                        "embedded_chunks": completed_chunks,
                        "total_chunks": len(chunks),
                        "pending_chunks": len(chunks) - completed_chunks,
                        "message": (
                            f"Embedding batch {batch_number}/{total_batches} completed."
                        ),
                    }
                )

        if completed_chunks != len(chunks):
            raise RuntimeError(
                f"Only {completed_chunks} of {len(chunks)} repository chunks were saved."
            )
        return ids

    def search(
        self,
        repository_id: int,
        query: str,
        top_k: int = 5,
    ) -> dict:
        query_embedding = self.embeddings.embed_query(query)
        db = SessionLocal()
        try:
            matches = (
                db.query(
                    VectorEmbedding,
                    VectorEmbedding.embedding.cosine_distance(query_embedding).label(
                        "distance"
                    ),
                )
                .filter(VectorEmbedding.repository_id == repository_id)
                .order_by("distance")
                .limit(top_k)
                .all()
            )
            return {
                "documents": [[embedding.content for embedding, _ in matches]],
                "metadatas": [
                    [
                        {
                            "path": embedding.path,
                            "start": embedding.start_line,
                            "end": embedding.end_line,
                        }
                        for embedding, _ in matches
                    ]
                ],
                "distances": [[float(distance) for _, distance in matches]],
            }
        finally:
            db.close()

    def count(self) -> int:
        db = SessionLocal()
        try:
            return db.query(func.count(VectorEmbedding.id)).scalar() or 0
        finally:
            db.close()

    def repository_count(self, repository_id: int) -> int:
        db = SessionLocal()
        try:
            return (
                db.query(func.count(VectorEmbedding.id))
                .filter(VectorEmbedding.repository_id == repository_id)
                .scalar()
                or 0
            )
        finally:
            db.close()

    def delete_repository(self, repository_id: int) -> None:
        db = SessionLocal()
        try:
            db.query(VectorEmbedding).filter(
                VectorEmbedding.repository_id == repository_id
            ).delete(synchronize_session=False)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_file_chunks(
        self,
        repository_id: int,
        file_paths: set[str],
    ) -> None:
        if not file_paths:
            return
        db = SessionLocal()
        try:
            db.query(VectorEmbedding).filter(
                VectorEmbedding.repository_id == repository_id,
                VectorEmbedding.path.in_(file_paths),
            ).delete(synchronize_session=False)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def file_chunk_ids(self, repository_id: int, file_paths: set[str]) -> list[str]:
        if not file_paths:
            return []
        db = SessionLocal()
        try:
            return [
                chunk_id
                for (chunk_id,) in db.query(VectorEmbedding.id)
                .filter(
                    VectorEmbedding.repository_id == repository_id,
                    VectorEmbedding.path.in_(file_paths),
                )
                .all()
            ]
        finally:
            db.close()

    def repository_chunk_ids(self, repository_id: int) -> list[str]:
        db = SessionLocal()
        try:
            return [
                chunk_id
                for (chunk_id,) in db.query(VectorEmbedding.id)
                .filter(VectorEmbedding.repository_id == repository_id)
                .all()
            ]
        finally:
            db.close()

    def delete_ids(self, ids: Sequence[str]) -> None:
        if not ids:
            return
        db = SessionLocal()
        try:
            db.query(VectorEmbedding).filter(VectorEmbedding.id.in_(ids)).delete(
                synchronize_session=False
            )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
