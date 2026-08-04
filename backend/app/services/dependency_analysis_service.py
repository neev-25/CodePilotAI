from app.ai.llm import GeminiClient
from app.services.dependency_graph_service import (
    DependencyGraphService,
)


class DependencyAnalysisService:

    @staticmethod
    def analyze(repository):

        graph = DependencyGraphService.build(
            repository
        )

        prompt = f"""
You are a senior software architect.

Analyze this repository dependency graph.

Return ONLY valid JSON.

JSON Schema:

{{
    "overall_score":90,

    "summary":"",

    "internal_dependencies":[
        {{
            "from":"",
            "to":""
        }}
    ],

    "external_dependencies":[
        ""
    ],

    "circular_dependencies":[
        [
            "",
            ""
        ]
    ],

    "highly_coupled_modules":[
        {{
            "module":"",
            "reason":""
        }}
    ],

    "recommendations":[
        ""
    ]
}}

Analysis Requirements:

1. Identify important internal dependencies.

2. List external libraries/packages.

3. Detect circular dependencies if present.

4. Detect highly coupled modules.

5. Give architectural recommendations.

Dependency Graph:

{graph}
"""

        return GeminiClient().generate_json(
            prompt
        )