from pathlib import Path

from app.ai.llm import GeminiClient


class ExplainFileService:

    MAX_FILE_SIZE = 12000

    @staticmethod
    def explain(repository, relative_path: str):

        file_path = Path(repository.local_path) / relative_path

        if not file_path.exists():
            raise FileNotFoundError(
                f"{relative_path} not found."
            )

        if not file_path.is_file():
            raise FileNotFoundError(
                f"{relative_path} is not a file."
            )

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if len(content) > ExplainFileService.MAX_FILE_SIZE:
            content = (
                content[: ExplainFileService.MAX_FILE_SIZE]
                + "\n..."
            )

        prompt = f"""
You are a senior software engineer.

Explain this source file.

Include:

1. Purpose
2. Main classes/functions
3. Responsibilities
4. Important logic
5. How it interacts with other files

File:
{relative_path}

Code:

{content}

Return only the explanation.
"""

        llm = GeminiClient()

        explanation = llm.generate(prompt)

        return {
            "file": relative_path,
            "explanation": explanation,
        }