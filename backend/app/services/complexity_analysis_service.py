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
You are an Academic Software Engineering Professor and Industry Expert.

Analyze the repository complexity strictly according to formal Software Engineering (SE) syllabus topics.

Return ONLY valid JSON.

Schema:

{{
  "overall_score":90,
  "summary":"",
  "cyclomatic_complexity_estimate":"",
  "coupling_assessment":"",
  "cohesion_assessment":"",
  "maintainability":"",
  "technical_debt":"",
  "solid_principle_violations":[
      {{
         "principle": "",
         "violation": "",
         "file": ""
      }}
  ],
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

1. Cyclomatic Complexity
2. Algorithmic Efficiency
3. Coupling (Loose vs Tight)
4. Cohesion (High vs Low)
5. SOLID Principle Adherence
6. Code Smells & Anti-patterns
7. Technical Debt

Repository:

{''.join(context)}
"""

        return GeminiClient().generate_json(
            prompt
        )