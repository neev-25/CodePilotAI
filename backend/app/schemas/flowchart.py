from pydantic import BaseModel


class FlowchartResponse(BaseModel):
    mermaid: str