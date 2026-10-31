from app.ai.vector_store import VectorStore


class SearchService:
    @staticmethod
    def search(
        question: str,
        repository_id: int,
        top_k: int = 5,
    ) -> dict:
        db = VectorStore()
        return db.search(
            repository_id=repository_id,
            query=question,
            top_k=top_k,
        )