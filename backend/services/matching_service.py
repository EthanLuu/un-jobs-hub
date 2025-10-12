"""Job matching service using AI."""
import re
from typing import Dict, List, Set
from models.resume import Resume
from models.job import Job
from config import settings

try:
    from openai import AsyncOpenAI
    openai_available = True
except ImportError:
    openai_available = False


async def calculate_match_score(resume: Resume, job: Job) -> Dict:
    """Calculate match score between resume and job."""
    # Extract keywords from job
    job_keywords = extract_keywords_from_job(job)
    
    # Extract skills from resume
    resume_skills = set(resume.skills or [])
    resume_text_lower = resume.raw_text.lower()
    
    # Find matching and missing keywords
    matching_keywords = []
    missing_keywords = []
    
    for keyword in job_keywords:
        if keyword.lower() in resume_text_lower or keyword.lower() in [s.lower() for s in resume_skills]:
            matching_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calculate basic score
    if len(job_keywords) > 0:
        basic_score = len(matching_keywords) / len(job_keywords)
    else:
        basic_score = 0.5
    
    # Check experience requirement
    if job.years_of_experience and resume.experience_years:
        if resume.experience_years >= job.years_of_experience:
            experience_score = 1.0
        else:
            experience_score = resume.experience_years / job.years_of_experience
    else:
        experience_score = 0.8
    
    # Calculate final score (weighted average)
    final_score = (basic_score * 0.7) + (experience_score * 0.3)
    final_score = min(1.0, max(0.0, final_score))
    
    # Generate recommendation
    if final_score >= 0.8:
        recommendation = "Excellent match! You meet most requirements for this position."
    elif final_score >= 0.6:
        recommendation = "Good match. Consider highlighting these skills: " + ", ".join(missing_keywords[:3])
    elif final_score >= 0.4:
        recommendation = "Moderate match. Focus on developing: " + ", ".join(missing_keywords[:5])
    else:
        recommendation = "Limited match. Consider gaining experience in: " + ", ".join(missing_keywords[:5])
    
    # If OpenAI is available and configured, use it for better recommendations
    if openai_available and settings.openai_api_key:
        try:
            recommendation = await get_ai_recommendation(resume, job, final_score, missing_keywords)
        except Exception:
            pass  # Fall back to basic recommendation
    
    return {
        "score": round(final_score, 2),
        "matching_keywords": matching_keywords[:10],
        "missing_keywords": missing_keywords[:10],
        "recommendation": recommendation
    }


def extract_keywords_from_job(job: Job) -> List[str]:
    """Extract important keywords from job posting."""
    keywords = set()
    
    # Combine all text fields
    text = f"{job.title} {job.description} {job.qualifications or ''} {job.responsibilities or ''}"
    text_lower = text.lower()
    
    # Common important keywords for UN jobs
    important_terms = [
        # Education
        "bachelor", "master", "phd", "degree",
        # Experience areas
        "project management", "program management", "monitoring", "evaluation",
        "humanitarian", "development", "partnership", "coordination",
        "policy", "research", "advocacy", "communication",
        # Technical
        "budget", "finance", "procurement", "logistics", "hr",
        "data analysis", "reporting", "planning", "strategy",
        # Soft skills
        "leadership", "teamwork", "multilingual", "english", "french",
    ]
    
    for term in important_terms:
        if term in text_lower:
            keywords.add(term)
    
    # Extract years of experience if mentioned
    exp_match = re.search(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text_lower)
    if exp_match:
        keywords.add(f"{exp_match.group(1)} years experience")
    
    # Add category and grade as keywords
    if job.category:
        keywords.add(job.category.lower())
    if job.grade:
        keywords.add(job.grade.lower())
    
    return list(keywords)


async def get_ai_recommendation(
    resume: Resume,
    job: Job,
    score: float,
    missing_keywords: List[str]
) -> str:
    """Generate AI-powered recommendation using OpenAI."""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""
    Based on the following information, provide a brief, actionable recommendation 
    for the candidate (2-3 sentences):
    
    Job Title: {job.title}
    Organization: {job.organization}
    Match Score: {score:.0%}
    Missing Skills/Keywords: {', '.join(missing_keywords[:5])}
    
    Candidate Experience: {resume.experience_years} years
    Candidate Skills: {', '.join((resume.skills or [])[:10])}
    
    Provide constructive advice on how to improve their chances or whether to apply.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a career advisor specializing in UN and international organization jobs."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()



