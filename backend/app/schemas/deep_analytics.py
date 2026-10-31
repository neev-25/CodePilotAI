from pydantic import BaseModel

class OnboardingResponse(BaseModel):
    markdown: str
