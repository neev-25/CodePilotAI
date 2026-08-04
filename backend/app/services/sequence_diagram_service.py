from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class SequenceDiagramService:

    @staticmethod
    def generate(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )

        contents = []

        for file in files[:25]:

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

---------------------------------------

{code[:1800]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are an experienced software architect.

Analyze this repository.

Generate ONLY a Mermaid Sequence Diagram.

Return ONLY Mermaid.

Rules:

- Start with

sequenceDiagram

- Use meaningful participants.

- Show request flow.

- Show important modules.

- Show database interactions.

- Show API interactions.

Do NOT explain anything.

Repository:

{chr(10).join(contents)}
"""

        return {
            "mermaid": GeminiClient().generate(prompt)
        }