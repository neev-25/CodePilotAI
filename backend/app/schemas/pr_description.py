from pydantic import BaseModel


class PRDescriptionRequest(BaseModel):
    title: str
    summary: str = ""


class PRDescriptionResponse(BaseModel):
    markdown: str