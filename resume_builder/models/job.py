from typing import List, Optional
from pydantic import BaseModel

class JobDescription(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    required_skills: List[str]
    preferred_skills: List[str]
    key_responsibilities: List[str]
    company_values: Optional[List[str]] = None
    experience_years: Optional[str] = None
    education: Optional[List[str]] = None