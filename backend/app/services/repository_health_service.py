from app.ai.llm import GeminiClient

from app.services.repository_stats_service import (
    RepositoryStatsService,
)

from app.services.repository_review_service import (
    RepositoryReviewService,
)

from app.services.security_analysis_service import (
    SecurityAnalysisService,
)

from app.services.complexity_analysis_service import (
    ComplexityAnalysisService,
)

from app.services.dependency_analysis_service import (
    DependencyAnalysisService,
)


class RepositoryHealthService:

    @staticmethod
    def analyze(repository, analyses=None):

        analyses = analyses or {}
        stats = analyses.get("stats") or RepositoryStatsService.get_stats(repository)
        review = analyses.get("review") or RepositoryReviewService.review(repository)
        security = analyses.get("security") or SecurityAnalysisService.analyze(repository)
        complexity = analyses.get("complexity") or ComplexityAnalysisService.analyze(repository)
        dependency = analyses.get("dependency") or DependencyAnalysisService.analyze(repository)

        prompt = f"""
You are a principal software architect.

Below are several analyses of a repository.

Repository Statistics

{stats}

Repository Review

{review}

Security Analysis

{security}

Complexity Analysis

{complexity}

Dependency Analysis

{dependency}

Return ONLY valid JSON.

Schema:

{{
    "overall_score":90,
    "grade":"A",

    "summary":"",

    "maintainability_score":90,

    "security_score":90,

    "architecture_score":90,

    "complexity_score":90,

    "strengths":[
        ""
    ],

    "weaknesses":[
        ""
    ],

    "priority_actions":[
        ""
    ]
}}
"""

        return GeminiClient().generate_json(
            prompt
        )
