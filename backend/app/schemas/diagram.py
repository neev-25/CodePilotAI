from pydantic import BaseModel

from app.schemas.response import SourceResponse


class DiagramResponse(BaseModel):
    diagram_type: str
    mermaid: str
    sources: list[SourceResponse]
