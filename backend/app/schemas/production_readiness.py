from pydantic import BaseModel


class ProductionReadinessResponse(BaseModel):
    production_score: int

    readiness: str

    summary: str

    scalability: str

    maintainability: str

    security: str

    testing: str

    observability: str

    deployment: str

    risks: list[str]

    blockers: list[str]

    recommendations: list[str]

    go_live: bool