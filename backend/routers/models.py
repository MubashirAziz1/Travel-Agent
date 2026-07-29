from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall health status", example="ok")
    version: str = Field(..., description="Application version", example="0.1.0")
    environment: str = Field(..., description="Deployment environment", example="development")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="User's travel query")
    thread_id: str = Field(min_length=5, description="Conversation thread ID")
    is_continuation: Optional[bool] = Field(False, description="Is this continuing a previous conversation")


class TaskResponse(BaseModel):
    task_id: str


class StatusResponse(BaseModel):
    status: str  # "running", "completed", "failed"
    result: dict | None = None
    form_to_display: str | None = None


class CustomerInfoRequest(BaseModel):
    thread_id: str = Field(min_length=5)
    customer_info: dict