from langchain_openai import ChatOpenAI
from agent import Agent, MainGraphState
from retriver import Retriver
from helper import create_pdf




def analyze_organization(url: str):
    initial_state = MainGraphState(
        stakeholders="",
        resarch_result="",
        errors=[]
    )
    
    # Create and run workflow
    retriver = Retriver(url)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent = Agent(retriver=retriver, llm=llm)
    workflow = agent.create_analysis_graph()
    app = workflow.compile()
    
    # Run analysis
    final_state = app.invoke(initial_state)
    create_pdf(final_state["resarch_result"], "output.pdf", retriver.urls)
    print(final_state)
    




if __name__ == "__main__":
    url = "https://psychologistsofcolor.com/"
    analyze_organization(url)







