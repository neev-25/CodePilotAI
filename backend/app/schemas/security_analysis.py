from pydantic import BaseModel


class Finding(BaseModel):
    severity: str
    file: str
    line: int
    issue: str
    explanation: str


class SecurityFinding(BaseModel):
    severity: str
    file: str
    line: int
    issue: str


class SecurityAnalysisResponse(BaseModel):
    risk_score: int
    bugs: list[Finding]
    security: list[SecurityFinding]
    reliability: list[Finding]
    recommendations: list[str]