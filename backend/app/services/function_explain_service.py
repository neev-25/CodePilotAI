from pathlib import Path
import regex as re

from fastapi import HTTPException

from app.ai.llm import GeminiClient


class FunctionExplainService:

    MAX_FUNCTION_SIZE = 12000

    PATTERNS = {
        ".py": r"^\s*(async\s+def|def)\s+{name}\s*\(",

        ".js": r"^\s*(export\s+)?(async\s+)?function\s+{name}\s*\(",
        ".ts": r"^\s*(export\s+)?(async\s+)?function\s+{name}\s*\(",

        ".java": r".*\b{name}\s*\(",

        ".cpp": r".*\b{name}\s*\(",
        ".cc": r".*\b{name}\s*\(",
        ".c": r".*\b{name}\s*\(",
        ".hpp": r".*\b{name}\s*\(",
        ".h": r".*\b{name}\s*\(",

        ".go": r"^\s*func\s+{name}\s*\(",

        ".rs": r"^\s*fn\s+{name}\s*\(",

        ".php": r"function\s+{name}\s*\(",
    }

    @staticmethod
    def extract_python(lines, start):

        indent = len(lines[start]) - len(lines[start].lstrip())

        end = start + 1

        while end < len(lines):

            line = lines[end]

            if line.strip() == "":
                end += 1
                continue

            current = len(line) - len(line.lstrip())

            if current <= indent:
                break

            end += 1

        return "\n".join(lines[start:end])

    @staticmethod
    def extract_braces(lines, start):

        code = []

        braces = 0

        started = False

        for line in lines[start:]:

            code.append(line)

            braces += line.count("{")
            braces -= line.count("}")

            if "{" in line:
                started = True

            if started and braces == 0:
                break

        return "\n".join(code)

    @staticmethod
    def extract_function(content, suffix, function_name):

        pattern = FunctionExplainService.PATTERNS.get(suffix)

        if pattern is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {suffix}"
            )

        pattern = pattern.format(name=re.escape(function_name))

        lines = content.splitlines()

        for i, line in enumerate(lines):

            if re.search(pattern, line):

                if suffix == ".py":
                    return FunctionExplainService.extract_python(lines, i)

                return FunctionExplainService.extract_braces(lines, i)

        return None

    @staticmethod
    def explain(repository, relative_path, function_name):

        file_path = Path(repository.local_path) / relative_path

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="File not found."
            )

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        function = FunctionExplainService.extract_function(
            content,
            file_path.suffix.lower(),
            function_name,
        )

        if function is None:
            raise HTTPException(
                status_code=404,
                detail=f"Function '{function_name}' not found."
            )

        if len(function) > FunctionExplainService.MAX_FUNCTION_SIZE:
            function = function[:FunctionExplainService.MAX_FUNCTION_SIZE]

        prompt = f"""
You are an expert software engineer.

Analyze ONLY this function.

Explain:

1. Purpose
2. Parameters
3. Return value
4. Internal logic
5. Algorithms used
6. Time complexity (if applicable)
7. Space complexity (if applicable)
8. Dependencies
9. Edge cases

Function Code:

{function}

Return only the explanation.
"""

        explanation = GeminiClient().generate(prompt)

        return {
            "file": relative_path,
            "function": function_name,
            "explanation": explanation,
        }