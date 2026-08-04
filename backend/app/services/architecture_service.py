from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class ArchitectureService:

    @staticmethod
    def generate(repository):

        files = RepositoryScanner.scan(repository.local_path)

        contents = []

        for file in files[:25]:

            try:

                relative = str(
                    file.relative_to(repository.local_path)
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
You are a Senior Software Architect.

Analyze the repository architecture.

Return ONLY Markdown.

Generate the following sections.

# Architecture Overview

## Project Type

## High-Level Architecture

## Entry Points

## Major Modules

## Data Flow

## External Dependencies

## Design Patterns

## Strengths

## Weaknesses

## Recommendations

Repository:

{chr(10).join(contents)}
"""

        return {
            "architecture": GeminiClient().generate(prompt)
        }