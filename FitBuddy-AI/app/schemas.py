from typing import Literal

from pydantic import BaseModel, Field, field_validator

Goal = Literal["general wellness", "strength", "flexibility", "endurance"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    user_id: str = Field(min_length=2, max_length=64)
    username: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=300)
    goal: Goal = "general wellness"
    intensity: Intensity = "medium"

    @field_validator("user_id", "username")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join(value.strip().split())


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=64)
    feedback: str = Field(min_length=3, max_length=1500)
