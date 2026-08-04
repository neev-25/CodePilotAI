from pydantic import BaseModel


class RepositoryHealthResponse(BaseModel):
    overall_score: int
    grade: str
    summary: str

    maintainability_score: int
    security_score: int
    architecture_score: int
    complexity_score: int

    strengths: list[str]
    weaknesses: list[str]
    priority_actions: list[str]