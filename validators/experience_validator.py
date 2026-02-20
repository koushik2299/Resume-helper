"""Validation logic for experience section."""

import re
from dataclasses import dataclass
from typing import List

from utils.keyword_analyzer import count_keyword_matches


@dataclass
class ExperienceValidationResult:
    """Result of experience validation checks."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    score: int  # 0-100
    keywords_matched: int


class ExperienceValidator:
    """Validator for experience section."""
    
    def __init__(self):
        """Initialize validator."""
        self.min_bullets = 4
        self.max_bullets = 6
        self.min_keywords = 3
        
        # Strong action verbs for resume bullets
        self.action_verbs = {
            'led', 'developed', 'implemented', 'designed', 'built', 'created',
            'managed', 'delivered', 'launched', 'optimized', 'improved', 'reduced',
            'increased', 'achieved', 'established', 'drove', 'spearheaded', 'facilitated',
            'deployed', 'architected', 'engineered', 'collaborated', 'coordinated'
        }
    
    def validate(self, experience_text: str, keywords: List[str]) -> ExperienceValidationResult:
        """
        Validate experience section against requirements.
        
        Args:
            experience_text: Generated experience LaTeX block
            keywords: List of keywords to check for
            
        Returns:
            ExperienceValidationResult with pass/fail status and details
        """
        errors = []
        warnings = []
        
        # Parse bullets from experience
        bullets = self._parse_bullets(experience_text)
        
        # Check 1: Bullet count (4-6)
        if len(bullets) < self.min_bullets:
            errors.append(f"Need at least {self.min_bullets} bullets (found {len(bullets)})")
        elif len(bullets) > self.max_bullets:
            warnings.append(f"Consider reducing to {self.max_bullets} bullets (found {len(bullets)})")
        
        # Check each bullet
        for i, bullet in enumerate(bullets, 1):
            # Check 2: Starts with action verb
            if not self._starts_with_action_verb(bullet):
                warnings.append(f"Bullet {i}: Consider starting with strong action verb")
            
            # Check 3: Contains quantifiable metrics
            if not self._contains_metrics(bullet):
                warnings.append(f"Bullet {i}: Add quantifiable metrics (%, numbers, scale)")
            
            # Check 4: No trailing periods
            if bullet.rstrip().endswith('.'):
                errors.append(f"Bullet {i}: Remove trailing period")
        
        # Check 5: Keyword integration
        full_text = ' '.join(bullets)
        keywords_matched = count_keyword_matches(full_text, keywords)
        if keywords_matched < self.min_keywords:
            errors.append(f"Only {keywords_matched}/{len(keywords)} keywords found (need {self.min_keywords})")
        
        # Check 6: LaTeX formatting
        if not self._check_latex_format(experience_text):
            errors.append("Invalid LaTeX format - must use \\resumeItem structure")
        
        # Calculate score
        score = self._calculate_score(errors, warnings, keywords_matched, len(keywords), len(bullets))
        
        # Overall pass/fail
        passed = len(errors) == 0
        
        return ExperienceValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            score=score,
            keywords_matched=keywords_matched
        )
    
    def _parse_bullets(self, experience_text: str) -> List[str]:
        """Extract bullet content from LaTeX format."""
        bullets = []
        
        # Match \resumeItem{...} patterns
        pattern = r'\\resumeItem\{(.*?)\}'
        matches = re.findall(pattern, experience_text, re.DOTALL)
        
        for match in matches:
            # Clean up the content
            content = match.strip()
            # Remove any nested LaTeX commands but keep the text
            content = re.sub(r'\\textit\{(.*?)\}', r'\1', content)
            content = re.sub(r'\\textbf\{(.*?)\}', r'\1', content)
            content = re.sub(r'\\textcolor\{.*?\}\{(.*?)\}', r'\1', content)
            bullets.append(content)
        
        return bullets
    
    def _starts_with_action_verb(self, bullet: str) -> bool:
        """Check if bullet starts with a strong action verb."""
        first_word = bullet.split()[0].lower() if bullet.split() else ""
        return first_word in self.action_verbs
    
    def _contains_metrics(self, text: str) -> bool:
        """Check if text contains quantifiable metrics."""
        # Look for numbers, percentages, or scale indicators
        patterns = [
            r'\d+%',  # Percentages
            r'\d+\+',  # Numbers with +
            r'\d+[KMB]',  # K, M, B suffixes
            r'\$\d+',  # Dollar amounts
            r'\d+x',  # Multipliers
            r'\d+',  # Any number
        ]
        return any(re.search(pattern, text) for pattern in patterns)
    
    def _check_latex_format(self, text: str) -> bool:
        """Check if experience uses proper LaTeX structure."""
        # Should contain \resumeSubheading and \resumeItem
        has_subheading = '\\resumeSubheading' in text
        has_items = '\\resumeItem' in text
        return has_subheading and has_items
    
    def _calculate_score(
        self, 
        errors: List[str], 
        warnings: List[str],
        keywords_matched: int,
        total_keywords: int,
        bullet_count: int
    ) -> int:
        """Calculate overall validation score (0-100)."""
        score = 100
        
        # Deduct for errors (major issues)
        score -= len(errors) * 15
        
        # Deduct for warnings (minor issues)
        score -= len(warnings) * 5
        
        # Bonus for keyword matching
        keyword_ratio = keywords_matched / max(total_keywords, 1)
        score += int(keyword_ratio * 15)
        
        # Bonus for optimal bullet count (5 bullets is ideal)
        if bullet_count == 5:
            score += 5
        
        # Clamp to 0-100
        return max(0, min(100, score))
