from pydantic import BaseModel

from app.schemas.response import SourceResponse


class ProjectAssessmentResponse(BaseModel):
    assessment: str
    sources: list[SourceResponse]
