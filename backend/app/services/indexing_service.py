from app.ai.chunker import CodeChunker
from app.ai.embeddings import EmbeddingModel
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner
from app.ai.vector_store import VectorStore


class IndexingService:

    @staticmethod
    def index(
        repository_id: int,
        repository_path: str,
    ):

        db = VectorStore()

        # Delete old vectors before indexing
        db.delete_repository(repository_id)

        files = RepositoryScanner.scan(repository_path)

        documents = FileReader.read_many(files)

        chunks = CodeChunker.chunk_many(documents)

        embedding_model = EmbeddingModel()

        vectors = embedding_model.encode(
            [
                chunk["content"]
                for chunk in chunks
            ]
        )

        db.add_chunks(
            repository_id=repository_id,
            chunks=chunks,
            embeddings=vectors,
        )

        return {
            "files": len(files),
            "documents": len(documents),
            "chunks": len(chunks),
            "vectors": len(vectors),
        }