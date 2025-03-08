import os
import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.job import JobDescription

class JobDescriptionAnalyzer:
    """Tool to analyze job descriptions and extract key requirements."""
    
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
    
    def __call__(self, job_description: str) -> JobDescription:
        """Extract key requirements and preferences from a job description."""
        try:
            llm = ChatGoogleGenerativeAI(model=self.model_name)
            
            template = """
            Analyze the following job description and extract:
            
            1. Job title
            2. Company name (if mentioned)
            3. Location (if mentioned)
            4. Required skills and technologies
            5. Preferred skills and qualifications
            6. Key responsibilities
            7. Company values and culture hints
            8. Years of experience required
            9. Education requirements
            
            Job Description:
            {job_description}
            
            Return a JSON object with the following structure:
            ```json
            {{
                "title": "",
                "company": "",
                "location": "",
                "required_skills": [],
                "preferred_skills": [],
                "key_responsibilities": [],
                "company_values": [],
                "experience_years": "",
                "education": []
            }}
            ```
            
            Make sure the JSON is valid and all arrays have at least one element if the information is present in the job description.
            """
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm | StrOutputParser()
            
            result = chain.invoke({"job_description": job_description})
            
            # Parse the JSON string to a Python dictionary
            try:
                parsed_result = json.loads(result)
                return JobDescription.model_validate(parsed_result)
            except json.JSONDecodeError:
                # If the result is not valid JSON, try to extract just the JSON part
                try:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        return JobDescription.model_validate(json.loads(json_str))
                    else:
                        raise ValueError("Could not extract valid JSON from the result")
                except Exception as e:
                    raise ValueError(f"Failed to parse job description: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error with model: {str(e)}")