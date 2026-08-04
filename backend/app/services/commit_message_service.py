from app.ai.llm import GeminiClient


class CommitMessageService:

    @staticmethod
    def generate(repository, summary: str):

        prompt = f"""
You are an experienced software engineer.

Generate professional Git commit messages.

Repository Name:
{repository.name}

Developer Summary:
{summary}

Return ONLY valid JSON.

Schema:

{{
  "conventional_commit": "",
  "detailed_commit": ""
}}

Rules:

1. Use Conventional Commits.
2. Keep the first message under 72 characters.
3. Use prefixes like:
   - feat
   - fix
   - docs
   - refactor
   - test
   - chore
   - perf
   - ci
4. detailed_commit should be 2-3 sentences explaining the change.
"""

        return GeminiClient().generate_json(prompt)