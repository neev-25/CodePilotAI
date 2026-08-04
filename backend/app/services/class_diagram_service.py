from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class ClassDiagramService:

    @staticmethod
    def generate(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )

        contents = []

        for file in files[:30]:

            try:

                relative = str(
                    file.relative_to(
                        repository.local_path
                    )
                )

                code = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                contents.append(
                    f"""
FILE:
{relative}

-------------------------------------

{code[:1800]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are a senior software architect.

Analyze the repository.

Generate ONLY a Mermaid Class Diagram.

Rules:

Return ONLY Mermaid.

Start with:

classDiagram

Include:

- Classes
- Services
- Models
- Controllers
- Utilities
- Interfaces if applicable
- Inheritance
- Composition
- Associations
- Dependencies

For JavaScript projects without explicit classes,
represent important modules as classes.

Do not explain anything.

Repository:

{chr(10).join(contents)}
"""

        return {
            "mermaid": GeminiClient().generate(
                prompt
            )
        }