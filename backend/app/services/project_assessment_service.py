from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from app.ai.llm import GeminiClient
from app.services.search_service import SearchService


class ProjectAssessmentError(ValueError):
    """Raised when an assessment cannot be grounded in retrieved repository code."""


class ProjectAssessmentService:
    RETRIEVAL_QUESTION = (
        "What problem does this project solve, who uses it, and how does its user "
        "workflow work? Show the application entry points, frontend/backend "
        "architecture, core modules, data persistence, security, testing, and "
        "deployment evidence."
    )

    PROMPT = PromptTemplate.from_template(
        """You are an evidence-grounded product and software engineering analyst.
Assess the repository only from the provided source excerpts. Do not invent
users, features, architecture, tests, or deployment behavior. If evidence is
missing, say it is not evident in the indexed files. Separate facts from
recommendations and cite evidence by its file path and line range as [path:Lx-Ly].

Write concise Markdown with these sections:
# Project Assessment
## Product and User Perspective
Explain the apparent user problem, intended users, primary workflow, user value,
and visible usability gaps. State uncertainty where evidence is limited.
## Software Engineering Perspective
Describe the observed architecture, major components/data flow, maintainability,
testing, security, and operational signals. Avoid claiming checks you cannot
support from the excerpts.
## Strengths
## Risks and Evidence Gaps
## Prioritized Next Steps
Make each material claim traceable to a citation. Do not include uncited claims.

Repository: {repository_name}

Source excerpts:
{context}"""
    )

    @classmethod
    def generate(cls, repository) -> dict:
        results = SearchService.search(
            cls.RETRIEVAL_QUESTION,
            repository.id,
            top_k=12,
        )
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        if not documents:
            raise ProjectAssessmentError(
                "No repository context was retrieved. Index the repository and try again."
            )

        context = "\n\n".join(
            (
                f"File: {metadata.get('path', 'unknown')}\n"
                f"Lines: {metadata.get('start', '?')}-{metadata.get('end', '?')}\n"
                f"{document}"
            )
            for document, metadata in zip(documents, metadatas)
        )
        chain = (
            cls.PROMPT
            | RunnableLambda(
                lambda prompt_value: GeminiClient().generate(prompt_value.to_string())
            )
            | StrOutputParser()
        )
        assessment = chain.invoke(
            {
                "repository_name": repository.name,
                "context": context,
            }
        )

        sources = []
        seen_sources = set()
        for document, metadata in zip(documents, metadatas):
            source_key = (metadata.get("path"), metadata.get("start"), metadata.get("end"))
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            sources.append(
                {
                    "file": str(metadata.get("path", "")).replace("\\", "/"),
                    "start_line": metadata.get("start", 1),
                    "end_line": metadata.get("end", 1),
                    "snippet": document[:500] + ("..." if len(document) > 500 else ""),
                }
            )
            if len(sources) == 8:
                break

        return {"assessment": assessment, "sources": sources}
