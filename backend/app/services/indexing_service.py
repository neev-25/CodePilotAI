from app.ai.chunker import CodeChunker
from app.ai.embeddings import EmbeddingModel
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner
from app.ai.vector_store import VectorStore


class IndexingError(ValueError):
    """Raised when a repository cannot produce a usable search index."""


class IndexingService:

    @staticmethod
    def index(
        repository_id: int,
        repository_path: str,
    ):

        files = RepositoryScanner.scan(repository_path)
        if not files:
            raise IndexingError("No supported source files were found in this repository.")

        documents = FileReader.read_many(files)
        if not documents:
            raise IndexingError("Supported files were found, but none could be read as text.")

        chunks = CodeChunker.chunk_many(documents)
        # Empty files have no lines and should not be sent to the embedding or vector APIs.
        chunks = [chunk for chunk in chunks if chunk["content"].strip()]
        if not chunks:
            raise IndexingError("No non-empty source content was available to index.")

        embedding_model = EmbeddingModel()

        vectors = embedding_model.encode(
            [
                chunk["content"]
                for chunk in chunks
            ]
        )

        if len(vectors) != len(chunks):
            raise IndexingError("Embedding generation returned an incomplete result.")

        db = VectorStore()
        # Only replace a working index once the new data is ready to store.
        db.delete_repository(repository_id)

        try:
            db.add_chunks(repository_id=repository_id, chunks=chunks, embeddings=vectors)
        except Exception as error:
            # Do not report success when the vector store failed after replacement.
            db.delete_repository(repository_id)
            raise IndexingError("The vector index could not be saved. Please try again.") from error

        return {
            "files": len(files),
            "documents": len(documents),
            "chunks": len(chunks),
            "vectors": len(vectors),
        }
