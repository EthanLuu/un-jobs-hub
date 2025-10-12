"""Resume parsing service."""
import re
from typing import Dict, List
from pathlib import Path
import PyPDF2
from docx import Document


async def parse_resume(file_path: str, content_type: str) -> Dict:
    """Parse resume file and extract information."""
    # Extract text
    if content_type == "application/pdf":
        raw_text = extract_text_from_pdf(file_path)
    else:  # DOCX
        raw_text = extract_text_from_docx(file_path)
    
    # Extract structured information
    skills = extract_skills(raw_text)
    experience_years = extract_experience_years(raw_text)
    education = extract_education(raw_text)
    
    return {
        "raw_text": raw_text,
        "structured_data": {
            "skills": skills,
            "experience_years": experience_years,
            "education": education
        },
        "skills": skills,
        "experience_years": experience_years
    }


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    return text


def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text."""
    # Common skills to look for
    skill_keywords = [
        # Programming
        "python", "java", "javascript", "typescript", "c++", "sql",
        # Frameworks
        "react", "django", "fastapi", "flask", "node.js", "express",
        # Tools
        "git", "docker", "kubernetes", "aws", "azure", "gcp",
        # Soft skills
        "project management", "leadership", "communication", "teamwork",
        # UN-related
        "humanitarian", "development", "monitoring and evaluation", "m&e",
        "program management", "partnership", "coordination", "advocacy",
        "policy analysis", "research", "reporting", "budget management"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))


def extract_experience_years(text: str) -> int:
    """Extract years of experience from resume text."""
    # Look for patterns like "X years of experience"
    patterns = [
        r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\+?\s*years?",
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            years = int(match)
            max_years = max(max_years, years)
    
    return max_years


def extract_education(text: str) -> List[Dict]:
    """Extract education information from resume text."""
    education = []
    
    # Look for degree keywords
    degree_patterns = [
        r"(bachelor|master|phd|doctorate|mba|b\.?a\.?|m\.?a\.?|b\.?s\.?|m\.?s\.?)",
    ]
    
    for pattern in degree_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            
            education.append({
                "degree": match.group(0),
                "context": context.strip()
            })
    
    return education



