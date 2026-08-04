from pydantic import BaseModel


class SourceResponse(BaseModel):

    file: str

    start_line: int

    end_line: int

    snippet: str


class AskResponse(BaseModel):

    answer: str

    sources: list[SourceResponse]