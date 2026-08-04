import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="codepilot"
        )

    def add_chunks(
        self,
        repository_id: int,
        chunks,
        embeddings,
    ):

        ids = []

        documents = []

        metadatas = []

        embedding_list = []

        for index, chunk in enumerate(chunks):

            ids.append(
                f"repo_{repository_id}_chunk_{index}"
            )

            documents.append(
                chunk["content"]
            )

            embedding_list.append(
                embeddings[index].tolist()
            )

            metadatas.append(
                {
                    "repository_id": repository_id,
                    "path": chunk["path"],
                    "start": chunk["start_line"],
                    "end": chunk["end_line"],
                }
            )

        self.collection.add(
            ids=ids,
            embeddings=embedding_list,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        repository_id: int,
        embedding,
        top_k=5,
    ):

        return self.collection.query(
            query_embeddings=[
                embedding.tolist()
            ],
            n_results=top_k,
            where={
                "repository_id": repository_id
            },
        )

    def count(self):

        return self.collection.count()

    def repository_count(
        self,
        repository_id: int,
    ):

        results = self.collection.get(
            where={
                "repository_id": repository_id
            }
        )

        return len(results["ids"])

    def delete_repository(
        self,
        repository_id: int,
    ):

        self.collection.delete(
            where={
                "repository_id": repository_id
            }
        )