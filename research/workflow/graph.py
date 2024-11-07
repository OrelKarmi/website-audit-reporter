from langgraph.graph import START, END, StateGraph
from research.analyzer import Research
from research.workflow.state import ResearchState, get_initial_state
from retriver import Retriver



def run_research_workflow(retriver:Retriver, task:str, output_foramt:str, max_iteration:int ) -> str:
    """Run the research workflow."""
    graph = create_research_graph(retriver)
    workflow = graph.compile()
    
    # Print workflow graph
    print(workflow.get_graph().draw_ascii())
    
    # Run workflow
    response = workflow.invoke(get_initial_state(task, output_foramt, max_iteration))
    return response["answer"]

def create_research_graph(retriver:Retriver) -> StateGraph:
    """Create the research workflow graph."""
    graph = StateGraph(ResearchState)
    research = Research(retriver)

    # Add nodes
    graph.add_node("planner", research.planner)
    graph.add_node("search_context", research.search_context)
    graph.add_node("optimize_search", research.optimize_search)
    graph.add_node("analyze_finfind", research.analyze_finfind)
    graph.add_node("summarize_findings", research.summarize_findings)

    # Add edges
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "search_context")
    graph.add_edge("search_context", "analyze_finfind")
    graph.add_edge("optimize_search", "search_context")
    graph.add_edge("summarize_findings", END)


    graph.add_conditional_edges(
        "analyze_finfind",
        research.check_completion,
        {
            True: "summarize_findings",
            False: "optimize_search"
        }
    )

    return graph



