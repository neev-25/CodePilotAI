import json

from app.ai.llm import GeminiClient
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner


class RepositoryReviewService:

    MAX_FILES = 15
    MAX_FILE_SIZE = 2000

    @staticmethod
    def review(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )[:RepositoryReviewService.MAX_FILES]

        documents = FileReader.read_many(files)

        context = []

        for document in documents:

            code = document["content"]

            if len(code) > RepositoryReviewService.MAX_FILE_SIZE:
                code = code[
                    : RepositoryReviewService.MAX_FILE_SIZE
                ]

            context.append(
                f"""
File: {document["path"]}

{code}
"""
            )

        prompt = f"""
You are a senior software architect.

Review the repository.

IMPORTANT RULES:

- Return ONLY valid JSON.
- Do NOT use markdown.
- Do NOT wrap the response inside ```json.
- Do NOT explain anything.
- Output must begin with {{
- Output must end with }}

Schema:

{{
  "overall_score": 0,
  "strengths": [],
  "issues": [
    {{
      "severity":"low",
      "category":"",
      "file":"",
      "message":""
    }}
  ],
  "recommendations":[]
}}

Repository:

{''.join(context)}
"""
        return GeminiClient().generate_json(prompt)
        # response = GeminiClient().generate(prompt)

        # if not response:
        #     raise Exception("Gemini returned an empty response.")

        # response = response.strip()

        # # Remove markdown code fences
        # if response.startswith("```json"):
        #     response = response[7:]

        # if response.startswith("```"):
        #     response = response[3:]

        # if response.endswith("```"):
        #     response = response[:-3]

        # response = response.strip()

        # try:
        #     return json.loads(response)

        # except json.JSONDecodeError:
        #     print("=" * 80)
        #     print("INVALID GEMINI RESPONSE")
        #     print(response)
        #     print("=" * 80)

        #     raise Exception("Gemini did not return valid JSON.")