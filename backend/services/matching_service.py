"""Job matching service using AI with enhanced algorithms."""
import re
import hashlib
from typing import Dict, List, Set, Optional
from models.resume import Resume
from models.job import Job
from config import settings
from utils.keyword_extraction import (
    KeywordExtractor,
    calculate_weighted_keyword_match,
    fuzzy_match_score
)
from utils.cache import cache

try:
    from openai import AsyncOpenAI
    openai_available = True
except ImportError:
    openai_available = False


# Global keyword extractor instance
keyword_extractor = KeywordExtractor()


async def calculate_match_score(resume: Resume, job: Job) -> Dict:
    """Calculate enhanced match score between resume and job with caching."""
    # Generate cache key
    cache_key = f"match:{resume.id}:{job.id}"

    # Try to get from cache
    cached_result = cache.get_json(cache_key)
    if cached_result:
        return cached_result

    # Extract keywords with importance weights from job
    job_text = f"{job.title} {job.description} {job.qualifications or ''} {job.responsibilities or ''}"
    job_keywords = keyword_extractor.extract_keywords_with_importance(job_text, max_keywords=30)

    # Extract resume data
    resume_skills = resume.skills or []
    resume_text = resume.raw_text or ""

    # Calculate weighted keyword match with fuzzy matching
    matching_keywords, missing_keywords, keyword_score = calculate_weighted_keyword_match(
        resume_text,
        resume_skills,
        job_keywords
    )

    # Check experience requirement with improved scoring
    experience_score = calculate_experience_score(
        job.years_of_experience,
        resume.experience_years
    )

    # Check education level match with improved logic
    education_score = calculate_education_score(
        job.education_level,
        resume.education_level
    )

    # Check language requirements with fuzzy matching
    language_score = calculate_language_score(
        job.language_requirements,
        resume_text,
        resume_skills
    )

    # Check location preference
    location_score = calculate_location_score(
        job.location,
        resume_text
    )

    # Calculate weighted final score with adjusted weights
    final_score = (
        keyword_score * 0.40 +      # Increased from 0.35
        experience_score * 0.25 +
        education_score * 0.15 +
        language_score * 0.12 +     # Slightly reduced
        location_score * 0.08       # Reduced from 0.10
    )
    final_score = min(1.0, max(0.0, final_score))

    # Extract top matching and missing keywords (with weights)
    top_matching = [kw for kw, _ in matching_keywords[:10]]
    top_missing = [kw for kw, _ in missing_keywords[:10]]

    # Generate recommendation based on score and missing elements
    recommendation = generate_recommendation(
        final_score,
        top_missing,
        job,
        resume
    )

    # If OpenAI is available and configured, use it for better recommendations
    if openai_available and settings.openai_api_key and final_score >= 0.5:
        try:
            ai_recommendation = await get_ai_recommendation(
                resume,
                job,
                final_score,
                top_missing
            )
            if ai_recommendation:
                recommendation = ai_recommendation
        except Exception:
            pass  # Fall back to basic recommendation

    result = {
        "score": round(final_score, 2),
        "matching_keywords": top_matching,
        "missing_keywords": top_missing,
        "recommendation": recommendation,
        "breakdown": {
            "keyword_match": round(keyword_score, 2),
            "experience_match": round(experience_score, 2),
            "education_match": round(education_score, 2),
            "language_match": round(language_score, 2),
            "location_match": round(location_score, 2)
        }
    }

    # Cache result for 1 hour
    cache.set_json(cache_key, result, ttl=3600)

    return result


def calculate_experience_score(
    required_years: Optional[int],
    candidate_years: Optional[int]
) -> float:
    """Calculate experience match score with improved logic."""
    if not required_years:
        return 0.9  # No requirement specified

    if not candidate_years:
        return 0.5  # Unknown candidate experience

    if candidate_years >= required_years:
        # Bonus for exceeding requirements
        if candidate_years > required_years * 1.5:
            return 1.0
        return 0.95 + (candidate_years - required_years) / required_years * 0.05

    # Graduated penalty for less experience
    ratio = candidate_years / required_years
    if ratio >= 0.75:  # Within 25% of requirement
        return 0.85
    elif ratio >= 0.5:  # Within 50% of requirement
        return 0.70
    else:
        return max(0.30, ratio)


