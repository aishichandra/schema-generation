from typing import List, Optional

from pydantic import BaseModel


class Survey(BaseModel):
    class Response(BaseModel):
        response_text: str
        responses_count: Optional[int]
        responses_percentage: Optional[float]

    class Question(BaseModel):
        question_number: Optional[int]
        question_text: str
        question_responses: List["Survey.Response"]

    survey_name: str
    survey_questions: List["Survey.Question"]
