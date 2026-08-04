from pydantic import BaseModel


class RepositorySummaryResponse(BaseModel):
    summary: str