from pydantic import BaseModel, Field
from typing import List

class ResearchFindings(BaseModel):
    """Model representing research findings for a specific question.
    
    Attributes:
        question (str): The guiding question being answered
        answer (str): The extracted answer from the research
        evidence (List[str]): Supporting evidence or quotes
        confidence (float): Confidence score (0-1)
        follow_up_question (str): Follow-up question for low confidence findings
    """
    question: str = Field(description="The guiding question")
    answer: str = Field(description="The extracted answer from the research")
    evidence: List[str] = Field(description="Supporting evidence or quotes from the research", default_factory=list)
    confidence: float = Field(description="Confidence score for the answer (0-1)", ge=0, le=1)
    follow_up_question: str = Field(
        description="Search-friendly follow-up question for low confidence or missing information",
    )

    def __str__(self) -> str:
        return (
            f"ResearchFindings(\n"
            f"  question={self.question!r},\n"
            f"  answer={self.answer!r},\n"
            f"  evidence={self.evidence!r},\n"
            f"  confidence={self.confidence!r},\n"
            f"  follow_up_question={self.follow_up_question!r}\n"
            f")"
        )

class ListResearchFindings(BaseModel):
    """Container model for a list of research findings."""
    findings: List[ResearchFindings] = Field(description="List of research findings", default_factory=list)
