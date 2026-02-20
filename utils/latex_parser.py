"""Utilities for parsing and manipulating LaTeX resume files."""

import re
from typing import List, Optional


def extract_summary_section(latex_content: str) -> Optional[List[str]]:
    """
    Extract summary bullets from LaTeX content.
    
    Args:
        latex_content: Full LaTeX document content
        
    Returns:
        List of bullet point strings (without \\item prefix), or None if not found
    """
    # Pattern to match the summary section
    pattern = r'%-+SUMMARY-+.*?\\section\{Summary\}.*?\\begin\{itemize\}(.*?)\\end\{itemize\}'
    
    match = re.search(pattern, latex_content, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    
    itemize_content = match.group(1)
    
    # Extract individual bullets
    bullet_pattern = r'\\item\s+(.*?)(?=\\item|$)'
    bullets = re.findall(bullet_pattern, itemize_content, re.DOTALL)
    
    # Clean up bullets (strip whitespace and newlines)
    cleaned_bullets = [bullet.strip().replace('\n', ' ') for bullet in bullets if bullet.strip()]
    
    return cleaned_bullets if cleaned_bullets else None


def replace_summary_section(latex_content: str, new_bullets: List[str]) -> str:
    """
    Replace the summary section with new bullets.
    
    Args:
        latex_content: Full LaTeX document content
        new_bullets: List of new bullet point strings (without \\item prefix)
        
    Returns:
        Updated LaTeX content with new summary section
    """
    # Pattern to match the entire summary itemize block
    pattern = r'(%-+SUMMARY-+.*?\\section\{Summary\}.*?\\begin\{itemize\}[^\n]*\n)(.*?)(\\end\{itemize\})'
    
    # Format new bullets - use raw string or double backslash
    formatted_bullets = '\n'.join([f'\\\\item {bullet}' for bullet in new_bullets])
    
    # Replace the content
    replacement = r'\1' + formatted_bullets + '\n' + r'\3'
    updated_content = re.sub(pattern, replacement, latex_content, flags=re.DOTALL | re.IGNORECASE)
    
    return updated_content


def extract_first_experience(latex_content: str) -> Optional[str]:
    """
    Extract the first experience/job section from LaTeX content.
    
    Args:
        latex_content: Full LaTeX document content
        
    Returns:
        Full LaTeX block for first experience, or None if not found
    """
    # Pattern to match first resumeSubheading after Professional Experience section
    pattern = r'\\section\{Professional Experience\}.*?\\resumeSubHeadingListStart\s*(\\resumeSubheading.*?\\resumeItemListEnd)'
    
    match = re.search(pattern, latex_content, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    
    return match.group(1).strip()


def replace_first_experience(latex_content: str, new_experience: str) -> str:
    """
    Replace the first experience section with new content.
    
    Args:
        latex_content: Full LaTeX document content
        new_experience: New LaTeX block for the experience section
        
    Returns:
        Updated LaTeX content with new first experience
    """
    # Pattern to match first resumeSubheading block
    pattern = r'(\\section\{Professional Experience\}.*?\\resumeSubHeadingListStart\s*)(\\resumeSubheading.*?\\resumeItemListEnd)'
    
    # Replace the content - use lambda to avoid backslash interpretation in replacement
    def replacement_func(match):
        return match.group(1) + new_experience
    
    updated_content = re.sub(pattern, replacement_func, latex_content, count=1, flags=re.DOTALL | re.IGNORECASE)
    
    return updated_content


def extract_skills_section(latex_content: str) -> Optional[str]:
    """
    Extract the skills section from LaTeX content.
    
    Args:
        latex_content: Full LaTeX document content
        
    Returns:
        Full skills section LaTeX block, or None if not found
    """
    # Pattern to match the skills section
    pattern = r'(\\section\{SKILLS\}.*?\\begin\{itemize\}.*?\\end\{itemize\})'
    
    match = re.search(pattern, latex_content, re.DOTALL | re.IGNORECASE)
    if not match:
        # Try alternate pattern with "Technical Skills"
        pattern = r'(\\section\{Technical Skills\}.*?\\begin\{itemize\}.*?\\end\{itemize\})'
        match = re.search(pattern, latex_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return None
    
    return match.group(1).strip()


def replace_skills_section(latex_content: str, new_skills: str) -> str:
    """
    Replace the skills section with new content.
    
    Args:
        latex_content: Full LaTeX document content
        new_skills: New LaTeX block for skills section
        
    Returns:
        Updated LaTeX content with new skills section
    """
    # Pattern to match the skills section
    pattern = r'\\section\{SKILLS\}.*?\\begin\{itemize\}.*?\\end\{itemize\}'
    
    # Try to find and replace - use lambda to avoid backslash interpretation
    if re.search(pattern, latex_content, re.DOTALL | re.IGNORECASE):
        updated_content = re.sub(pattern, lambda m: new_skills, latex_content, count=1, flags=re.DOTALL | re.IGNORECASE)
        return updated_content
    
    # Try alternate pattern
    pattern = r'\\section\{Technical Skills\}.*?\\begin\{itemize\}.*?\\end\{itemize\}'
    updated_content = re.sub(pattern, lambda m: new_skills, latex_content, count=1, flags=re.DOTALL | re.IGNORECASE)
    
    return updated_content


def escape_latex_special_chars(text: str) -> str:
    """
    Escape special LaTeX characters in text.
    
    Args:
        text: Plain text that may contain special characters
        
    Returns:
        Text with LaTeX special characters properly escaped
    """
    # Characters that need escaping in LaTeX
    special_chars = {
        '%': r'\%',
        '$': r'\$',
        '&': r'\&',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '#': r'\#',
        '^': r'\^{}',
        '~': r'\~{}',
    }
    
    result = text
    for char, escaped in special_chars.items():
        # Only escape if not already escaped
        result = re.sub(f'(?<!\\\\){re.escape(char)}', escaped, result)
    
    return result


def validate_latex_structure(latex_content: str) -> bool:
    """
    Basic validation to check if LaTeX content has required structure.
    
    Args:
        latex_content: LaTeX document content
        
    Returns:
        True if structure is valid, False otherwise
    """
    required_elements = [
        r'\\documentclass',
        r'\\begin\{document\}',
        r'\\end\{document\}',
    ]
    
    for element in required_elements:
        if not re.search(element, latex_content):
            return False
    
    return True
