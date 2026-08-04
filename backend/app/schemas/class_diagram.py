from pydantic import BaseModel


class ClassDiagramResponse(BaseModel):
    mermaid: str