from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.ai.llm import GeminiClient
from app.ai.prompt_builder import PromptBuilder
from app.services.search_service import SearchService


class RAGService:
    @staticmethod
    def ask(question: str, repository_id: int) -> dict:
        search_results = SearchService.search(
            question,
            repository_id,
        )

        client = GeminiClient()
        chain = (
            RunnableLambda(
                lambda inputs: PromptBuilder.build(
                    inputs["question"],
                    inputs["search_results"],
                )
            )
            | RunnableLambda(client.generate)
            | StrOutputParser()
        )
        answer = chain.invoke(
            {
                "question": question,
                "search_results": search_results,
            }
        )

        sources = []
        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]
        for document, metadata in zip(documents, metadatas):
            snippet = document[:500]
            if len(document) > 500:
                snippet += "..."
            sources.append(
                {
                    "file": metadata.get("path", "").replace("\\", "/"),
                    "start_line": metadata.get("start"),
                    "end_line": metadata.get("end"),
                    "snippet": snippet,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }