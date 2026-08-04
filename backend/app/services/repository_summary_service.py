from app.ai.llm import GeminiClient
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner


class RepositorySummaryService:

    MAX_FILES = 10
    MAX_CHARS_PER_FILE = 2000

    @staticmethod
    def generate_summary(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )

        files = files[:RepositorySummaryService.MAX_FILES]

        documents = FileReader.read_many(files)

        repository_context = []

        for document in documents:

            content = document["content"]

            if len(content) > RepositorySummaryService.MAX_CHARS_PER_FILE:
                content = (
                    content[
                        : RepositorySummaryService.MAX_CHARS_PER_FILE
                    ]
                    + "\n..."
                )

            repository_context.append(
                f"""
==============================
File: {document["path"]}
==============================

{content}
"""
            )

        prompt = f"""
You are an expert software architect.

Analyze the following repository.

Write a professional summary including:

1. Repository purpose
2. Main technologies used
3. Overall architecture
4. Major modules
5. Primary responsibilities
6. Important observations

Repository:

{''.join(repository_context)}

Return only the summary.
"""

        llm = GeminiClient()

        summary = llm.generate(prompt)

        return {
            "summary": summary
        }