from app.ai.llm import GeminiClient
from app.ai.reader import FileReader
from app.ai.scanner import RepositoryScanner


class SecurityAnalysisService:

    MAX_FILES = 20
    MAX_FILE_SIZE = 2000

    @staticmethod
    def analyze(repository):

        files = RepositoryScanner.scan(
            repository.local_path
        )[:SecurityAnalysisService.MAX_FILES]

        docs = FileReader.read_many(files)

        context = []

        for doc in docs:

            code = doc["content"][:SecurityAnalysisService.MAX_FILE_SIZE]

            context.append(
                f"""
File:
{doc["path"]}

{code}
"""
            )

        prompt = f"""
You are a senior security engineer.

Analyze this repository.

Find:

1. Bugs
2. Security vulnerabilities
3. Reliability issues

Examples:

- SQL Injection
- Command Injection
- Hardcoded secrets
- Missing validation
- Weak authentication
- Null pointer risks
- Resource leaks
- Missing exception handling
- Race conditions
- Dangerous filesystem operations

IMPORTANT:
Return ONLY valid JSON.
Do NOT use markdown.
Do NOT wrap the response inside ```json.
Do NOT explain anything.

Schema:

{{
  "risk_score": 0,
  "bugs": [
    {{
      "severity": "",
      "file": "",
      "line": 0,
      "issue": "",
      "explanation": ""
    }}
  ],
  "security": [
    {{
      "severity": "",
      "file": "",
      "line": 0,
      "issue": ""
    }}
  ],
  "reliability": [
    {{
      "severity": "",
      "file": "",
      "line": 0,
      "issue": "",
      "explanation": ""
    }}
  ],
  "recommendations": []
}}

Repository:

{''.join(context)}
"""

        return GeminiClient().generate_json(prompt)

        # response = GeminiClient().generate(prompt)

        # print("=" * 80)
        # print("RAW GEMINI RESPONSE")
        # print(response)
        # print("=" * 80)

        # if not response:
        #     raise Exception("Gemini returned an empty response.")

        # response = response.strip()

        # # Remove markdown code fences
        # response = re.sub(r"^```json", "", response, flags=re.IGNORECASE)
        # response = re.sub(r"^```", "", response)
        # response = re.sub(r"```$", "", response)

        # response = response.strip()

        # # Extract JSON object
        # start = response.find("{")
        # end = response.rfind("}")

        # if start == -1 or end == -1:
        #     raise Exception(
        #         f"Gemini did not return JSON.\n\nResponse:\n{response}"
        #     )

        # response = response[start:end + 1]

        # try:
        #     return json.loads(response)

        # except json.JSONDecodeError as e:
        #     raise Exception(f"Invalid JSON returned by Gemini.\n{e}")