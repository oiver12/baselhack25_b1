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
    classification: Literal["positive", "neutral", "negative"]


class QuestionRequest(BaseModel):
    """Request body for creating a question"""
    question: str


class QuestionResponse(BaseModel):
    """Response when creating a question"""
    question_id: str
    dashboard_url: str


class QuestionInfo(BaseModel):
    """Question with ID for listing endpoints"""
    question_id: str
    question: str

