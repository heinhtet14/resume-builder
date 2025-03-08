import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.resume import Resume
from resume_builder.models.job import JobDescription

class ResumeGenerator:
    """Tool to generate a tailored resume based on an existing resume and job description."""
    
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
    
    def __call__(self, resume: Resume, job: JobDescription) -> Resume:
        """Generate a tailored resume."""
        try:
            llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.2)
            
            # Convert models to dictionaries for prompt
            resume_dict = resume.model_dump()
            job_dict = job.model_dump()
            
            template = """
            You are a professional resume writer and career coach. Your task is to create a tailored resume
            based on the applicant's existing resume and the job description they're applying for.
            
            Current Resume:
            {resume_info}
            
            Job Description:
            {job_info}
            
            Follow these guidelines:
            1. Highlight skills and experiences that match the job requirements
            2. Quantify achievements where possible
            3. Use relevant keywords from the job description
            4. Prioritize recent and relevant experience
            5. Focus on impact and results, not just responsibilities
            6. Keep the resume concise and focused
            
            Create an optimized version of the resume that targets this specific job. Return the result as a valid JSON object with the same structure as the input resume, but with the content tailored to the job description.
            
            Do not write in markdown or any other format - ONLY return a valid JSON object.
            """
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm | StrOutputParser()
            
            result = chain.invoke({
                "resume_info": json.dumps(resume_dict, indent=2),
                "job_info": json.dumps(job_dict, indent=2)
            })
            
            # Parse the JSON string to a Python dictionary
            try:
                parsed_result = json.loads(result)
                return Resume.model_validate(parsed_result)
            except json.JSONDecodeError:
                # If the result is not valid JSON, try to extract just the JSON part
                try:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        return Resume.model_validate(json.loads(json_str))
                    else:
                        raise ValueError("Could not extract valid JSON from the result")
                except Exception as e:
                    raise ValueError(f"Failed to generate optimized resume: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error with model: {str(e)}")