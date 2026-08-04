from pydantic import BaseModel


class ArchitectureResponse(BaseModel):
    architecture: str