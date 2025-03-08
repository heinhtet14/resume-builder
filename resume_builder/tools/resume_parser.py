import os
import json
from typing import Dict, List, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.resume import Resume

class ResumeParser:
    """Tool to parse and extract information from a resume."""
    
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
    
    def load_resume(self, file_path: str) -> List[Document]:
        """Load a resume from a PDF file."""
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return documents
        else:
            raise ValueError("Unsupported file format. Please provide a PDF file.")
    
    def extract_resume_info(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured information from resume text."""
        try:
            llm = ChatGoogleGenerativeAI(model=self.model_name)
            
            template = """
            Extract the following information from the resume text:
            
            1. Contact Information
            2. Professional Summary
            3. Skills (technical and soft skills)
            4. Work Experience
            5. Education
            6. Certifications
            7. Projects (if any)
            
            Resume text:
            {resume_text}
            
            Return a JSON object with the following structure:
            ```json
            {{
                "contact": {{
                    "name": "",
                    "email": "",
                    "phone": "",
                    "linkedin": ""
                }},
                "summary": "",
                "skills": {{
                    "technical": [],
                    "soft": []
                }},
                "experience": [
                    {{
                        "title": "",
                        "company": "",
                        "location": "",
                        "duration": "",
                        "responsibilities": []
                    }}
                ],
                "education": [
                    {{
                        "degree": "",
                        "institution": "",
                        "location": "",
                        "year": ""
                    }}
                ],
                "certifications": [],
                "projects": [
                    {{
                        "name": "",
                        "description": "",
                        "technologies": []
                    }}
                ]
            }}
            ```
            
            Make sure the JSON is valid and all arrays have at least one element if the information is present in the resume.
            """
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm | StrOutputParser()
            
            result = chain.invoke({"resume_text": resume_text})
            
            # Parse the JSON string to a Python dictionary
            try:
                parsed_result = json.loads(result)
                return parsed_result
            except json.JSONDecodeError:
                # If the result is not valid JSON, try to extract just the JSON part
                try:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        return json.loads(json_str)
                    else:
                        raise ValueError("Could not extract valid JSON from the result")
                except Exception as e:
                    raise ValueError(f"Failed to parse resume information: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error with model: {str(e)}")
    
    def __call__(self, file_path: str) -> Resume:
        """Parse resume from a PDF file."""
        try:
            documents = self.load_resume(file_path)
            full_text = "\n".join([doc.page_content for doc in documents])
            resume_dict = self.extract_resume_info(full_text)
            
            # Convert the dictionary to a Resume model
            return Resume.model_validate(resume_dict)
            
        except Exception as e:
            raise ValueError(f"Error parsing resume: {str(e)}")