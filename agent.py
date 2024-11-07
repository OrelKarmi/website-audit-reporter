from typing import List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from research.workflow.graph import run_research_workflow





class MainGraphState(TypedDict):
    """Represents the current state of the analysis process"""
    stakeholders: str
    resarch_result:str
    errors: List[str]
    


class Agent:
    def __init__(self, retriver, llm):
        self.retriver = retriver
        self.llm = llm



    def get_stakeholders(self, state: MainGraphState) -> MainGraphState:
        """
        Node function that runs research tasks in parallel using async
        """
        try:
            # Run both research tasks asynchronously


            stakeholders_task = """
                identify the relevant stakeholder groups for non-profit organizations, 
                    focusing on groups such as Donors, Regulators, Beneficiaries, Partners, Internal Staff, Public/Media, and Volunteers.

                1. Think step-by-step to determine who the main stakeholder groups of the organization are, 
                    based on the content and information provided on the website.
                2. Assess if each identified group is essential to achieving the organization’s mission.
                3. Note any key stakeholder groups that may be missing or underserved.
                
                
                """
            
            output_format = "Your answer should only list the stakeholder group names, without any introductions, conclusions, or additional commentary. Just the group names, each on a new line."



            stakeholders_result = run_research_workflow(self.retriver, stakeholders_task, output_format, 1)
            state["stakeholders"] = stakeholders_result
                    
        except Exception as e:
            state["errors"].append(f"Error in parallel research: {str(e)}")
        
        return state


    def main_research(self, state: MainGraphState) -> MainGraphState:
        """create the main research task"""
        stakeholder_groups = state["stakeholders"]

        try:
            resarch_task = f"""
                As part of our ongoing marketing support, you will conduct an audit of the client's website to understand how the relevant stakeholders perceive the organization. Focus solely on the stakeholders selected for this task.

                Instructions:

                1. Stakeholder Selection:
                - You will be provided with a list of relevant stakeholders for this audit: {stakeholder_groups}. Ensure that your research focuses exclusively on these stakeholders.
                - Do not include any stakeholders that are not relevant to the organization’s objectives.

                2. Audit Focus:
                - Analyze how the organization is perceived by the selected stakeholders based on their website. Key areas to assess include:
                    - Transparency and clarity of information
                    - Ease of navigation and accessibility
                    - Communication of mission and values
                    - Trust-building and credibility factors

                3. **Recommendations for Improvement:**
                - Provide tailored recommendations on how the organization can improve its online presence to better align with the needs and expectations of the selected stakeholders. Suggestions should include:
                    - How to improve engagement with the selected stakeholders
                    - How to make key information (e.g., mission, impact, funding transparency) more visible and accessible
                    - Recommendations for enhancing user experience and accessibility on the site

                Deliverables:
                - A detailed report summarizing the findings of the audit, including areas where the organization excels or needs improvement, based only on the relevant stakeholders.
                - Actionable recommendations for improving the client’s website to enhance alignment with the selected stakeholders.

            """
            
            output_format = """
                Please structure your research findings in the following format:

                1. Summary of Findings:

                **[Stakeholder Perceptions]**
                • Provide 3-4 key findings about how the selected stakeholders perceive the organization through the website:
                    - Communication effectiveness and transparency
                    - Mission and values alignment
                    - Accessibility and engagement features
                    - Trust-building elements

                **[Website Effectiveness]**
                • Analyze 2-3 key aspects of the website's effectiveness:
                    - Navigation and user experience
                    - Content organization and clarity
                    - Feature accessibility and functionality

                **[Recommendations]**
                • List 2-3 specific, actionable improvements:
                    - Engagement enhancement suggestions
                    - Accessibility improvements
                    - Content organization recommendations

                **[Quality Assessment]**
                    Evaluate the overall quality of your findings using this scale:
                        0.0-0.3: Little to no direct evidence
                        0.4-0.6: Some evidence but with gaps
                        0.7-0.8: Good evidence with minor gaps
                        0.9-1.0: Strong, comprehensive evidence
                    
                    - Confidence Level: [Insert your confidence level here]
                    - Explanation: [Briefly explain why you assigned this confidence level]


                2. Additional Notes:
                • Include 2-3 broader insights about:
                - Patterns in stakeholder engagement
                - Opportunities for enhancement
                - Notable strengths or challenges
                - Future considerations

                Formatting Requirements:
                - Use bullet points (•) for all listed items
                - Keep each point concise and specific
                - Include examples where relevant
                - Separate sections with blank lines
                - Start each main section with a number (1., 2.)
                - Use **Section Title** format for subsection titles
                """

            result = run_research_workflow(self.retriver, resarch_task, output_format, 3)
            state["resarch_result"] = result
        
        except Exception as e:
            state["errors"].append(f"Error in parallel research: {str(e)}")

        return state

   
    def create_analysis_graph(self) -> StateGraph:
        """Create the analysis workflow graph"""
        

        workflow = StateGraph(MainGraphState)
        
        # Add nodes
        workflow.add_node("stakeholders_researcher", self.get_stakeholders)
        workflow.add_node("main_researcher", self.main_research)
        
        # Define edges
        workflow.add_edge(START, "stakeholders_researcher")
        workflow.add_edge("stakeholders_researcher", "main_researcher")
        workflow.add_edge("main_researcher", END)

        return workflow