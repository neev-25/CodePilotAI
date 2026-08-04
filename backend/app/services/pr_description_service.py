from pathlib import Path

from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class PRDescriptionService:

    @staticmethod
    def generate(repository, title: str, summary: str):

        files = RepositoryScanner.scan(repository.local_path)

        snippets = []

        for file in files[:15]:

            try:

                relative = str(
                    file.relative_to(repository.local_path)
                )

                code = file.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                snippets.append(
                    f"""
File:
{relative}

------------------------

{code[:1200]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are an experienced software engineer.

Generate a professional GitHub Pull Request description.

Return ONLY Markdown.

PR Title:
{title}

Developer Notes:
{summary}

Repository Context:

{chr(10).join(snippets)}

The PR description should contain:

# Summary

## Changes Made

## Why

## Testing

## Checklist

Use GitHub markdown.
"""

        return {
            "markdown": GeminiClient().generate(prompt)
        }