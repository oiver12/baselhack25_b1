"""
Pydantic schemas matching TypeScript types
"""
from pydantic import BaseModel
from typing import Literal, List


class PersonOpinion(BaseModel):
    """Matches TypeScript PersonOpinion type"""
    name: str
    profile_pic_url: str
    message: str  # If followup questions were asked, this is the summary / all the messages
    classification: Literal["good", "neutral", "bad"]


class Suggestion(BaseModel):
    """Matches TypeScript Suggestion type"""
    title: str
    size: float  # 0 - 1
    pros: List[str]
    contra: List[str]
    people_opinions: List[PersonOpinion]


# Response type: array of Suggestions
SuggestionsResponse = List[Suggestion]


class QuestionRequest(BaseModel):
    """Request body for creating a question"""
    question: str


class QuestionResponse(BaseModel):
    """Response when creating a question"""
    question_id: str
    dashboard_url: str

