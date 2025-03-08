import os
import json
import time
import random
import re
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from resume_builder.models.resume import Resume
from resume_builder.models.job import JobDescription

class ATSOptimizer:
    """Tool to optimize a resume for Applicant Tracking Systems (ATS) with local fallbacks."""
    
    def __init__(self, model_name="gemini-1.5-pro", api_key=None):
        self.model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
        # Flag to track if we've hit quota limits
        self.quota_exhausted = False
    
    def _extract_keywords_local(self, job_description: JobDescription) -> List[str]:
        """
        Extract keywords locally without using the API.
        This is a fallback method when quota is exhausted.
        """
        keywords = set()
        
        # Start with all required and preferred skills
        for skill in job_description.required_skills + job_description.preferred_skills:
            keywords.add(skill)
        
        # Add job title components (split by spaces and remove common words)
        common_words = {"and", "the", "or", "for", "in", "at", "with", "to", "a", "an"}
        title_words = job_description.title.split()
        for word in title_words:
            if word.lower() not in common_words and len(word) > 2:
                keywords.add(word)
        
        # Extract important terms from responsibilities
        for resp in job_description.key_responsibilities:
            # Look for capitalized terms or terms in quotes
            capitalized = re.findall(r'\b[A-Z][a-zA-Z]+\b', resp)
            quoted = re.findall(r'"([^"]*)"', resp) + re.findall(r"'([^']*)'", resp)
            
            for term in capitalized + quoted:
                if len(term) > 2 and term.lower() not in common_words:
                    keywords.add(term)
        
        # Return as a list
        return list(keywords)
    
    def extract_keywords(self, job_description: JobDescription) -> List[str]:
        """
        Extract important keywords from a job description that would be 
        relevant for ATS systems.
        """
        # If we already know quota is exhausted, use local extraction immediately
        if self.quota_exhausted:
            print("Using local keyword extraction due to API quota exhaustion")
            return self._extract_keywords_local(job_description)
        
        try:
            # First get local keywords as a fallback
            local_keywords = self._extract_keywords_local(job_description)
            
            # If we have enough local keywords, don't bother with API call
            if len(local_keywords) >= 15:
                print("Using local keyword extraction (sufficient keywords found)")
                return local_keywords
            
            # Try API-based extraction with retry logic
            max_retries = 2  # Limit retries to conserve quota
            retries = 0
            backoff = 2
            
            while retries <= max_retries:
                try:
                    llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.1)
                    
                    template = """
                    Extract important keywords from this job description that would be 
                    relevant for ATS systems. Focus on hard skills, technical abilities,
                    tools, and domain knowledge.
                    
                    Job Description:
                    {job_description}
                    
                    Return ONLY a JSON array of keywords, with no explanation.
                    For example: ["Python", "AWS", "Machine Learning"]
                    """
                    
                    job_text = f"""
                    Title: {job_description.title}
                    Required Skills: {', '.join(job_description.required_skills)}
                    Preferred Skills: {', '.join(job_description.preferred_skills)}
                    Responsibilities: {', '.join(job_description.key_responsibilities)}
                    """
                    
                    prompt = PromptTemplate.from_template(template)
                    chain = prompt | llm | StrOutputParser()
                    
                    result = chain.invoke({"job_description": job_text})
                    
                    # Extract JSON array
                    json_start = result.find("[")
                    json_end = result.rfind("]") + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        keywords = json.loads(json_str)
                        
                        # Merge with local keywords for better coverage
                        combined = list(set(keywords + local_keywords))
                        return combined
                    else:
                        raise ValueError("No valid JSON array found in response")
                    
                except Exception as e:
                    retries += 1
                    if '429' in str(e) or 'Resource has been exhausted' in str(e):
                        print(f"API quota exhausted. Switching to local keyword extraction.")
                        self.quota_exhausted = True  # Mark quota as exhausted for future calls
                        return local_keywords
                    
                    if retries > max_retries:
                        print(f"API keyword extraction failed after {max_retries} retries.")
                        return local_keywords
                    
                    print(f"Keyword extraction error: {str(e)}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
            
            return local_keywords
            
        except Exception as e:
            print(f"Error in keyword extraction: {str(e)}")
            return self._extract_keywords_local(job_description)
    
    def analyze_resume_ats_score(self, resume: Resume, keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze how well a resume matches ATS keywords and score it.
        This function works entirely locally without API calls.
        """
        # Create a complete text representation of the resume
        resume_text = json.dumps(resume.model_dump()).lower()
        
        # Count keyword matches with smarter matching
        matches = []
        missing = []
        partial_matches = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact match
            if keyword_lower in resume_text:
                matches.append(keyword)
            else:
                # Check if all words in multi-word keyword appear
                all_words_present = True
                for word in keyword_lower.split():
                    if len(word) > 3 and word not in resume_text:  # Only check significant words
                        all_words_present = False
                        break
                
                if all_words_present and len(keyword_lower.split()) > 1:
                    partial_matches.append(keyword)
                else:
                    missing.append(keyword)
        
        # Compute score with partial credit for partial matches
        total_keywords = len(keywords)
        if total_keywords == 0:
            return {"score": 100, "matches": [], "missing": [], "partial_matches": [], "total_keywords": 0}
        
        match_percentage = ((len(matches) + (len(partial_matches) * 0.5)) / total_keywords) * 100
        
        return {
            "score": match_percentage,
            "matches": matches,
            "missing": missing,
            "partial_matches": partial_matches,
            "total_keywords": total_keywords
        }
    
    def _enhance_summary_locally(self, summary: str, missing_keywords: List[str], max_keywords=3) -> str:
        """
        Enhance a resume summary with missing keywords without using API calls.
        """
        # Choose a few most important keywords to incorporate
        keywords_to_add = missing_keywords[:max_keywords]
        if not keywords_to_add:
            return summary
        
        # Create a natural-sounding addition
        if len(keywords_to_add) == 1:
            addition = f" Proficient in {keywords_to_add[0]}."
        elif len(keywords_to_add) == 2:
            addition = f" Skilled in {keywords_to_add[0]} and {keywords_to_add[1]}."
        else:
            joined = ", ".join(keywords_to_add[:-1]) + f", and {keywords_to_add[-1]}"
            addition = f" Experienced with {joined}."
        
        # Add to summary if it doesn't already end with a period
        if summary.endswith('.'):
            enhanced_summary = summary[:-1] + addition
        else:
            enhanced_summary = summary + addition
            
        return enhanced_summary
    
    def optimize_resume_for_ats(self, resume: Resume, job: JobDescription, ats_analysis: Dict[str, Any]) -> Resume:
        """
        Optimize a resume for ATS systems with fallback to local processing.
        """
        # If quota is already exhausted or high score, use local optimization
        if self.quota_exhausted or ats_analysis["score"] > 70:
            return self._optimize_locally(resume, job, ats_analysis)
        
        try:
            # Try API-based optimization first
            llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0.2)
            
            template = """
            Optimize this resume summary and skills for ATS systems:
            
            Current Summary: {resume_summary}
            
            Current Skills: {resume_skills}
            
            Job Title: {job_title}
            
            Missing Keywords: {missing_keywords}
            
            Return ONLY a JSON object with:
            {{
              "summary": "improved summary with keywords naturally incorporated",
              "skills": ["skill1", "skill2", ...]
            }}
            """
            
            # Prepare a list of skills
            current_skills = resume.skills.technical
            if resume.skills.soft:
                current_skills.extend(resume.skills.soft)
            
            # Only use the most important missing keywords
            top_missing = ats_analysis["missing"][:5]
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | llm | StrOutputParser()
            
            result = chain.invoke({
                "resume_summary": resume.summary,
                "resume_skills": ", ".join(current_skills),
                "job_title": job.title,
                "missing_keywords": ", ".join(top_missing)
            })
            
            # Try to extract JSON
            try:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    updates = json.loads(json_str)
                    
                    # Create updated resume
                    updated_resume = resume.model_copy(deep=True)
                    
                    # Update summary if provided
                    if "summary" in updates:
                        updated_resume.summary = updates["summary"]
                    
                    # Update skills if provided
                    if "skills" in updates and isinstance(updates["skills"], list):
                        # Add new skills to technical skills
                        existing_skills_set = set(updated_resume.skills.technical)
                        for skill in updates["skills"]:
                            if skill not in existing_skills_set:
                                updated_resume.skills.technical.append(skill)
                    
                    return updated_resume
                else:
                    # Fallback to local optimization
                    print("Invalid JSON response from API, falling back to local optimization")
                    return self._optimize_locally(resume, job, ats_analysis)
            except Exception as e:
                print(f"Error parsing API response: {str(e)}")
                return self._optimize_locally(resume, job, ats_analysis)
                
        except Exception as e:
            if '429' in str(e) or 'Resource has been exhausted' in str(e):
                print("API quota exhausted, using local optimization")
                self.quota_exhausted = True
            else:
                print(f"ATS optimization error: {str(e)}")
            
            return self._optimize_locally(resume, job, ats_analysis)
    
    def _optimize_locally(self, resume: Resume, job: JobDescription, ats_analysis: Dict[str, Any]) -> Resume:
        """
        Optimize resume for ATS using purely local techniques.
        This function requires no API calls.
        """
        # Create a copy of the resume to modify
        updated_resume = resume.model_copy(deep=True)
        
        # 1. Add missing keywords to skills section
        missing_relevant = []
        
        # Check which missing keywords are in job requirements
        req_skills_lower = [s.lower() for s in job.required_skills]
        pref_skills_lower = [s.lower() for s in job.preferred_skills]
        
        for keyword in ats_analysis["missing"]:
            keyword_lower = keyword.lower()
            if (keyword_lower in req_skills_lower or 
                keyword_lower in pref_skills_lower or
                any(keyword_lower in resp.lower() for resp in job.key_responsibilities)):
                missing_relevant.append(keyword)
        
        # Add relevant missing skills
        existing_skills = set(s.lower() for s in updated_resume.skills.technical)
        for skill in missing_relevant:
            if skill.lower() not in existing_skills:
                updated_resume.skills.technical.append(skill)
        
        # 2. Enhance summary with important missing keywords
        # Choose keywords that appear in required skills or job title
        critical_keywords = []
        job_title_lower = job.title.lower()
        
        for keyword in ats_analysis["missing"]:
            keyword_lower = keyword.lower()
            if (keyword_lower in job_title_lower or
                keyword_lower in req_skills_lower):
                critical_keywords.append(keyword)
        
        # Enhance the summary
        updated_resume.summary = self._enhance_summary_locally(
            updated_resume.summary, 
            critical_keywords,
            max_keywords=3
        )
        
        return updated_resume
    
    def __call__(self, resume: Resume, job: JobDescription) -> Resume:
        """
        Optimize a resume to pass ATS systems for a specific job.
        """
        # 1. Extract important keywords from job description
        keywords = self.extract_keywords(job)
        
        # 2. Analyze how well the resume matches these keywords
        ats_analysis = self.analyze_resume_ats_score(resume, keywords)
        
        # 3. Print ATS analysis
        print(f"\nATS Analysis:")
        print(f"Current Score: {ats_analysis['score']:.1f}%")
        print(f"Matched Keywords ({len(ats_analysis['matches'])}): {', '.join(ats_analysis['matches'])}")
        if ats_analysis["partial_matches"]:
            print(f"Partial Matches ({len(ats_analysis['partial_matches'])}): {', '.join(ats_analysis['partial_matches'])}")
        print(f"Missing Keywords ({len(ats_analysis['missing'])}): {', '.join(ats_analysis['missing'])}")
        
        # 4. If score is already very high, skip optimization
        if ats_analysis["score"] > 90:
            print(f"\nATS score is already excellent ({ats_analysis['score']:.1f}%). Skipping optimization.")
            return resume
        
        # 5. Optimize the resume
        optimized_resume = self.optimize_resume_for_ats(resume, job, ats_analysis)
        
        # 6. Re-analyze the optimized resume
        new_analysis = self.analyze_resume_ats_score(optimized_resume, keywords)
        print(f"\nOptimized Resume Score: {new_analysis['score']:.1f}%")
        print(f"Improvement: +{new_analysis['score'] - ats_analysis['score']:.1f}%")
        
        return optimized_resume