import os
import json
from typing import Dict, List, Any, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.resume import Resume, Experience, Education, Project, Skills, ContactInfo

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
            All string fields must be non-null - use empty strings if you can't extract the information, but NEVER use null values.
            For arrays, if there's no relevant information, use an empty array [], not null.
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
    
    def validate_and_fix_resume_dict(self, resume_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the resume dictionary and fill in missing required fields.
        """
        # Ensure all required fields exist and have proper types
        if "contact" not in resume_dict or not isinstance(resume_dict["contact"], dict):
            resume_dict["contact"] = {}
            
        contact = resume_dict["contact"]
        for field in ["name", "email", "phone", "linkedin"]:
            if field not in contact or contact[field] is None:
                contact[field] = ""
        
        # Ensure summary exists
        if "summary" not in resume_dict or resume_dict["summary"] is None:
            resume_dict["summary"] = "Professional with experience in relevant fields."
        
        # Ensure skills section exists
        if "skills" not in resume_dict or not isinstance(resume_dict["skills"], dict):
            resume_dict["skills"] = {"technical": [], "soft": []}
        
        skills = resume_dict["skills"]
        if "technical" not in skills or skills["technical"] is None:
            skills["technical"] = []
        if "soft" not in skills or skills["soft"] is None:
            skills["soft"] = []
        
        # Ensure experience section exists and has valid structure
        if "experience" not in resume_dict or not isinstance(resume_dict["experience"], list):
            resume_dict["experience"] = []
            
        for i, exp in enumerate(resume_dict["experience"]):
            if not isinstance(exp, dict):
                resume_dict["experience"][i] = {
                    "title": "",
                    "company": "",
                    "location": "",
                    "duration": "",
                    "responsibilities": []
                }
                continue
                
            for field in ["title", "company", "location", "duration"]:
                if field not in exp or exp[field] is None:
                    exp[field] = ""
            
            if "responsibilities" not in exp or exp["responsibilities"] is None:
                exp["responsibilities"] = []
        
        # Ensure education section exists and has valid structure
        if "education" not in resume_dict or not isinstance(resume_dict["education"], list):
            resume_dict["education"] = []
            
        for i, edu in enumerate(resume_dict["education"]):
            if not isinstance(edu, dict):
                resume_dict["education"][i] = {
                    "degree": "",
                    "institution": "",
                    "location": "",
                    "year": ""
                }
                continue
                
            for field in ["degree", "institution", "location", "year"]:
                if field not in edu or edu[field] is None:
                    edu[field] = ""
        
        # Ensure projects section exists and has valid structure
        if "projects" not in resume_dict or not isinstance(resume_dict["projects"], list):
            resume_dict["projects"] = []
            
        for i, proj in enumerate(resume_dict["projects"]):
            if not isinstance(proj, dict):
                resume_dict["projects"][i] = {
                    "name": "",
                    "description": "",
                    "technologies": []
                }
                continue
                
            for field in ["name", "description"]:
                if field not in proj or proj[field] is None:
                    proj[field] = ""
            
            if "technologies" not in proj or proj["technologies"] is None:
                proj["technologies"] = []
        
        # Ensure certifications exist
        if "certifications" not in resume_dict or resume_dict["certifications"] is None:
            resume_dict["certifications"] = []
        
        return resume_dict
    
    def __call__(self, file_path: str) -> Resume:
        """Parse resume from a PDF file."""
        try:
            documents = self.load_resume(file_path)
            full_text = "\n".join([doc.page_content for doc in documents])
            resume_dict = self.extract_resume_info(full_text)
            
            # Validate and fix the resume dictionary
            validated_resume_dict = self.validate_and_fix_resume_dict(resume_dict)
            
            # Convert the dictionary to a Resume model
            try:
                return Resume.model_validate(validated_resume_dict)
            except Exception as validation_error:
                # If validation still fails, create a minimal valid Resume object
                print(f"Warning: Could not fully validate resume. Creating minimal valid resume. Error: {str(validation_error)}")
                
                # Create a minimal valid Resume object
                return Resume(
                    contact=ContactInfo(
                        name=validated_resume_dict.get("contact", {}).get("name", ""),
                        email=validated_resume_dict.get("contact", {}).get("email", ""),
                        phone=validated_resume_dict.get("contact", {}).get("phone", ""),
                        linkedin=validated_resume_dict.get("contact", {}).get("linkedin", "")
                    ),
                    summary=validated_resume_dict.get("summary", "Professional with experience in relevant fields."),
                    skills=Skills(
                        technical=validated_resume_dict.get("skills", {}).get("technical", []),
                        soft=validated_resume_dict.get("skills", {}).get("soft", [])
                    ),
                    experience=[
                        Experience(
                            title=exp.get("title", ""),
                            company=exp.get("company", ""),
                            location=exp.get("location", ""),
                            duration=exp.get("duration", ""),
                            responsibilities=exp.get("responsibilities", [])
                        ) for exp in validated_resume_dict.get("experience", [])
                    ],
                    education=[
                        Education(
                            degree=edu.get("degree", ""),
                            institution=edu.get("institution", ""),
                            location=edu.get("location", ""),
                            year=edu.get("year", "")
                        ) for edu in validated_resume_dict.get("education", [])
                    ],
                    projects=[
                        Project(
                            name=proj.get("name", ""),
                            description=proj.get("description", ""),
                            technologies=proj.get("technologies", [])
                        ) for proj in validated_resume_dict.get("projects", [])
                    ] if validated_resume_dict.get("projects") else None,
                    certifications=validated_resume_dict.get("certifications", [])
                )
            
        except Exception as e:
            raise ValueError(f"Error parsing resume: {str(e)}")