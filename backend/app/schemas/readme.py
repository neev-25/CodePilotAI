from pydantic import BaseModel


class ReadmeResponse(BaseModel):
    readme: str