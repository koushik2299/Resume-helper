"""Validation logic for summary section."""

import re
from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from config.settings import settings
from utils.keyword_analyzer import count_keyword_matches


class SummaryValidationContext(BaseModel):
    """Context for semantic validation of summary bullets."""
    
    company_names: List[str] = Field(
        default_factory=list,
        description="Company names to block from appearing in summary"
    )
    role_level: str = Field(
        default="Mid",
        description="Role level: Junior, Mid, Senior, Staff, or Lead"
    )
    max_experience_years: Optional[int] = Field(
        default=None,
        description="Maximum experience years appropriate for this role"
    )
    leadership_allowed: bool = Field(
        default=False,
        description="Whether leadership language is appropriate for this role"
    )


class SummaryBullet(BaseModel):
    """Pydantic model for a single summary bullet with semantic validation."""
    
    content: str = Field(description="The bullet content without \\item prefix")
    context: Optional[SummaryValidationContext] = Field(
        default=None,
        description="Validation context from job description analysis"
    )
    
    @model_validator(mode='after')
    def check_all_constraints(self) -> 'SummaryBullet':
        """Run all semantic validations on the bullet content."""
        if not self.context:
            return self
        
        content_lower = self.content.lower()
        
        # Check 1: Block company names
        for company_name in self.context.company_names:
            patterns = [
                rf'\b{re.escape(company_name.lower())}\b',  # Exact word
                rf'for\s+{re.escape(company_name.lower())}\b',  # "for Company"
                rf'at\s+{re.escape(company_name.lower())}\b',  # "at Company"
            ]
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    raise ValueError(
                        f"Company name '{company_name}' found in bullet. "
                        f"Never mention the target company as if you work there."
                    )
        
        # Check 2: Leadership language for non-leadership roles
        if not self.context.leadership_allowed:
            leadership_verbs = [
                r'\bled\b', r'\bleading\b', r'\blead\b',
                r'\bmanaged\b', r'\bmanaging\b', r'\bmanage\b',
                r'\bdirected\b', r'\bdirecting\b', r'\bdirect\b',
                r'\boversaw\b', r'\boverseeing\b', r'\boversee\b',
                r'\bsupervised\b', r'\bsupervising\b', r'\bsupervise\b',
            ]
            
            for verb_pattern in leadership_verbs:
                match = re.search(verb_pattern, content_lower)
                if match:
                    verb = match.group()
                    raise ValueError(
                        f"Leadership verb '{verb}' inappropriate for {self.context.role_level}-level role. "
                        f"Use contributor language: collaborated, contributed, implemented, supported."
                    )
        
        # Check 3: Experience level
        if self.context.max_experience_years is not None:
            years_match = re.search(r'(\d+)\+?\s*(?:yrs?|years?)', content_lower)
            if years_match:
                years = int(years_match.group(1))
                if years > self.context.max_experience_years:
                    raise ValueError(
                        f"Experience level '{years}+ yrs' exceeds maximum {self.context.max_experience_years} "
                        f"for {self.context.role_level}-level role. Adjust to match job requirements."
                    )
        
        return self


