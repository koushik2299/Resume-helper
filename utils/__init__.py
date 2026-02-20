"""Utility functions for resume processing."""

from .latex_parser import (
    extract_summary_section,
    replace_summary_section,
    extract_first_experience,
    replace_first_experience,
    extract_skills_section,
    replace_skills_section,
    escape_latex_special_chars,
    validate_latex_structure,
)
from .keyword_analyzer import extract_keywords, count_keyword_matches
from .pdf_generator import compile_latex_to_pdf, is_pdflatex_available

__all__ = [
    "extract_summary_section",
    "replace_summary_section",
    "extract_first_experience",
    "replace_first_experience",
    "extract_skills_section",
    "replace_skills_section",
    "escape_latex_special_chars",
    "validate_latex_structure",
    "extract_keywords",
    "count_keyword_matches",
    "compile_latex_to_pdf",
    "is_pdflatex_available",
]
