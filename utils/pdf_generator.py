"""Utilities for compiling LaTeX to PDF."""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional


def compile_latex_to_pdf(latex_content: str, output_path: str) -> Tuple[bool, Optional[str]]:
    """
    Compile LaTeX content to PDF.
    
    Args:
        latex_content: Full LaTeX document content
        output_path: Path where the PDF should be saved
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Check if pdflatex is available
    if not is_pdflatex_available():
        return False, "pdflatex is not installed. Please install a LaTeX distribution (TeX Live, MiKTeX, etc.)"
    
    # Create temporary directory for compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        tex_file = temp_dir_path / "resume.tex"
        
        # Write LaTeX content to temporary file
        try:
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
        except Exception as e:
            return False, f"Failed to write LaTeX file: {str(e)}"
        
        # Compile with pdflatex
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(temp_dir_path), str(tex_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check if PDF was generated
            pdf_file = temp_dir_path / "resume.pdf"
            if not pdf_file.exists():
                # Parse error from log
                error_msg = parse_latex_error(result.stdout, result.stderr)
                return False, f"PDF compilation failed: {error_msg}"
            
            # Copy PDF to output location
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(pdf_file, output_path)
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "PDF compilation timed out (>30 seconds)"
        except Exception as e:
            return False, f"Compilation error: {str(e)}"


def is_pdflatex_available() -> bool:
    """
    Check if pdflatex is available in the system.
    
    Returns:
        True if pdflatex is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['pdflatex', '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def parse_latex_error(stdout: str, stderr: str) -> str:
    """
    Parse LaTeX compilation output to extract meaningful error messages.
    
    Args:
        stdout: Standard output from pdflatex
        stderr: Standard error from pdflatex
        
    Returns:
        User-friendly error message
    """
    # Look for common error patterns
    error_patterns = [
        r'! (.+)',  # LaTeX errors start with !
        r'Error: (.+)',
        r'Fatal error (.+)',
    ]
    
    combined_output = stdout + '\n' + stderr
    
    for pattern in error_patterns:
        matches = re.findall(pattern, combined_output)
        if matches:
            # Return first meaningful error
            return matches[0].strip()
    
    # If no specific error found, return generic message
    if 'Emergency stop' in combined_output:
        return "LaTeX encountered a critical error. Check your LaTeX syntax."
    
    return "Unknown compilation error. Check LaTeX syntax and packages."


# Import re for error parsing
import re
