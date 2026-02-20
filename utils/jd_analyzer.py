"""Job Description Analyzer - Extracts structured metadata from job descriptions."""

import json
import re
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from anthropic import Anthropic

from config.settings import settings


class JobDescriptionMetadata(BaseModel):
    """Structured metadata extracted from a job description."""
    
    company_names: List[str] = Field(
        default_factory=list,
        description="All company names mentioned in the job description"
    )
    role_level: str = Field(
        default="Mid",
        description="Role level: Junior, Mid, Senior, Staff, or Lead"
    )
    experience_years_min: Optional[int] = Field(
        default=None,
        description="Minimum years of experience required"
    )
    experience_years_max: Optional[int] = Field(
        default=None,
        description="Maximum years of experience mentioned or implied"
    )
    key_responsibilities: List[str] = Field(
        default_factory=list,
        description="Top 5 key responsibilities from the job description"
    )
    leadership_required: bool = Field(
        default=False,
        description="Whether the role explicitly requires leadership experience"
    )
    
    @field_validator('role_level')
    @classmethod
    def validate_role_level(cls, v: str) -> str:
        """Ensure role level is one of the expected values."""
        valid_levels = ["Junior", "Mid", "Senior", "Staff", "Lead"]
        if v not in valid_levels:
            # Try to map common variations
            v_lower = v.lower()
            if "junior" in v_lower or "entry" in v_lower or "i" == v_lower:
                return "Junior"
            elif "senior" in v_lower or "sr" in v_lower or "iii" in v_lower:
                return "Senior"
            elif "staff" in v_lower or "principal" in v_lower or "iv" in v_lower:
                return "Staff"
            elif "lead" in v_lower or "manager" in v_lower:
                return "Lead"
            else:
                return "Mid"  # Default to Mid for "II" or unclear
        return v
    
    def get_suggested_experience_years(self) -> str:
        """Get suggested experience years for resume summary."""
        if self.experience_years_min and self.experience_years_max:
            # Use the midpoint
            midpoint = (self.experience_years_min + self.experience_years_max) // 2
            return f"{midpoint}+"
        elif self.experience_years_min:
            return f"{self.experience_years_min}+"
        else:
            # Default based on role level
            defaults = {
                "Junior": "2+",
                "Mid": "4+",
                "Senior": "7+",
                "Staff": "10+",
                "Lead": "12+"
            }
            return defaults.get(self.role_level, "5+")
    
    def get_leadership_guidance(self) -> str:
        """Get guidance on leadership language usage."""
        if self.leadership_required or self.role_level in ["Staff", "Lead"]:
            return "Leadership language encouraged (led, managed, directed)"
        elif self.role_level == "Senior":
            return "Moderate leadership language acceptable (led small teams, mentored)"
        else:
            return "Use contributor language (collaborated, contributed, implemented, supported)"


class JDAnalyzer:
    """Analyzes job descriptions to extract structured metadata."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize JD analyzer.
        
        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.model = settings.claude_model
        self._cache: Dict[str, JobDescriptionMetadata] = {}
    
    def analyze(self, job_description: str, use_cache: bool = True) -> JobDescriptionMetadata:
        """
        Analyze a job description and extract structured metadata.
        
        Args:
            job_description: Full job description text
            use_cache: Whether to use cached results for identical JDs
            
        Returns:
            JobDescriptionMetadata with extracted information
            
        Raises:
            Exception: If API call fails or parsing fails
        """
        # Check cache
        cache_key = self._get_cache_key(job_description)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(job_description)
        
        try:
            # Call Claude with JSON mode
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for more consistent extraction
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            metadata_dict = self._parse_json_response(response_text)
            
            # Create Pydantic model
            metadata = JobDescriptionMetadata(**metadata_dict)
            
            # Cache result
            if use_cache:
                self._cache[cache_key] = metadata
            
            return metadata
            
        except Exception as e:
            # Return default metadata on failure
            return self._get_default_metadata(job_description)
    
    def _create_analysis_prompt(self, job_description: str) -> str:
        """Create the analysis prompt for Claude."""
        return f"""Analyze this job description and extract structured metadata. Return ONLY a valid JSON object with these exact fields:

