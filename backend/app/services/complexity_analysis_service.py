from app.ai.llm import GeminiClient
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner


class ComplexityAnalysisService:

    MAX_FILES = 25
    MAX_FILE_SIZE = 2500

    @staticmethod
    def analyze(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )[:ComplexityAnalysisService.MAX_FILES]

        docs = FileReader.read_many(files)

        context = []

        for doc in docs:

            context.append(
                f"""
FILE:
{doc["path"]}

CODE:
{doc["content"][:ComplexityAnalysisService.MAX_FILE_SIZE]}
"""
            )

        prompt = f"""
You are a senior software architect.

Analyze the repository complexity.

Return ONLY valid JSON.

Schema:

{{
  "overall_score":90,
  "summary":"",
  "maintainability":"",
  "technical_debt":"",
  "complex_files":[
      {{
          "file":"",
          "complexity":"",
          "reason":""
      }}
  ],
  "code_smells":[
      ""
  ],
  "recommendations":[
      ""
  ]
}}

Evaluate:

1. Maintainability
2. Complexity
3. Long methods
4. Large files
5. Duplicate logic
6. Tight coupling
7. Technical debt
8. Code smells

Repository:

{''.join(context)}
"""

        return GeminiClient().generate_json(
            prompt
        )