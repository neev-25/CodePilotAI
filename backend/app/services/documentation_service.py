# from pathlib import Path

# from app.ai.llm import GeminiClient

# class DocumentationService:

#     @staticmethod
#     def generate(repository, file_path: str):

#         full_path = Path(repository.local_path) / file_path

#         if not full_path.exists():
#             raise FileNotFoundError(file_path)

#         code = full_path.read_text(
#             encoding="utf-8",
#             errors="ignore"
#         )

#         prompt = f"""
# You are a senior software engineer.

# Generate professional documentation for the following source file.

# Return ONLY valid JSON.

# Schema:

# {{
#   "title": "",
#   "overview": "",
#   "documentation": ""
# }}

# Documentation should include:

# - Purpose
# - Main functionality
# - Key classes/functions
# - Inputs
# - Outputs
# - Dependencies
# - Notes

# Source Code:

# {code[:12000]}
# """

#         return GeminiClient().generate_json(prompt)

#         # response = GeminiClient().generate(prompt)

#         # print("=" * 80)
#         # print("RAW GEMINI RESPONSE")
#         # print(response)
#         # print("=" * 80)

#         # response = response.strip()

#         # # Remove markdown code fences
#         # response = re.sub(r"^```json", "", response, flags=re.IGNORECASE)
#         # response = re.sub(r"^```", "", response)
#         # response = re.sub(r"```$", "", response)

#         # response = response.strip()

#         # start = response.find("{")
#         # end = response.rfind("}")

#         # if start == -1 or end == -1:
#         #     raise Exception("Gemini did not return JSON")

#         # response = response[start:end + 1]

#         # return json.loads(response)

from pathlib import Path

from app.ai.llm import GeminiClient


class DocumentationService:

    @staticmethod
    def generate(repository, file_path: str):

        full_path = Path(repository.local_path) / file_path

        if not full_path.exists():
            raise FileNotFoundError(file_path)

        code = full_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        prompt = f"""
You are a senior software engineer.

Generate professional Markdown documentation for this file.

Do NOT return JSON.

Use this format:

# File Documentation

## Purpose

## Main Functionality

## Key Functions

## Inputs

## Outputs

## Dependencies

## Notes

Source Code:

{code[:12000]}
"""

        return {
            "documentation": GeminiClient().generate(prompt)
        }