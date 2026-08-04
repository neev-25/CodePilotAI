from pathlib import Path

from app.ai.llm import GeminiClient


class TestGeneratorService:

    @staticmethod
    def generate(repository, file_path: str):

        full_path = Path(repository.local_path) / file_path

        if not full_path.exists():
            raise FileNotFoundError(file_path)

        code = full_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        prompt = f"""
You are a Senior Software Engineer and QA Engineer.

Generate high-quality unit test cases for the following file.

Return ONLY Markdown.

Include:

# Test Strategy

## Functional Tests

## Edge Cases

## Error Cases

## Performance Tests (if applicable)

## Suggested Test Framework

## Example Test Code

Source File:
{file_path}

Source Code:

{code[:12000]}
"""

        return {
            "tests": GeminiClient().generate(prompt)
        }