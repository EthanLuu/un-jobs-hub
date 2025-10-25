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
    """Calculate enhanced match score between resume and job."""
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
    
    # Calculate keyword match score
    if len(job_keywords) > 0:
        keyword_score = len(matching_keywords) / len(job_keywords)
    else:
        keyword_score = 0.5
    
    # Check experience requirement
    experience_score = 0.8  # Default
    if job.years_of_experience and resume.experience_years:
        if resume.experience_years >= job.years_of_experience:
            experience_score = 1.0
        else:
            # Gradual penalty for less experience
            experience_score = max(0.3, resume.experience_years / job.years_of_experience)
    
    # Check education level match
    education_score = 0.8  # Default
    if job.education_level and resume.education_level:
        education_levels = ["Diploma/Certificate", "Bachelor's", "Master's", "Doctorate"]
        job_level_idx = education_levels.index(job.education_level) if job.education_level in education_levels else 0
        resume_level_idx = education_levels.index(resume.education_level) if resume.education_level in education_levels else 0
        
        if resume_level_idx >= job_level_idx:
            education_score = 1.0
        else:
            education_score = max(0.4, resume_level_idx / job_level_idx)
    
    # Check language requirements
    language_score = 0.8  # Default
    if job.language_requirements:
        required_languages = [lang for lang, level in job.language_requirements.items() if level == "required"]
        if required_languages:
            # Simple check - could be enhanced with actual language detection
            language_score = 0.9  # Assume basic language skills
    
    # Check location preference (if available in resume)
    location_score = 0.8  # Default
    if job.location and resume_text_lower:
        # Check if location is mentioned in resume (preference indicator)
        if job.location.lower() in resume_text_lower:
            location_score = 1.0
    
    # Calculate weighted final score
    final_score = (
        keyword_score * 0.35 +
        experience_score * 0.25 +
        education_score * 0.15 +
        language_score * 0.15 +
        location_score * 0.10
    )
    final_score = min(1.0, max(0.0, final_score))
    
    # Generate recommendation based on score and missing elements
    if final_score >= 0.85:
        recommendation = "🌟 Excellent match! You meet most requirements and should definitely apply."
    elif final_score >= 0.70:
        recommendation = "✅ Good match. Highlight these skills in your application: " + ", ".join(missing_keywords[:3])
    elif final_score >= 0.50:
        recommendation = "⚠️ Moderate match. Consider developing these areas: " + ", ".join(missing_keywords[:4])
    elif final_score >= 0.30:
        recommendation = "📚 Limited match. Focus on gaining experience in: " + ", ".join(missing_keywords[:5])
    else:
        recommendation = "❌ Poor match. This position may not be suitable at this time."
    
    # Add specific advice based on missing elements
    if job.years_of_experience and resume.experience_years and resume.experience_years < job.years_of_experience:
        recommendation += f" Consider gaining {job.years_of_experience - resume.experience_years} more years of experience."
    
    if job.education_level and resume.education_level and resume.education_level != job.education_level:
        recommendation += f" Education requirement: {job.education_level}."
    
    # If OpenAI is available and configured, use it for better recommendations
    if openai_available and settings.openai_api_key:
        try:
            ai_recommendation = await get_ai_recommendation(resume, job, final_score, missing_keywords)
            if ai_recommendation:
                recommendation = ai_recommendation
        except Exception:
            pass  # Fall back to basic recommendation
    
    return {
        "score": round(final_score, 2),
        "matching_keywords": matching_keywords[:10],
        "missing_keywords": missing_keywords[:10],
        "recommendation": recommendation,
        "breakdown": {
            "keyword_match": round(keyword_score, 2),
            "experience_match": round(experience_score, 2),
            "education_match": round(education_score, 2),
            "language_match": round(language_score, 2),
            "location_match": round(location_score, 2)
        }
    }


def extract_keywords_from_job(job: Job) -> List[str]:
    """Extract important keywords from job posting with enhanced logic."""
    keywords = set()
    
    # Combine all text fields
    text = f"{job.title} {job.description} {job.qualifications or ''} {job.responsibilities or ''}"
    text_lower = text.lower()
    
    # Enhanced keyword categories for UN jobs
    keyword_categories = {
        # Education & Qualifications
        "education": ["bachelor", "master", "phd", "doctorate", "degree", "diploma", "certificate"],
        
        # Management & Leadership
        "management": ["project management", "program management", "team leadership", "strategic planning", 
                      "change management", "stakeholder management", "resource management"],
        
        # Technical Skills
        "technical": ["data analysis", "monitoring", "evaluation", "reporting", "budget", "finance", 
                     "procurement", "logistics", "hr", "it", "database", "statistics", "research"],
        
        # UN-specific Areas
        "un_areas": ["humanitarian", "development", "peacekeeping", "human rights", "gender", "climate", 
                    "sustainability", "partnership", "coordination", "advocacy", "policy"],
        
        # Languages
        "languages": ["english", "french", "spanish", "arabic", "chinese", "russian", "multilingual"],
        
        # Soft Skills
        "soft_skills": ["leadership", "teamwork", "communication", "negotiation", "problem solving", 
                       "adaptability", "cultural sensitivity", "interpersonal"],
        
        # Sectors
        "sectors": ["health", "education", "agriculture", "environment", "migration", "refugees", 
                   "children", "women", "disability", "elderly"],
        
        # Tools & Technologies
        "tools": ["excel", "powerpoint", "word", "outlook", "sharepoint", "sap", "oracle", "sql", 
                 "python", "r", "spss", "stata", "gis", "arcgis"]
    }
    
    # Extract keywords from each category
    for category, terms in keyword_categories.items():
        for term in terms:
            if term in text_lower:
                keywords.add(term)
    
    # Extract years of experience if mentioned
    exp_patterns = [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"minimum\s+(\d+)\s*years?",
        r"at\s+least\s+(\d+)\s*years?",
        r"(\d+)\s*-\s*(\d+)\s*years?"
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            if isinstance(matches[0], tuple):
                keywords.add(f"{matches[0][0]} years experience")
            else:
                keywords.add(f"{matches[0]} years experience")
    
    # Add job-specific metadata as keywords
    if job.category:
        keywords.add(job.category.lower())
    if job.grade:
        keywords.add(job.grade.lower())
    if job.contract_type:
        keywords.add(job.contract_type.lower())
    if job.organization:
        keywords.add(job.organization.lower())
    
    # Extract specific skills mentioned in qualifications
    skill_patterns = [
        r"experience\s+in\s+([^.,]+)",
        r"knowledge\s+of\s+([^.,]+)",
        r"familiarity\s+with\s+([^.,]+)",
        r"proficiency\s+in\s+([^.,]+)"
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            # Clean up the match and add as keyword
            clean_match = re.sub(r'\s+', ' ', match.strip())
            if len(clean_match) > 3 and len(clean_match) < 50:
                keywords.add(clean_match)
    
    # Remove very short or very long keywords
    filtered_keywords = []
    for keyword in keywords:
        if 3 <= len(keyword) <= 50 and not keyword.isdigit():
            filtered_keywords.append(keyword)
    
    return filtered_keywords


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



