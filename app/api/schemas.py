"""Pydantic schemas matching TypeScript types."""
from pydantic import BaseModel
from typing import Literal


class PersonOpinion(BaseModel):
    """Represents a person's opinion on a suggestion."""
    name: str
    profile_pic_url: str
    message: str  # If followup questions were asked, this is the summary / all the messages
    classification: Literal["sophisticated", "simple", "neutral"]


class Suggestion(BaseModel):
    """Represents a suggestion/option for the question."""
    title: str
    size: float  # 0 - 1
    pros: list[str]
    contra: list[str]
    people_opinions: list[PersonOpinion]


# Response type (array of Suggestions)
SuggestionsResponse = list[Suggestion]


class QuestionRequest(BaseModel):
    """Request body for creating a new question."""
    question: str


class QuestionResponse(BaseModel):
    """Response for creating a new question."""
    question_id: str
    dashboard_url: str


class BubbleData(BaseModel):
    """Represents a live bubble (2-word summary)."""
    summary: str
    username: str
    timestamp: str

