"""
Enhanced keyword extraction and text analysis utilities.

Provides:
- TF-IDF based keyword extraction
- Fuzzy string matching
- Skill importance weighting
- N-gram extraction
"""

from typing import List, Dict, Set, Tuple
from collections import Counter
import re
import math


class KeywordExtractor:
    """Enhanced keyword extraction with TF-IDF and importance weighting."""

    # Skill importance weights (higher = more important)
    SKILL_WEIGHTS = {
        # High importance - technical and specialized skills
        "project management": 1.5,
        "program management": 1.5,
        "data analysis": 1.4,
        "monitoring": 1.3,
        "evaluation": 1.3,
        "strategic planning": 1.4,
        "budget management": 1.3,
        "procurement": 1.2,
        "python": 1.4,
        "sql": 1.4,
        "gis": 1.3,

        # Medium-high importance - UN-specific
        "humanitarian": 1.3,
        "peacekeeping": 1.3,
        "human rights": 1.3,
        "climate change": 1.3,
        "gender equality": 1.2,
        "sdgs": 1.3,
        "sustainable development": 1.3,

        # Medium importance - languages
        "english": 1.2,
        "french": 1.2,
        "spanish": 1.2,
        "arabic": 1.2,

        # Medium-low importance - soft skills
        "leadership": 1.1,
        "teamwork": 1.0,
        "communication": 1.0,
    }

    def __init__(self):
        self.idf_cache: Dict[str, float] = {}

    def extract_keywords_with_importance(
        self,
        text: str,
        max_keywords: int = 30
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords with importance scores.

        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return

        Returns:
            List of (keyword, importance_score) tuples
        """
        text_lower = text.lower()
        keywords = {}

        # 1. Extract multi-word phrases (bigrams and trigrams)
        bigrams = self._extract_ngrams(text_lower, n=2)
        trigrams = self._extract_ngrams(text_lower, n=3)

        # Add bigrams and trigrams with their frequencies
        for phrase, freq in bigrams.items():
            if self._is_valid_phrase(phrase):
                base_score = math.log(freq + 1)
                weight = self.SKILL_WEIGHTS.get(phrase, 1.0)
                keywords[phrase] = base_score * weight

        for phrase, freq in trigrams.items():
            if self._is_valid_phrase(phrase):
                base_score = math.log(freq + 1) * 1.2  # Slightly boost longer phrases
                weight = self.SKILL_WEIGHTS.get(phrase, 1.0)
                keywords[phrase] = base_score * weight

        # 2. Extract single important words
        important_terms = self._extract_important_terms(text_lower)
        for term, freq in important_terms.items():
            if term not in keywords and self._is_valid_term(term):
                base_score = math.log(freq + 1) * 0.8  # Slightly lower weight than phrases
                weight = self.SKILL_WEIGHTS.get(term, 1.0)
                keywords[term] = base_score * weight

        # 3. Extract technical skills patterns
        technical_skills = self._extract_technical_skills(text_lower)
        for skill in technical_skills:
            if skill not in keywords:
                keywords[skill] = keywords.get(skill, 0) + 1.5

        # 4. Extract experience requirements
        experience_keywords = self._extract_experience_requirements(text_lower)
        keywords.update(experience_keywords)

        # Sort by importance score and return top keywords
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:max_keywords]

    def _extract_ngrams(self, text: str, n: int) -> Dict[str, int]:
        """Extract n-grams from text."""
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s-]', ' ', text)
        words = text.split()

        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)

        return Counter(ngrams)

    def _extract_important_terms(self, text: str) -> Dict[str, int]:
        """Extract single important terms."""
        # Technical and domain-specific terms
        important_patterns = [
            r'\b(?:python|java|sql|r|excel|powerpoint|spss|stata)\b',
            r'\b(?:management|coordination|planning|analysis|evaluation)\b',
            r'\b(?:humanitarian|development|peacekeeping|advocacy)\b',
            r'\b(?:bachelor|master|phd|doctorate|degree)\b',
        ]

        terms = []
        for pattern in important_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)

        return Counter(terms)

    def _extract_technical_skills(self, text: str) -> Set[str]:
        """Extract technical skills using patterns."""
        skills = set()

        # Programming languages
        prog_langs = ['python', 'java', 'javascript', 'r', 'sql', 'c++', 'c#']
        for lang in prog_langs:
            if lang in text:
                skills.add(lang)

        # Tools and software
        tools = ['excel', 'powerpoint', 'word', 'sap', 'oracle', 'sharepoint',
                'tableau', 'power bi', 'spss', 'stata', 'arcgis', 'qgis']
        for tool in tools:
            if tool in text:
                skills.add(tool)

        # Methodologies
        methodologies = ['agile', 'scrum', 'waterfall', 'lean', 'six sigma']
        for method in methodologies:
            if method in text:
                skills.add(method)

        return skills

    def _extract_experience_requirements(self, text: str) -> Dict[str, float]:
        """Extract and score experience requirements."""
        keywords = {}

        patterns = [
            (r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', 1.3),
            (r'minimum\s+(\d+)\s*years?', 1.2),
            (r'at\s+least\s+(\d+)\s*years?', 1.2),
            (r'(\d+)\s*-\s*(\d+)\s*years?', 1.1),
        ]

        for pattern, weight in patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        years = match[0]
                    else:
                        years = match
                    keywords[f"{years} years experience"] = weight

        return keywords

    def _is_valid_phrase(self, phrase: str) -> bool:
        """Check if phrase is valid for extraction."""
        # Filter out common stop-word phrases
        stop_phrases = [
            'of the', 'in the', 'to the', 'for the', 'on the',
            'at the', 'by the', 'from the', 'with the', 'as the',
            'will be', 'has been', 'have been', 'should be', 'must be'
        ]

        if phrase in stop_phrases:
            return False

        # Must have at least one meaningful word
        words = phrase.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                     'are', 'were', 'be', 'been', 'being'}

        meaningful_words = [w for w in words if w not in stop_words]
        return len(meaningful_words) >= 1

    def _is_valid_term(self, term: str) -> bool:
        """Check if single term is valid."""
        if len(term) < 3 or len(term) > 30:
            return False

        # Must be alphabetic or contain hyphen
        if not re.match(r'^[a-z][\w-]*[a-z]$', term):
            return False

        # Filter common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get',
            'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
            'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let',
            'put', 'say', 'she', 'too', 'use'
        }

        return term not in stop_words


def fuzzy_match_score(s1: str, s2: str) -> float:
    """
    Calculate fuzzy match score between two strings.

    Uses Levenshtein distance-based similarity.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score between 0 and 1
    """
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()

    if s1 == s2:
        return 1.0

    # Check for substring match
    if s1 in s2 or s2 in s1:
        shorter = min(len(s1), len(s2))
        longer = max(len(s1), len(s2))
        return 0.8 + (shorter / longer) * 0.2

    # Levenshtein distance
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))

    if max_len == 0:
        return 1.0

    similarity = 1.0 - (distance / max_len)

    # Apply threshold
    return similarity if similarity >= 0.6 else 0.0


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def calculate_weighted_keyword_match(
    resume_text: str,
    resume_skills: List[str],
    job_keywords: List[Tuple[str, float]]
) -> Tuple[List[str], List[str], float]:
    """
    Calculate weighted keyword match with fuzzy matching.

    Args:
        resume_text: Resume text content
        resume_skills: List of resume skills
        job_keywords: List of (keyword, weight) tuples

    Returns:
        Tuple of (matching_keywords, missing_keywords, weighted_score)
    """
    resume_text_lower = resume_text.lower()
    resume_skills_lower = [s.lower() for s in resume_skills]

    matching_keywords = []
    missing_keywords = []
    total_weight = 0.0
    matched_weight = 0.0

    for keyword, weight in job_keywords:
        total_weight += weight
        keyword_lower = keyword.lower()

        # Exact match
        if (keyword_lower in resume_text_lower or
            keyword_lower in resume_skills_lower):
            matching_keywords.append(keyword)
            matched_weight += weight
            continue

        # Fuzzy match against resume skills
        best_match_score = 0.0
        for skill in resume_skills_lower:
            score = fuzzy_match_score(keyword_lower, skill)
            best_match_score = max(best_match_score, score)

        if best_match_score >= 0.8:
            matching_keywords.append(keyword)
            matched_weight += weight * best_match_score
        else:
            missing_keywords.append(keyword)

    # Calculate weighted score
    if total_weight > 0:
        weighted_score = matched_weight / total_weight
    else:
        weighted_score = 0.5

    return matching_keywords, missing_keywords, weighted_score