@dataclass
class ValidationResult:
    """Result of validation checks."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    score: int  # 0-100
    keywords_matched: int


class SummaryValidator:
    """Validator for summary section bullets."""
    
    def __init__(self):
        """Initialize validator with settings."""
        self.char_min = settings.summary_char_min
        self.char_max = settings.summary_char_max
        self.bullet_count = settings.summary_bullet_count
        self.min_keywords = settings.min_keywords_required
    
    def validate(
        self, 
        bullets_text: str, 
        keywords: List[str],
        context: Optional[SummaryValidationContext] = None
    ) -> ValidationResult:
        """
        Validate summary bullets against all requirements.
        
        Args:
            bullets_text: Generated bullets as string (with \\item prefix)
            keywords: List of keywords to check for
            context: Optional validation context from job description analysis
            
        Returns:
            ValidationResult with pass/fail status and details
        """
        errors = []
        warnings = []
        
        # Parse bullets
        bullets = self._parse_bullets(bullets_text)
        
        # Run Pydantic semantic validation on each bullet if context provided
        if context:
            from pydantic import ValidationError
            for i, bullet in enumerate(bullets, 1):
                try:
                    SummaryBullet(content=bullet, context=context)
                except ValidationError as e:
                    # Extract error messages from Pydantic validation
                    for error in e.errors():
                        error_msg = error.get('msg', str(error))
                        # Clean up the message
                        if error_msg.startswith('Value error, '):
                            error_msg = error_msg[13:]  # Remove "Value error, " prefix
                        errors.append(f"Bullet {i}: {error_msg}")
                except Exception as e:
                    # Catch any other exceptions
                    errors.append(f"Bullet {i}: Validation error - {str(e)}")
        
        # Check 1: Exactly 4 bullets
        if len(bullets) != self.bullet_count:
            errors.append(f"Must have exactly {self.bullet_count} bullets (found {len(bullets)})")
        
        # Check each bullet
        for i, bullet in enumerate(bullets, 1):
            # Check 2: Character count (105-109)
            char_count = len(bullet)
            if char_count < self.char_min or char_count > self.char_max:
                errors.append(f"Bullet {i}: {char_count} chars (must be {self.char_min}-{self.char_max})")
            
            # Check 3: First bullet format
            if i == 1:
                if not self._check_first_bullet_format(bullet):
                    errors.append(f"Bullet 1 must start with '[Role] with X+ yrs'")
            
            # Check 4: No trailing periods
            if bullet.rstrip().endswith('.'):
                errors.append(f"Bullet {i}: Remove trailing period")
            
            # Check 5: Measurable impact (contains numbers)
            if not self._contains_numbers(bullet):
                warnings.append(f"Bullet {i}: Consider adding measurable impact (numbers/percentages)")
        
        # Check 6: Keyword integration
        full_text = ' '.join(bullets)
        keywords_matched = count_keyword_matches(full_text, keywords)
        if keywords_matched < self.min_keywords:
            errors.append(f"Only {keywords_matched}/{len(keywords)} keywords found (need {self.min_keywords})")
        
        # Check 7: LaTeX special characters
        if not self._check_latex_escaping(bullets_text):
            warnings.append("Some special characters may not be properly escaped")
        
        # Calculate score
        score = self._calculate_score(errors, warnings, keywords_matched, len(keywords))
        
        # Overall pass/fail
        passed = len(errors) == 0
        
        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            score=score,
            keywords_matched=keywords_matched
        )
    
    def _parse_bullets(self, bullets_text: str) -> List[str]:
        """Extract bullet content from LaTeX format."""
        lines = bullets_text.strip().split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('\\item'):
                # Remove \item prefix and get content
                content = line[5:].strip()
                bullets.append(content)
        
        return bullets
    
    def _check_first_bullet_format(self, bullet: str) -> bool:
        """Check if first bullet follows '[Role] with X+ yrs' format."""
        # Pattern: starts with words, then "with", then number+, then "yrs" or "years"
        pattern = r'^[A-Za-z\s]+\s+with\s+\d+\+?\s+(yrs?|years)'
        return bool(re.search(pattern, bullet, re.IGNORECASE))
    
    def _contains_numbers(self, text: str) -> bool:
        """Check if text contains numbers (for measurable impact)."""
        return bool(re.search(r'\d+', text))
    
    def _check_latex_escaping(self, text: str) -> bool:
        """Check if special characters are properly escaped."""
        # Look for unescaped special characters
        unescaped_pattern = r'(?<!\\)[%$&#_{}^~]'
        return not bool(re.search(unescaped_pattern, text))
    
    def _calculate_score(
        self, 
        errors: List[str], 
        warnings: List[str],
        keywords_matched: int,
        total_keywords: int
    ) -> int:
        """Calculate overall validation score (0-100)."""
        score = 100
        
        # Count semantic vs format errors
        semantic_errors = sum(1 for e in errors if any(
            term in e.lower() for term in ['company name', 'leadership', 'experience level']
        ))
        format_errors = len(errors) - semantic_errors
        
        # Deduct more heavily for semantic violations (critical ATS issues)
        score -= semantic_errors * 20
        
        # Deduct for format errors (still important)
        score -= format_errors * 15
        
        # Deduct for warnings (minor issues)
        score -= len(warnings) * 5
        
        # Bonus for keyword matching
        keyword_ratio = keywords_matched / max(total_keywords, 1)
        score += int(keyword_ratio * 10)
        
        # Clamp to 0-100
        return max(0, min(100, score))
