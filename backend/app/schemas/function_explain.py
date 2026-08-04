from pydantic import BaseModel


class ExplainFunctionRequest(BaseModel):
    path: str
    function: str


class ExplainFunctionResponse(BaseModel):
    file: str
    function: str
    explanation: str