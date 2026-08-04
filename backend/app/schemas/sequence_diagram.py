from pydantic import BaseModel


class SequenceDiagramResponse(BaseModel):
    mermaid: str