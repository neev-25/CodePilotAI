from app.ai.embeddings import EmbeddingModel
from app.ai.vector_store import VectorStore

class SemanticSearchService:
    @staticmethod
    def search(repository_id: int, query: str, top_k: int = 15):
        embedding_model = EmbeddingModel()
        vector_store = VectorStore()
        
        query_embedding = embedding_model.encode([query])[0]
        results = vector_store.search(repository_id, query_embedding, top_k=top_k)
        
        hits = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0] if "distances" in results and results["distances"] else [0]*len(docs)
            
            for doc, meta, dist in zip(docs, metas, dists):
                hits.append({
                    "content": doc,
                    "path": meta.get("path"),
                    "start_line": meta.get("start"),
                    "end_line": meta.get("end"),
                    "distance": dist
                })
                
        return {"hits": hits}
