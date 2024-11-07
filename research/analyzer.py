
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


from research.models.research_findings import ListResearchFindings
from research.models.task_analysis import Queries, TaskAnalysis
from research.workflow.state import ResearchState
from retriver import Retriver



class Research:
    def __init__(self, retriver:Retriver):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.retriver = retriver

    def planner(self, state: ResearchState) -> ResearchState:
        """Split the task research task into small chanks"""
        task = state["task"]

        # Add your logic here
        messages = [
            SystemMessage(content=f"""You are a task analysis expert who helps break down complex tasks into guiding questions. 
                        Your expertise lies in:

                        Identifying key aspects that need to be addressed
                        Formulating clear, specific questions that guide thorough analysis
                        Suggesting relevant search queries for research
                          
                        Think step-by-step and break down the task by:

                            1.Creating a set of guiding questions to ensure comprehensive coverage, avoiding negative phrasing.
                            2.Developing targeted search queries to find relevant information, ensuring each question is specific and maintains context between keywords. 
                            For example:
                                Question: 'What is the capital of Brazil?'
                                Search query: 'capital of Brazil'
                          
                        Always maintain a focused, analytical approach and ensure questions are specific and actionable."""),
            HumanMessage(content=f"""Please analyze this task:

                {task}

                Break it down into:
                1. Guiding questions that will help verify all important aspects are covered
                2. Search queries to find relevant information
                Present your analysis in a clear structure with both questions and queries""")
        ]
        response = self.llm.with_structured_output(TaskAnalysis).invoke(messages)
        if not isinstance(response, TaskAnalysis):
            raise ValueError("Invalid response from LLM")

        state["guiding_questions"] = response.guiding_questions.guiding_questions
        state["search_queries"] = response.search_queries.search_queries
        return state

    def search_context(self, state: ResearchState) -> ResearchState:
        """Search for relevant context based on the task and search queries"""
        state["context"] = []
        
        queries = state["search_queries"]
        for query in queries:
            response = self.retriver.get_relevant_documents(query)
            state["context"].append(response)
        
        return state

    def optimize_search(self, state: ResearchState) -> ResearchState:
        """Optimize search results based on previous findings"""

        task = state["task"]
        missing_guiding_questions =  state["guiding_questions"]
        low_confidence_findings = [str(x) for x in state["lower_findings"]]
        state["current_iteration"] += 1


        SYSTEM_PROMPT = """You are a search query optimization expert. Your task is to refine and enhance search queries to ensure maximum effectiveness. Your refined queries should:

                - Be focused on the core concept, avoiding general or broad terms such as 'best,' 'how to,' 'steps for' or other non-specific words that don’t add value.
                - Be atomic, meaning each query is simple, specific, and captures the essential idea.
                - Be optimized for search engine performance, using precise and relevant terms that are likely to return high-quality, data-driven results.
                
                    For example:
                Query: 'best practices for project management in small teams' → Search query: 'project management small teams'
                Query: 'how to improve employee engagement in large companies' → Search query: 'employee engagement large companies'
                Query: 'steps for creating an effective social media strategy' → Search query: 'effective social media strategy'"""

        HUMAN_PROMPT = f"""
            Based on the research analysis, generate targeted search queries:

            Original Task:
            {task}

            Guiding Questions That Need Answers:
            {missing_guiding_questions}

            Current Findings with Low Confidence:
            {low_confidence_findings}

            Create specific search queries that will help find:
            1. Direct answers to missing questions
            2. Additional evidence for low-confidence findings
            3. Recent data and statistics

            Format each query to be search-engine friendly. Focus on getting factual, authoritative information.
            List each query with a brief explanation of what information it seeks.

        """

        response = self.llm.with_structured_output(Queries).invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=HUMAN_PROMPT)])

        if not isinstance(response, Queries):
            raise ValueError("Invalid response from LLM")
        
        state["search_queries"] = response.search_queries

        return state

    def analyze_finfind(self, state: ResearchState) -> ResearchState:
        """Analyze research context and extract structured findings"""
        context = state["context"]
        guiding_questions = state["guiding_questions"]

        SYSTEM_PROMPT = """
        You are a precise research analyst specializing in extracting structured findings from research content. Your task is to:
        1. Analyze research text carefully
        2. Extract clear answers to guiding questions
        3. Identify specific supporting evidence
        4. Assign confidence scores based on evidence quality
        5. Generate search queries for any findings with confidence below 0.8

        For each finding, you must provide:
        - A clear, concise answer
        - Direct quotes or specific evidence from the source
        - A confidence score (0-1) based on:
            * 0.0-0.3: Little to no direct evidence
            * 0.4-0.6: Some evidence but with gaps
            * 0.7-0.8: Good evidence with minor gaps
            * 0.9-1.0: Strong, comprehensive evidence
        - Search queries if confidence is below 0.8, focused on filling the specific gaps in knowledge
        """

        HUMAN_PROMPT = f"""
        Please analyze this research content and provide structured findings:

        Research Text:
        {context}

        Guiding Questions:
        {guiding_questions}"""

        prompt = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=HUMAN_PROMPT)]
        response = self.llm.with_structured_output(ListResearchFindings).invoke(prompt)

        if not isinstance(response, ListResearchFindings):
            raise ValueError("Invalid response from LLM")
        
        state["lower_findings"] = []

        for finding in response.findings:
            if finding.question in guiding_questions:
                if finding.confidence >= 0.7:
                    state["findings"].append(finding)
                    guiding_questions.remove(finding.question)
                else:
                    state["lower_findings"].append(finding)

        state["guiding_questions"] = guiding_questions
        return state

    def check_completion(self, state: ResearchState) -> bool:
        """Check if research is complete based on multiple conditions"""
        within_iterations = state["current_iteration"] < state["max_iterations"]
        no_remaining_questions = len(state["guiding_questions"]) == 0
        
        # Return True only if all conditions are met
        return not within_iterations or  no_remaining_questions

    def summarize_findings(self, state: ResearchState) -> ResearchState:
        """Summarize research findings and evaluate the level of the findings"""
        system = """You are a research summarization expert. 
            Your task is to summarize the key findings of the research process and evaluate the level of the findings"""

        human = f"""Summarize the research based on the findings and task:
                Task:
                {state['task']}

                Findings:
                {state['findings']}

                Lower Confidence Findings:
                {state['lower_findings']}

                Output Format:
                {state['output_format']}"""


        messages = [SystemMessage(content=system),HumanMessage(content=human)]

        response = self.llm.invoke(messages)
        state["answer"] = str(response.content)

        return state