import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from resume_builder.tools.resume_parser import ResumeParser
from resume_builder.tools.job_analyzer import JobDescriptionAnalyzer
from resume_builder.tools.resume_generator import ResumeGenerator

def create_resume_agent(model_name="gemini-1.5-pro", verbose=True, api_key=None):
    """Create a ReAct agent for resume optimization."""
    
    # Set API key if provided
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    # Initialize tools
    resume_parser = ResumeParser(model_name=model_name, api_key=api_key)
    job_analyzer = JobDescriptionAnalyzer(model_name=model_name, api_key=api_key)
    resume_generator = ResumeGenerator(model_name=model_name, api_key=api_key)
    
    # Define tools for the agent
    tools = [
        Tool(
            name="ResumeParser",
            func=resume_parser,
            description="Parse resume information from a PDF file. Input should be a file path to the PDF resume."
        ),
        Tool(
            name="JobDescriptionAnalyzer",
            func=job_analyzer,
            description="Analyze a job description to extract key requirements, skills, and values."
        ),
        Tool(
            name="ResumeGenerator",
            func=resume_generator,
            description="""Generate a tailored resume based on the applicant's information and job description analysis. 
                         Input should be a dictionary with two keys: 'resume' (a Resume object) and 'job' (a JobDescription object)."""
        )
    ]
    
    # Create the React agent
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    
    agent_prompt = """You are an AI assistant specialized in resume optimization. Your goal is to help job seekers tailor their resumes to specific job descriptions to maximize their chances of getting interviews.

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