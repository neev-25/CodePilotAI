from app.ai.llm import GeminiClient


class ChangelogService:

    @staticmethod
    def generate(repository, version: str, summary: str):

        prompt = f"""
You are a senior software engineer.

Generate a professional CHANGELOG entry.

Repository:
{repository.name}

Version:
{version}

Developer Summary:
{summary}

Return ONLY Markdown.

Format:

# Changelog

## [{version}]

### Added

### Changed

### Fixed

### Improved

### Notes

Rules:

- Use concise bullet points.
- Only include information supported by the summary.
- Do not invent features.
"""

        return {
            "changelog": GeminiClient().generate(prompt)
        }