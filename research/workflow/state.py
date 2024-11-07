from typing_extensions import TypedDict
from typing import List
from research.models.research_findings import ResearchFindings

class ResearchState(TypedDict):

    task: str
    output_format: str
    guiding_questions: List[str]
    search_queries: List[str]
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
        search_queries=[],
        context=[],
        findings=[],
        lower_findings=[],
        max_iterations=max_iterations,
        current_iteration=1,
        answer=""
    )
