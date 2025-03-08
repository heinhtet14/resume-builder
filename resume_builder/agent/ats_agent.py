import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from resume_builder.tools.ats_optimizer import ATSOptimizer
from resume_builder.models.resume import Resume
from resume_builder.models.job import JobDescription

def create_ats_optimization_agent(model_name="gemini-1.5-pro", verbose=True, api_key=None):
    """Create a ReAct agent for ATS optimization."""
    
    # Set API key if provided
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    # Initialize the ATS optimizer tool
    ats_optimizer = ATSOptimizer(model_name=model_name, api_key=api_key)
    
    # Define tools for the agent
    tools = [
        Tool(
            name="ATSOptimizer",
            func=ats_optimizer,
            description="""Optimize a resume to pass Applicant Tracking Systems (ATS) for a specific job.
                        Input should be a dictionary with two keys: 'resume' (a Resume object) and 'job' (a JobDescription object)."""
        )
    ]
    
    # Create the React agent
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    
    agent_prompt = """You are an AI assistant specialized in optimizing resumes to pass Applicant Tracking Systems (ATS).
    Your goal is to help job seekers improve their resumes to maximize their chances of getting past automated resume screening systems.

    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat multiple times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    {agent_scratchpad}
    """
    
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=PromptTemplate.from_template(agent_prompt)
    )
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    return agent_executor