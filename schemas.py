from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    content: str = Field(min_length=1)
    priority: int = Field(default=1, ge=1, le=5)
    description: str | None = Field(default=None, max_length=250)


class DocumentResponse(DocumentCreate):
    id: int
    ai_summary: str | None = None

    model_config = {"from_attributes": True}


class AIAnalysisResponse(BaseModel):
    summary: str
    key_points: list[str]
    category: str
    suggested_priority: int = Field(ge=1, le=5)


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)


class AgentResponse(BaseModel):
    answer: str
