from pydantic import BaseModel


class ReviewIssue(BaseModel):
    severity: str
    category: str
    file: str
    message: str


class RepositoryReviewResponse(BaseModel):
    overall_score: float
    strengths: list[str]
    issues: list[ReviewIssue]
    recommendations: list[str]