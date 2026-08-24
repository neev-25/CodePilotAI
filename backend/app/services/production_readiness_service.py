from app.ai.llm import GeminiClient

from app.services.repository_health_service import (
    RepositoryHealthService,
)


class ProductionReadinessService:

    @staticmethod
    def analyze(repository, health=None):

        health = health or RepositoryHealthService.analyze(repository)

        prompt = f"""
You are a Principal Software Architect.

Evaluate whether this repository is ready for production deployment.

Repository Health Report

{health}

Return ONLY valid JSON.

Schema:

{{
    "production_score":90,

    "readiness":"Production Ready",

    "summary":"",

    "scalability":"",

    "maintainability":"",

    "security":"",

    "testing":"",

    "observability":"",

    "deployment":"",

    "risks":[
        ""
    ],

    "blockers":[
        ""
    ],

    "recommendations":[
        ""
    ],

    "go_live":true
}}

Evaluate:

• scalability

• maintainability

• architecture

• security

• deployment readiness

• testing maturity

• observability

• CI/CD readiness

• production risks

• overall readiness
"""

        return GeminiClient().generate_json(
            prompt
        )
