from pathlib import Path

from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class RefactorService:

    @staticmethod
    def generate(repository):

        files = RepositoryScanner.scan(repository.local_path)

        repository_content = []

        for file in files[:20]:

            try:

                relative = str(
                    file.relative_to(repository.local_path)
                )

                code = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                repository_content.append(
                    f"""
FILE:
{relative}

--------------------------

{code[:2000]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are an expert software architect.

Analyze the repository for code quality and refactoring opportunities.

Return ONLY valid JSON.

Schema:

{{
  "overall_score": 0,
  "summary": "",
  "suggestions": [
    {{
      "priority": "High|Medium|Low",
      "file": "",
      "reason": "",
      "recommendation": ""
    }}
  ]
}}

Focus on:

- Long functions
- Duplicate code
- Poor naming
- Large files
- Repeated logic
- SOLID violations
- Readability
- Maintainability
- Design improvements

Repository:

{chr(10).join(repository_content)}
"""

        return GeminiClient().generate_json(prompt)