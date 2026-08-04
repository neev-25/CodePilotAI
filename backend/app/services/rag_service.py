from app.ai.llm import GeminiClient
from app.ai.prompt_builder import PromptBuilder
from app.services.search_service import SearchService


class RAGService:

    @staticmethod
    def ask(question: str, repository_id: int):

        # Step 1: Retrieve relevant code
        search_results = SearchService.search(
            question,
            repository_id,
        )

        # Step 2: Build prompt
        prompt = PromptBuilder.build(
            question,
            search_results,
        )

        # Step 3: Generate AI answer
        client = GeminiClient()

        answer = client.generate(prompt)

        sources = []

        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]

        for document, metadata in zip(
            documents,
            metadatas,
        ):
            
            snippet = document

            if len(snippet) > 500:
                snippet = snippet[:500] + "..."

            sources.append(
                {
                    "file": metadata["path"].replace("\\", "/"),
                    "start_line": metadata["start"],
                    "end_line": metadata["end"],
                    "snippet": snippet,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }