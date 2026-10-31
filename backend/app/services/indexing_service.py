from collections.abc import Callable

from app.ai.chunker import CodeChunker
from app.ai.embeddings import EmbeddingQuotaError
from app.ai.embedding_rate_limiter import EmbeddingConfigurationError
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner
from app.ai.vector_store import VectorStore
from app.services.file_hash_service import FileHashService


class IndexingError(ValueError):
    """Raised when a repository cannot produce a usable search index."""


class IndexingService:

    @staticmethod
    def index(
        repository_id: int,
        repository_path: str,
        *,
        job_id: int | None = None,
        progress: Callable[[dict], None] | None = None,
    ):
        if progress:
            progress({"state": "scanning", "message": "Scanning repository files."})
        files = RepositoryScanner.scan(repository_path)
        if not files:
            raise IndexingError("No supported source files were found in this repository.")

        documents = FileReader.read_many(files)
        if not documents:
            raise IndexingError("Supported files were found, but none could be read as text.")

        # ── Incremental: skip files whose content hasn't changed ─────────────
        stored_hashes = FileHashService.load(repository_id)
        changed_docs, new_hashes = FileHashService.changed_documents(documents, stored_hashes)
        removed_paths = set(stored_hashes) - set(new_hashes)
        if progress:
            progress(
                {
                    "state": "chunking",
                    "total_files": len(files),
                    "processed_files": len(documents),
                    "changed_files": len(changed_docs),
                    "deleted_files": len(removed_paths),
                    "message": (
                        f"Read {len(documents)} of {len(files)} supported files; "
                        f"{len(changed_docs)} changed."
                    ),
                }
            )

        is_full_reindex = not stored_hashes  # first run → full index
        if not changed_docs and not removed_paths and not is_full_reindex:
            # Nothing changed – return early without touching the vector store
            return {
                "files": len(files),
                "documents": len(documents),
                "chunks": 0,
                "vectors": 0,
                "incremental": True,
                "skipped": len(documents),
            }
        # ─────────────────────────────────────────────────────────────────────

        docs_to_index = changed_docs if not is_full_reindex else documents

        chunks = CodeChunker.chunk_many(docs_to_index)
        chunks = [chunk for chunk in chunks if chunk["content"].strip()]
        if progress:
            progress(
                {
                    "state": "embedding",
                    "total_files": len(files),
                    "processed_files": len(documents),
                    "total_chunks": len(chunks),
                    "embedded_chunks": 0,
                    "pending_chunks": len(chunks),
                    "message": f"Prepared {len(chunks)} chunks for embedding.",
                }
            )
        if not chunks and not is_full_reindex:
            db = VectorStore()
            db.delete_file_chunks(
                repository_id,
                {doc["path"] for doc in changed_docs} | removed_paths,
            )
            FileHashService.save(repository_id, new_hashes)
            return {
                "files": len(files),
                "documents": len(documents),
                "chunks": 0,
                "vectors": 0,
                "incremental": True,
            }

        if not chunks:
            raise IndexingError("No non-empty source content was available to index.")

        db = VectorStore()

        changed_paths = {doc["path"] for doc in changed_docs}
        old_chunk_ids = (
            db.repository_chunk_ids(repository_id)
            if is_full_reindex
            else db.file_chunk_ids(repository_id, changed_paths | removed_paths)
        )

        try:
            new_chunk_ids = db.add_chunks(
                repository_id=repository_id,
                chunks=chunks,
                job_id=job_id,
                progress=progress,
            )
            db.delete_ids(
                [chunk_id for chunk_id in old_chunk_ids if chunk_id not in new_chunk_ids]
            )
        except (EmbeddingQuotaError, EmbeddingConfigurationError):
            raise
        except Exception as error:
            raise IndexingError("The vector index could not be saved. Please try again.") from error

        # Persist updated hash ledger only on success
        FileHashService.save(repository_id, new_hashes)

        return {
            "files": len(files),
            "documents": len(documents),
            "chunks": len(chunks),
            "vectors": len(chunks),
            "incremental": not is_full_reindex,
            "skipped": len(documents) - len(docs_to_index),
        }