def calculate_education_score(
    required_level: Optional[str],
    candidate_level: Optional[str]
) -> float:
    """Calculate education match score with improved logic."""
    if not required_level:
        return 0.9  # No requirement specified

    if not candidate_level:
        return 0.6  # Unknown candidate education

    education_levels = {
        "High School": 1,
        "Diploma/Certificate": 2,
        "Bachelor's": 3,
        "Master's": 4,
        "Doctorate": 5,
        "PhD": 5
    }

    required_idx = education_levels.get(required_level, 3)
    candidate_idx = education_levels.get(candidate_level, 3)

    if candidate_idx >= required_idx:
        # Bonus for higher education
        if candidate_idx > required_idx:
            return 1.0
        return 0.95
    else:
        # Penalty for lower education
        ratio = candidate_idx / required_idx
        return max(0.40, ratio * 0.8)


def calculate_language_score(
    language_requirements: Optional[Dict],
    resume_text: str,
    resume_skills: List[str]
) -> float:
    """Calculate language match score with fuzzy matching."""
    if not language_requirements:
        return 0.9  # No requirement specified

    required_languages = [
        lang.lower()
        for lang, level in language_requirements.items()
        if level == "required"
    ]

    if not required_languages:
        return 0.9

    resume_text_lower = resume_text.lower()
    resume_skills_lower = [s.lower() for s in resume_skills]

    matched_count = 0
    for lang in required_languages:
        # Check exact match
        if lang in resume_text_lower or lang in resume_skills_lower:
            matched_count += 1
            continue

        # Check fuzzy match
        for skill in resume_skills_lower:
            if fuzzy_match_score(lang, skill) >= 0.8:
                matched_count += 1
                break

    if len(required_languages) == 0:
        return 0.9

    match_ratio = matched_count / len(required_languages)
    return 0.5 + (match_ratio * 0.5)  # Score between 0.5 and 1.0


def calculate_location_score(
    job_location: Optional[str],
    resume_text: str
) -> float:
    """Calculate location preference score."""
    if not job_location:
        return 0.85  # No location specified

    if not resume_text:
        return 0.75  # Unknown preference

    resume_text_lower = resume_text.lower()
    location_lower = job_location.lower()

    # Exact match
    if location_lower in resume_text_lower:
        return 1.0

    # Check for country name or city
    location_parts = location_lower.split(',')
    for part in location_parts:
        part = part.strip()
        if part and part in resume_text_lower:
            return 0.95

    # Default - no explicit preference
    return 0.75


def generate_recommendation(
    score: float,
    missing_keywords: List[str],
    job: Job,
    resume: Resume
) -> str:
    """Generate detailed recommendation based on match score and gaps."""
    if score >= 0.85:
        recommendation = "🌟 Excellent match! You meet most requirements and should definitely apply. "
        if missing_keywords:
            recommendation += f"To strengthen your application, highlight experience with: {', '.join(missing_keywords[:2])}."
    elif score >= 0.70:
        recommendation = "✅ Good match! You meet many key requirements. "
        if missing_keywords:
            recommendation += f"Consider emphasizing these skills in your application: {', '.join(missing_keywords[:3])}."
    elif score >= 0.55:
        recommendation = "⚠️ Moderate match. You have some relevant experience. "
        if missing_keywords:
            recommendation += f"To improve your chances, develop experience in: {', '.join(missing_keywords[:4])}."
    elif score >= 0.35:
        recommendation = "📚 Limited match. This position may be a stretch. "
        if missing_keywords:
            recommendation += f"Focus on gaining experience in: {', '.join(missing_keywords[:5])}."
    else:
        recommendation = "❌ Poor match. Consider positions better aligned with your background. "
        if missing_keywords and len(missing_keywords) > 3:
            recommendation += f"Key gaps include: {', '.join(missing_keywords[:3])}."

    # Add specific advice based on gaps
    if job.years_of_experience and resume.experience_years:
        if resume.experience_years < job.years_of_experience:
            gap = job.years_of_experience - resume.experience_years
            recommendation += f" Note: Position requires {gap} more year(s) of experience."

    if job.education_level and resume.education_level:
        education_levels = ["High School", "Diploma/Certificate", "Bachelor's", "Master's", "Doctorate"]
        job_level_idx = education_levels.index(job.education_level) if job.education_level in education_levels else -1
        resume_level_idx = education_levels.index(resume.education_level) if resume.education_level in education_levels else -1

        if resume_level_idx >= 0 and job_level_idx >= 0 and resume_level_idx < job_level_idx:
            recommendation += f" Education requirement: {job.education_level} degree."

    return recommendation


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



