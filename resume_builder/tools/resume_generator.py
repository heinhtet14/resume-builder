# Fixing resume_builder/tools/resume_generator.py

import os
import json
import re
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.resume import Resume
from resume_builder.models.job import JobDescription

class ResumeGenerator:
    """Tool to generate a tailored resume based on an existing resume, job description, and keywords."""
    
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
    
    def _fix_json_string(self, json_str: str) -> str:
        """
        Attempt to fix common JSON formatting issues.
        """
        # Fix unescaped quotes in JSON strings
        fixed = re.sub(r'(?<!\\)"(?=(.*?"[^:,\{\}\[\]]*[:,\]\}]))', r'\"', json_str)
        
        # Fix trailing commas in arrays and objects
        fixed = re.sub(r',\s*([\}\]])', r'\1', fixed)
        
        # Fix missing commas between elements
        fixed = re.sub(r'(true|false|null|"[^"]*"|[0-9]+)\s*("|\{|\[)', r'\1, \2', fixed)
        
        return fixed
    
    def _sanitize_json_from_llm(self, text: str) -> str:
        """
        Extract and sanitize JSON from LLM output.
        
        Args:
            text: The raw text output from the LLM
            
        Returns:
            Sanitized JSON string
        """
        # Find JSON content
        json_start = text.find("{")
        if json_start == -1:
            raise ValueError("No JSON object found in the response")
            
        json_end = text.rfind("}") + 1
        if json_end <= json_start:
            raise ValueError("Invalid JSON structure in the response")
            
        json_content = text[json_start:json_end]
        
        # Try to fix common JSON issues
        return self._fix_json_string(json_content)
    
    def __call__(self, input_data: Dict[str, Any]) -> Resume:
        """
        Generate a tailored resume.
        
        Args:
            input_data: Dictionary with 'resume' (Resume object), 
                       'job' (JobDescription object), and 
                       'keywords' (list of strings, optional)
        
        Returns:
            Optimized Resume object
        """
        try:
            # Extract inputs
            if isinstance(input_data, dict):
                resume = input_data.get('resume')
                job = input_data.get('job')
                keywords = input_data.get('keywords', [])
            else:
                # Handle legacy input format (just resume and job)
                resume = input_data
                job = None
                keywords = []
                
            if not resume:
                raise ValueError("Resume is required")
            
            llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.2)
            
            # Convert models to dictionaries for prompt
            resume_dict = resume.model_dump()
            job_dict = job.model_dump() if job else {}
            
            template = """
            You are a professional resume writer and career coach. Your task is to create a tailored resume
            based on the applicant's existing resume and the job description they're applying for.
            
            Current Resume:
            {resume_info}
            
            Job Description:
            {job_info}
            
            User-Specified Keywords to Include (prioritize these):
            {keywords}
            
            Follow these guidelines:
            1. Highlight skills and experiences that match the job requirements
            2. Quantify achievements where possible
            3. Use relevant keywords from the job description
            4. Prioritize recent and relevant experience
            5. Focus on impact and results, not just responsibilities
            6. Keep the resume concise and focused
            7. Make sure to incorporate the user-specified keywords naturally into the resume
            
            Create an optimized version of the resume that targets this specific job. Return the result as a valid, properly formatted JSON object with the same structure as the input resume, but with the content tailored to the job description.
            
            DO NOT include any explanations, markdown formatting, or text outside the JSON structure. Response MUST be a single, valid JSON object only.
            """
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm | StrOutputParser()
            
            result = chain.invoke({
                "resume_info": json.dumps(resume_dict, indent=2),
                "job_info": json.dumps(job_dict, indent=2),
                "keywords": ", ".join(keywords) if keywords else "None specified"
            })
            
            # Parse the JSON string to a Python dictionary
            try:
                # First try to parse the JSON as is
                parsed_result = json.loads(result)
                return Resume.model_validate(parsed_result)
            except json.JSONDecodeError as e:
                # If that fails, try to extract and fix the JSON
                try:
                    sanitized_json = self._sanitize_json_from_llm(result)
                    parsed_result = json.loads(sanitized_json)
                    return Resume.model_validate(parsed_result)
                except Exception as json_error:
                    # If all parsing fails, make one more attempt with a simplified approach
                    try:
                        # Find the JSON object in the text
                        json_start = result.find("{")
                        json_end = result.rfind("}") + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            # Extract just the JSON part and try to fix common issues
                            json_str = result[json_start:json_end]
                            
                            # Remove all non-ASCII characters
                            json_str = ''.join(char for char in json_str if ord(char) < 128)
                            
                            # Try to make it valid JSON
                            # Replace unescaped quotes in values
                            json_str = re.sub(r': ?"([^"]*)"([^,\}])', r': "\1\"\2', json_str)
                            
                            parsed_result = json.loads(json_str)
                            return Resume.model_validate(parsed_result)
                        else:
                            raise ValueError("Could not extract valid JSON from the result")
                    except Exception as e:
                        # If all attempts fail, raise a descriptive error
                        error_msg = f"Failed to generate optimized resume: {str(e)}\n"
                        error_msg += "The model returned malformed JSON. Please try again."
                        raise ValueError(error_msg)
        except Exception as e:
            # Add result debugging info if available
            error_msg = f"Error with model: {str(e)}"
            raise ValueError(error_msg)