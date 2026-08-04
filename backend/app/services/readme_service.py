from pathlib import Path

from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner


class ReadmeService:

    @staticmethod
    def generate(repository):

        files = RepositoryScanner.scan(repository.local_path)

        contents = []

        for file in files[:20]:

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
File:
{relative}

---------------------------------------

{code[:1500]}
"""
                )

            except Exception:
                continue

        prompt = f"""
You are a Senior Software Engineer.

Generate a professional README.md.

Return ONLY Markdown.

Repository Name:
{repository.name}

Include:

# Project Title

## Overview

## Features

## Tech Stack

## Installation

## Usage

## API Endpoints

## Folder Structure

## Future Improvements

## Contributing

## License

Repository Contents:

{chr(10).join(contents)}
"""

        return {
            "readme": GeminiClient().generate(prompt)
        }