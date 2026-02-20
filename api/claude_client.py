"""Claude API client for resume generation."""

import re
from typing import List, Optional, Dict
from anthropic import Anthropic
from pathlib import Path

from config.settings import settings
from utils.jd_analyzer import JDAnalyzer, JobDescriptionMetadata


class ClaudeClient:
    """Client for interacting with Claude API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.jd_analyzer = JDAnalyzer(api_key=self.api_key)
    
    def analyze_job_description(self, job_description: str) -> JobDescriptionMetadata:
        """
        Analyze job description to extract structured metadata.
        
        Args:
            job_description: Full job description text
            
        Returns:
            JobDescriptionMetadata with extracted information
        """
        return self.jd_analyzer.analyze(job_description)
    
    def generate_summary(
        self, 
        old_summary: str, 
        job_description: str, 
        keywords: List[str],
        jd_metadata: Optional[JobDescriptionMetadata] = None
    ) -> str:
        """
        Generate a tailored summary section using Claude.
        
        Args:
            old_summary: Current summary bullets (as plain text)
            job_description: Full job description
            keywords: List of top keywords to include
            jd_metadata: Optional job description metadata for enhanced validation
            
        Returns:
            Generated summary bullets as LaTeX \\item lines
            
        Raises:
            Exception: If API call fails
        """
        # Prepare metadata for prompt
        if jd_metadata:
            company_names_str = ", ".join(jd_metadata.company_names) if jd_metadata.company_names else "None detected"
            experience_range = jd_metadata.get_suggested_experience_years()
            leadership_guidance = jd_metadata.get_leadership_guidance()
        else:
            company_names_str = "Not analyzed"
            experience_range = "5+"
            leadership_guidance = "Use contributor language by default"
        
        prompt = self._load_and_format_prompt(
            prompt_name="summary_prompt.md",
            old_summary=old_summary,
            job_description=job_description,
            keywords=', '.join(keywords),
            company_names=company_names_str,
            role_level=jd_metadata.role_level if jd_metadata else "Mid",
            experience_range=experience_range,
            leadership_guidance=leadership_guidance
        )
        
        return self._call_claude(prompt)
    
    def generate_experience(
        self,
        old_experience: str,
        job_description: str,
        keywords: List[str]
    ) -> str:
        """
        Generate a tailored experience section using Claude.
        
        Args:
            old_experience: Current experience section (full LaTeX block)
            job_description: Full job description
            keywords: List of top keywords to include
            
        Returns:
            Generated experience section as LaTeX block
            
        Raises:
            Exception: If API call fails
        """
        prompt = self._load_and_format_prompt(
            prompt_name="projects_prompt.md",
            old_experience=old_experience,
            job_description=job_description,
            keywords=', '.join(keywords)
        )
        
        return self._call_claude(prompt)
    
    def generate_skills(
        self,
        old_skills: str,
        job_description: str,
        keywords: List[str]
    ) -> str:
        """
        Generate a tailored skills section using Claude.
        
        Args:
            old_skills: Current skills section (full LaTeX block)
            job_description: Full job description
            keywords: List of top keywords to include
            
        Returns:
            Generated skills section as LaTeX block
            
        Raises:
            Exception: If API call fails
        """
        prompt = self._load_and_format_prompt(
            prompt_name="skills_prompt.md",
            old_skills=old_skills,
            job_description=job_description,
            keywords=', '.join(keywords)
        )
        
        return self._call_claude(prompt)
    
    def _call_claude(self, prompt: str) -> str:
        """
        Make API call to Claude.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Claude's response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return self._clean_response(response_text)
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def _load_and_format_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load prompt template and format with provided variables.
        
        Args:
            prompt_name: Name of the prompt file
            **kwargs: Variables to substitute in template
            
        Returns:
            Formatted prompt string
        """
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_name
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Format with variables
        formatted_prompt = template.format(**kwargs)
        
        return formatted_prompt
    
    def _clean_response(self, response: str) -> str:
        """
        Clean Claude's response to extract relevant LaTeX code.
        
        Args:
            response: Raw response from Claude
            
        Returns:
            Cleaned response
        """
        # Remove markdown code blocks if present
        response = re.sub(r'```(?:latex)?\n?(.*?)\n?```', r'\1', response, flags=re.DOTALL)
        
        # Remove any leading/trailing explanations
        lines = response.strip().split('\n')
        latex_lines = []
        in_latex = False
        
        for line in lines:
            # Start collecting when we see LaTeX commands
            if '\\item' in line or '\\section' in line or '\\begin' in line or '\\resumeSubheading' in line:
                in_latex = True
            
            if in_latex:
                latex_lines.append(line)
        
        # If we found LaTeX content, return it; otherwise return original
        if latex_lines:
            return '\n'.join(latex_lines).strip()
        
        return response.strip()
