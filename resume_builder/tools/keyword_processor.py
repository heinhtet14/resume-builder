# New file: resume_builder/tools/keyword_processor.py

from typing import Dict, List, Any
from resume_builder.models.job import JobDescription

class KeywordProcessor:
    """Tool to process and select the most relevant keywords from user input."""
    
    def __call__(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Process user-provided keywords and select the most relevant ones.
        
        Args:
            input_data: Dictionary with 'keywords' (list of user keywords), 
                       'max_count' (max number to select), and 
                       'job' (JobDescription object)
        
        Returns:
            List of selected keywords
        """
        keywords = input_data.get('keywords', [])
        max_count = input_data.get('max_count', 10)
        job = input_data.get('job')
        
        # If no keywords or job, return empty list
        if not keywords or not job:
            return []
        
        # Extract required and preferred skills from job for comparison
        job_skills = set([skill.lower() for skill in job.required_skills + job.preferred_skills])
        
        # Score keywords based on relevance to the job
        scored_keywords = []
        for keyword in keywords:
            score = 0
            keyword_lower = keyword.lower()
            
            # Check for exact match with job skills
            if keyword_lower in job_skills:
                score += 10
            
            # Check for partial match with job skills
            for skill in job_skills:
                if keyword_lower in skill or skill in keyword_lower:
                    score += 5
                    break
            
            # Check for presence in job title
            if keyword_lower in job.title.lower():
                score += 8
            
            # Check for presence in job responsibilities
            for resp in job.key_responsibilities:
                if keyword_lower in resp.lower():
                    score += 3
                    break
            
            scored_keywords.append((keyword, score))
        
        # Sort keywords by score (descending) and take top max_count
        sorted_keywords = [kw for kw, score in sorted(scored_keywords, key=lambda x: x[1], reverse=True)]
        selected_keywords = sorted_keywords[:max_count]
        
        print(f"Selected keywords: {', '.join(selected_keywords)}")
        return selected_keywords