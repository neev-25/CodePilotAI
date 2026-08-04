from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class FlowchartService:

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

---------------------------------------

{code[:1800]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are a senior software architect.

Analyze this repository.

Generate ONLY a Mermaid Flowchart.

Return ONLY Mermaid.

Rules:

- Start with:

flowchart TD

- Show the application's high-level execution flow.

Include:

- Entry points
- APIs
- Controllers
- Services
- AI modules
- Database
- External APIs
- Outputs

Do NOT explain anything.

Repository:

{chr(10).join(contents)}
"""

        return {
            "mermaid": GeminiClient().generate(
                prompt
            )
        }