{{
  "company_names": ["list", "of", "company", "names"],
  "role_level": "Junior|Mid|Senior|Staff|Lead",
  "experience_years_min": <number or null>,
  "experience_years_max": <number or null>,
  "key_responsibilities": ["top", "5", "responsibilities"],
  "leadership_required": true|false
}}

Guidelines:
1. company_names: Extract ALL company/organization names mentioned (e.g., "R1", "R37", "Google")
2. role_level: Determine from title and description:
   - "Engineer I", "Junior", "Entry-level" → "Junior"
   - "Engineer II", no modifier, "intermediate" → "Mid"
   - "Engineer III", "Senior" → "Senior"
   - "Staff", "Principal" → "Staff"
   - "Lead", "Manager" → "Lead"
3. experience_years_min/max: Extract from phrases like "3-5 years", "5+ years", "minimum 3 years"
4. key_responsibilities: Top 5 most important responsibilities (be concise)
5. leadership_required: true if explicitly requires "leading teams", "managing people", "directing others"
   - Do NOT mark true for "working with teams" or "collaborating"
   - Mark true only for actual people management or team leadership

Job Description:
{job_description}

Return ONLY the JSON object, no other text."""
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from Claude's response."""
        # Try to extract JSON if wrapped in markdown
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Remove any leading/trailing text
        response_text = response_text.strip()
        if not response_text.startswith('{'):
            # Find first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
    
    def _get_cache_key(self, job_description: str) -> str:
        """Generate cache key from job description."""
        # Use first 200 chars as key (enough to identify unique JDs)
        return job_description[:200].strip()
    
    def _get_default_metadata(self, job_description: str) -> JobDescriptionMetadata:
        """
        Return default metadata when analysis fails.
        Uses simple heuristics as fallback.
        """
        # Try to extract company names with simple regex
        company_names = []
        # Look for common patterns like "at Company" or "Company is"
        company_patterns = [
            r'(?:at|join|for)\s+([A-Z][A-Za-z0-9]+)',
            r'([A-Z][A-Za-z0-9]+)\s+(?:is|are|seeks)',
        ]
        for pattern in company_patterns:
            matches = re.findall(pattern, job_description)
            company_names.extend(matches)
        
        # Deduplicate and limit
        company_names = list(set(company_names))[:3]
        
        # Detect role level from title (prioritize numeric levels)
        jd_lower = job_description.lower()
        
        # Check for numeric levels first (more specific)
        if any(term in jd_lower for term in ['engineer ii', 'ii ', ' ii,', 'level ii', 'level 2']):
            role_level = "Mid"
        elif any(term in jd_lower for term in ['engineer iii', 'iii ', ' iii,', 'level iii', 'level 3']):
            role_level = "Senior"
        elif any(term in jd_lower for term in ['engineer i ', ' i ', ' i,', 'level i', 'level 1', 'junior', 'entry']):
            role_level = "Junior"
        elif any(term in jd_lower for term in ['engineer iv', 'iv ', ' iv,', 'staff', 'principal']):
            role_level = "Staff"
        elif any(term in jd_lower for term in ['lead', 'manager']):
            role_level = "Lead"
        # Then check for word-based levels
        elif any(term in jd_lower for term in ['senior', 'sr.']):
            role_level = "Senior"
        else:
            role_level = "Mid"
        
        # Extract experience years
        exp_match = re.search(r'(\d+)[\s-]+(?:to|-)?\s*(\d+)?\s*(?:\+)?\s*years?', jd_lower)
        exp_min = None
        exp_max = None
        if exp_match:
            exp_min = int(exp_match.group(1))
            if exp_match.group(2):
                exp_max = int(exp_match.group(2))
        
        # Detect leadership requirement
        leadership_required = any(term in jd_lower for term in [
            'lead team', 'manage team', 'direct report', 'people management'
        ])
        
        return JobDescriptionMetadata(
            company_names=company_names,
            role_level=role_level,
            experience_years_min=exp_min,
            experience_years_max=exp_max,
            key_responsibilities=[],
            leadership_required=leadership_required
        )
