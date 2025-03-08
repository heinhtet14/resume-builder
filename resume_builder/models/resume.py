from typing import List, Optional
from pydantic import BaseModel

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    duration: str
    responsibilities: List[str]
    achievements: Optional[List[str]] = None

class Education(BaseModel):
    degree: str
    institution: str
    location: Optional[str] = None
    year: str
    gpa: Optional[str] = None
    highlights: Optional[List[str]] = None

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    url: Optional[str] = None
    duration: Optional[str] = None

class Skills(BaseModel):
    technical: List[str]
    soft: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    certifications: Optional[List[str]] = None

class Resume(BaseModel):
    contact: ContactInfo
    summary: str
    skills: Skills
    experience: List[Experience]
    education: List[Education]
    projects: Optional[List[Project]] = None
    certifications: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    awards: Optional[List[str]] = None