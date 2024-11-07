from pydantic import BaseModel, Field, validator
from typing import ClassVar, List

class Queries(BaseModel):
    """Model for managing search queries with a maximum limit."""
    MAX_QUERIES: ClassVar[int] = 3
    search_queries: List[str] = Field(
        description=f"Search queries to gather relevant information the query nust be an atom quetion, max search queries is {MAX_QUERIES}",
        default_factory=list
    )

    @validator('search_queries')
    def validate_queries_length(cls, v):
        if len(v) > cls.MAX_QUERIES:
            return v[:cls.MAX_QUERIES]
        return v

class GuidingQuestions(BaseModel):
    """Model for managing guiding questions with a maximum limit."""
    MAX_GUIDING_QUESTIONS: ClassVar[int] = 3
    guiding_questions: List[str] = Field(
        description=f"Questions to verify that all aspects of the task are covered, max guiding questions is {MAX_GUIDING_QUESTIONS}",
    )
    
    @validator('guiding_questions')
    def validate_guiding_questions_length(cls, v):
        if len(v) > cls.MAX_GUIDING_QUESTIONS:
            return v[:cls.MAX_GUIDING_QUESTIONS]
        return v

class TaskAnalysis(BaseModel):
    """Model combining search queries and guiding questions for task analysis."""
    search_queries: Queries
    guiding_questions: GuidingQuestions
