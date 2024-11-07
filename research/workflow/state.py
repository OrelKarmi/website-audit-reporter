from typing_extensions import TypedDict
from typing import List
from research.models.research_findings import ResearchFindings

class ResearchState(TypedDict):
    """State container for the research process.
    
    Attributes:
        task (str): The main research task
        guiding_questions (List[str]): Questions to guide the research
        missing_areas (List[str]): Areas that need more research
        search_queries (List[str]): Current search queries
        focus_areas (List[str]): Areas of focus for the research
        context (List[str]): Gathered research context
        findings (List[ResearchFindings]): High-confidence findings
        lower_findings (List[ResearchFindings]): Low-confidence findings
        max_iterations (int): Maximum number of research iterations
        current_iteration (int): Current iteration count
    """
    task: str
    output_format: str
    guiding_questions: List[str]
    missing_areas: List[str]
    search_queries: List[str]
    focus_areas: List[str]
    context: list[str]
    findings: List[ResearchFindings]
    lower_findings: List[ResearchFindings]
    max_iterations: int
    current_iteration: int
    answer: str

def get_initial_state(task: str, output_format:str ,max_iterations:int) -> ResearchState:
    """Create initial research state."""
    return ResearchState(
        task=task,
        output_format=output_format,
        guiding_questions=[],
        missing_areas=[],
        search_queries=[],
        focus_areas=[],
        context=[],
        findings=[],
        lower_findings=[],
        max_iterations=max_iterations,
        current_iteration=1,
        answer=""
    )
