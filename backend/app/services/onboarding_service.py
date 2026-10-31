from app.ai.llm import GeminiClient
from app.ai.scanner import RepositoryScanner

class OnboardingService:
    @staticmethod
    def generate(repository):
        files = RepositoryScanner.scan(repository.local_path)
        contents = []

        for file in files[:25]:
            try:
                relative = str(file.relative_to(repository.local_path))
                code = file.read_text(encoding="utf-8", errors="ignore")
                contents.append(f"FILE:\n{relative}\n\n{code[:1500]}\n")
            except Exception:
                continue

        prompt = f"""
You are a Staff Engineer welcoming a junior developer to the project.

Write a comprehensive "Codebase 101" Onboarding Guide.
Return ONLY Markdown.

Structure:
# Developer Onboarding Guide

## Project Setup & Verification
(How to get this code running logically)

## Where to Start Reading
(Which 3-4 files form the absolute core entry points and why)

## Core Technologies & Dependencies
(Explain the stack chosen)

## Common "Gotchas" & Pitfalls
(What usually confuses new devs in this framework/pattern)

Repository:

{chr(10).join(contents)}
"""
        return {"markdown": GeminiClient().generate(prompt)}
