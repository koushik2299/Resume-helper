"""Validation logic for skills section."""

import re
from dataclasses import dataclass
from typing import List

from utils.keyword_analyzer import count_keyword_matches


@dataclass
class SkillsValidationResult:
    """Result of skills validation checks."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    score: int  # 0-100
    keywords_matched: int


class SkillsValidator:
    """Validator for skills section."""
    
    def __init__(self):
        """Initialize validator."""
        self.min_skills = 8
        self.max_skills = 20
        self.min_keywords = 3
    
    def validate(self, skills_text: str, keywords: List[str]) -> SkillsValidationResult:
        """
        Validate skills section against requirements.
        
        Args:
            skills_text: Generated skills LaTeX block
            keywords: List of keywords to check for
            
        Returns:
            SkillsValidationResult with pass/fail status and details
        """
        errors = []
        warnings = []
        
        # Parse skills from text
        skills = self._parse_skills(skills_text)
        
        # Check 1: Skill count (8-20)
        if len(skills) < self.min_skills:
            warnings.append(f"Consider adding more skills (found {len(skills)}, recommended {self.min_skills}+)")
        elif len(skills) > self.max_skills:
            warnings.append(f"Consider reducing skills (found {len(skills)}, recommended max {self.max_skills})")
        
        # Check 2: Keyword integration
        full_text = ' '.join(skills)
        keywords_matched = count_keyword_matches(full_text, keywords)
        if keywords_matched < self.min_keywords:
            errors.append(f"Only {keywords_matched}/{len(keywords)} keywords found (need {self.min_keywords})")
        
        # Check 3: Proper categorization
        if not self._has_categories(skills_text):
            warnings.append("Consider organizing skills into categories (Languages, Frameworks, Tools, etc.)")
        
        # Check 4: LaTeX formatting
        if not self._check_latex_format(skills_text):
            errors.append("Invalid LaTeX format - must use \\item structure")
        
        # Check 5: Avoid duplicates
        duplicates = self._find_duplicates(skills)
        if duplicates:
            warnings.append(f"Duplicate skills found: {', '.join(duplicates)}")
        
        # Calculate score
        score = self._calculate_score(errors, warnings, keywords_matched, len(keywords), len(skills))
        
        # Overall pass/fail
        passed = len(errors) == 0
        
        return SkillsValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            score=score,
            keywords_matched=keywords_matched
        )
    
    def _parse_skills(self, skills_text: str) -> List[str]:
        """Extract individual skills from LaTeX format."""
        skills = []
        
        # Match \item patterns and extract content
        lines = skills_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('\\item'):
                # Remove \item prefix
                content = line[5:].strip()
                
                # Split by common delimiters (comma, semicolon, pipe)
                parts = re.split(r'[,;|]', content)
                for part in parts:
                    skill = part.strip()
                    # Remove any LaTeX formatting
                    skill = re.sub(r'\\textbf\{(.*?)\}', r'\1', skill)
                    skill = re.sub(r'\\textit\{(.*?)\}', r'\1', skill)
                    if skill and skill != ':':
                        skills.append(skill)
        
        return skills
    
    def _has_categories(self, text: str) -> bool:
        """Check if skills are organized into categories."""
        # Look for common category indicators
        category_patterns = [
            r'\\textbf\{.*?:',  # Bold category names with colon
            r'Languages:',
            r'Frameworks:',
            r'Tools:',
            r'Technologies:',
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in category_patterns)
    
    def _check_latex_format(self, text: str) -> bool:
        """Check if skills use proper LaTeX structure."""
        # Should contain \item and be within itemize environment
        has_items = '\\item' in text
        has_section = '\\section' in text or '\\begin{itemize}' in text
        return has_items and has_section
    
    def _find_duplicates(self, skills: List[str]) -> List[str]:
        """Find duplicate skills (case-insensitive)."""
        seen = set()
        duplicates = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in seen:
                duplicates.append(skill)
            else:
                seen.add(skill_lower)
        
        return duplicates
    
    def _calculate_score(
        self, 
        errors: List[str], 
        warnings: List[str],
        keywords_matched: int,
        total_keywords: int,
        skill_count: int
    ) -> int:
        """Calculate overall validation score (0-100)."""
        score = 100
        
        # Deduct for errors (major issues)
        score -= len(errors) * 15
        
        # Deduct for warnings (minor issues)
        score -= len(warnings) * 5
        
        # Bonus for keyword matching
        keyword_ratio = keywords_matched / max(total_keywords, 1)
        score += int(keyword_ratio * 20)
        
        # Bonus for good skill count (12-15 is ideal)
        if 12 <= skill_count <= 15:
            score += 5
        
        # Clamp to 0-100
        return max(0, min(100, score))
