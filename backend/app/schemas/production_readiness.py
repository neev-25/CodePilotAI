from typing import Literal

from pydantic import BaseModel, Field


class ReadinessEvidence(BaseModel):
    area: str
    status: Literal["present", "missing", "partial"]
    detail: str
    files: list[str] = Field(default_factory=list)


class ProductionReadinessResponse(BaseModel):
    production_score: int = Field(ge=0, le=100)
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
    evidence: list[ReadinessEvidence]
    go_live: bool
