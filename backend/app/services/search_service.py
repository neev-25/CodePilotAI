from app.ai.embeddings import EmbeddingModel
from app.ai.vector_store import VectorStore


class SearchService:

    @staticmethod
    def search(
        question: str,
        repository_id: int,
    ):

        model = EmbeddingModel()

        embedding = model.encode(
            [question]
        )[0]

        db = VectorStore()

        results = db.search(
            repository_id=repository_id,
            embedding=embedding,
        )

        return results