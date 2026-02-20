"""Main Streamlit application for Resume Builder - Three Section Generation."""

import streamlit as st
from pathlib import Path
import tempfile
from datetime import datetime
import re

from api.claude_client import ClaudeClient
from validators.summary_validator import SummaryValidator
from validators.experience_validator import ExperienceValidator
from validators.skills_validator import SkillsValidator
from utils.latex_parser import (
    extract_summary_section, replace_summary_section,
    extract_first_experience, replace_first_experience,
    extract_skills_section, replace_skills_section
)
from utils.keyword_analyzer import extract_keywords, get_matched_keywords
from utils.pdf_generator import compile_latex_to_pdf, is_pdflatex_available


# Page configuration
st.set_page_config(
    page_title="ResumeForge - AI Resume Builder",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'latex_content' not in st.session_state:
    st.session_state.latex_content = None
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'keywords' not in st.session_state:
    st.session_state.keywords = []

# Section-specific state
if 'old_summary' not in st.session_state:
    st.session_state.old_summary = None
if 'old_experience' not in st.session_state:
    st.session_state.old_experience = None
if 'old_skills' not in st.session_state:
    st.session_state.old_skills = None

if 'generated_summary' not in st.session_state:
    st.session_state.generated_summary = None
if 'generated_experience' not in st.session_state:
    st.session_state.generated_experience = None
if 'generated_skills' not in st.session_state:
    st.session_state.generated_skills = None

if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None
if 'experience_validation_result' not in st.session_state:
    st.session_state.experience_validation_result = None
if 'skills_validation_result' not in st.session_state:
    st.session_state.skills_validation_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'updated_latex' not in st.session_state:
    st.session_state.updated_latex = None
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = None
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'jd_metadata' not in st.session_state:
    st.session_state.jd_metadata = None


def main():
    """Main application function."""
    
    # Header
    st.title("📝 ResumeForge - AI Resume Builder")
    st.markdown("### Phase 1 MVP: Three-Section Generator")
    st.markdown("*Tailors your Summary, First Experience, and Skills sections*")
    st.markdown("---")
    
    # Check LaTeX installation
    if not is_pdflatex_available():
        st.warning("⚠️ **pdflatex not found!** PDF compilation will fail. Install LaTeX or download .tex files instead.")
        with st.expander("📦 Installation Instructions"):
            st.code("brew install --cask mactex  # macOS")
    
    # Job Board Section
    display_job_board()
    
    st.markdown("---")
    # Step 1: Load Resume
    st.header("Step 1: Load Your Resume")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Primary button - Load Koushik's resume
        if st.button("📄 Load Koushik Health AI Resume", type="primary", use_container_width=True):
            template_path = Path("templates/sample_resume.tex")
            if template_path.exists():
                st.session_state.latex_content = template_path.read_text(encoding='utf-8')
                extract_all_sections()
                st.success("✅ Koushik Health AI Resume loaded!")
                st.rerun()
            else:
                st.error("❌ Template file not found!")
        
        st.markdown("---")
        
        # Alternative: Paste LaTeX code
        with st.expander("📋 Or paste your LaTeX resume code here"):
            latex_input = st.text_area(
                "Paste LaTeX Resume Code",
                height=300,
                placeholder="Paste your complete LaTeX resume code here...",
                help="Paste the entire .tex file content including \\documentclass, \\begin{document}, etc.",
                label_visibility="collapsed"
            )
            
            if st.button("Load from Pasted Code"):
                if latex_input.strip():
                    st.session_state.latex_content = latex_input
                    extract_all_sections()
                    st.success("✅ Resume loaded from pasted code!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please paste LaTeX code first")
    
    with col2:
        if st.session_state.latex_content:
            st.success("✅ **Resume Loaded**")
            display_extracted_sections()
        else:
            st.info("👈 Click the button to load your resume")
    
    st.markdown("---")
    
    # Step 2: Job Description
    st.header("Step 2: Paste Job Description")
    
    job_desc = st.text_area(
        "Job Description",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste the full job description here...",
        help="Paste the complete job posting including requirements and responsibilities"
    )
    
    if job_desc != st.session_state.job_description:
        st.session_state.job_description = job_desc
        if job_desc:
            st.session_state.keywords = extract_keywords(job_desc, top_n=8)
    
    if st.session_state.keywords:
        with st.expander("🔑 Top Keywords Extracted"):
            st.write(", ".join(st.session_state.keywords))
    
    # Display JD analysis if available
    if st.session_state.jd_metadata:
        with st.expander("📋 Job Analysis", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Company Names:**")
                if st.session_state.jd_metadata.company_names:
                    st.info(", ".join(st.session_state.jd_metadata.company_names))
                else:
                    st.caption("None detected")
                
                st.markdown("**Role Level:**")
                st.info(st.session_state.jd_metadata.role_level)
            
            with col2:
                st.markdown("**Experience Range:**")
                exp_str = f"{st.session_state.jd_metadata.experience_years_min}-{st.session_state.jd_metadata.experience_years_max} years" if st.session_state.jd_metadata.experience_years_min and st.session_state.jd_metadata.experience_years_max else st.session_state.jd_metadata.get_suggested_experience_years()
                st.info(exp_str)
                
                st.markdown("**Leadership Required:**")
                st.info("Yes" if st.session_state.jd_metadata.leadership_required else "No")
    
    st.markdown("---")
    
    # Step 3: Generate All Sections
    st.header("Step 3: Generate Tailored Sections")
    
    can_generate = (
        st.session_state.latex_content is not None 
        and st.session_state.job_description.strip() != ""
        and st.session_state.old_summary is not None
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🚀 Generate All Sections", disabled=not can_generate, type="primary"):
            generate_all_sections()
    
    with col2:
        if st.session_state.generated_summary:
            if st.button("🔄 Regenerate All"):
                generate_all_sections()
    
    if not can_generate:
        st.info("👆 Please upload a resume and paste a job description to continue.")
    
    st.markdown("---")
    
    # Results Section
    if st.session_state.generated_summary:
        display_results()


def extract_all_sections():
    """Extract all three sections from uploaded resume."""
    if not st.session_state.latex_content:
        return
    
    # Extract Summary
    summary_bullets = extract_summary_section(st.session_state.latex_content)
    st.session_state.old_summary = summary_bullets
    
    # Extract First Experience
    experience_block = extract_first_experience(st.session_state.latex_content)
    st.session_state.old_experience = experience_block
    
    # Extract Skills
    skills_block = extract_skills_section(st.session_state.latex_content)
    st.session_state.old_skills = skills_block


def display_extracted_sections():
    """Display what was extracted from the resume."""
    with st.expander("📄 Extracted Sections"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Summary**")
            if st.session_state.old_summary:
                st.success(f"✅ {len(st.session_state.old_summary)} bullets found")
            else:
                st.error("❌ Not found")
        
        with col2:
            st.markdown("**First Experience**")
            if st.session_state.old_experience:
                st.success("✅ Found")
            else:
                st.error("❌ Not found")
        
        with col3:
            st.markdown("**Skills**")
            if st.session_state.old_skills:
                st.success("✅ Found")
            else:
                st.error("❌ Not found")


def generate_all_sections():
    """Generate all three sections using Claude API."""
    
    with st.spinner("🤖 Generating tailored sections with Claude..."):
        try:
            client = ClaudeClient()
            
            # Step 1: Analyze job description for metadata
            st.info("Analyzing job description...")
            st.session_state.jd_metadata = client.analyze_job_description(
                st.session_state.job_description
            )
            
            # Create validation context from metadata
            from validators.summary_validator import SummaryValidationContext
            validation_context = SummaryValidationContext(
                company_names=st.session_state.jd_metadata.company_names,
                role_level=st.session_state.jd_metadata.role_level,
                max_experience_years=st.session_state.jd_metadata.experience_years_max,
                leadership_allowed=st.session_state.jd_metadata.leadership_required
            )
            
            # Step 2: Generate Summary with metadata
            st.info("Generating Summary section...")
            old_summary_text = '\\n'.join(st.session_state.old_summary)
            st.session_state.generated_summary = client.generate_summary(
                old_summary=old_summary_text,
                job_description=st.session_state.job_description,
                keywords=st.session_state.keywords,
                jd_metadata=st.session_state.jd_metadata
            )
            
            # Step 3: Generate Experience (if available)
            if st.session_state.old_experience:
                st.info("Generating First Experience section...")
                st.session_state.generated_experience = client.generate_experience(
                    old_experience=st.session_state.old_experience,
                    job_description=st.session_state.job_description,
                    keywords=st.session_state.keywords
                )
            
            # Step 4: Generate Skills (if available)
            if st.session_state.old_skills:
                st.info("Generating Skills section...")
                st.session_state.generated_skills = client.generate_skills(
                    old_skills=st.session_state.old_skills,
                    job_description=st.session_state.job_description,
                    keywords=st.session_state.keywords
                )
            
            # Step 5: Validate all three sections (with context for summary)
            summary_validator = SummaryValidator()
            st.session_state.validation_result = summary_validator.validate(
                st.session_state.generated_summary,
                st.session_state.keywords,
                context=validation_context
            )
            
            if st.session_state.generated_experience:
                experience_validator = ExperienceValidator()
                st.session_state.experience_validation_result = experience_validator.validate(
                    st.session_state.generated_experience,
                    st.session_state.keywords
                )
            
            if st.session_state.generated_skills:
                skills_validator = SkillsValidator()
                st.session_state.skills_validation_result = skills_validator.validate(
                    st.session_state.generated_skills,
                    st.session_state.keywords
                )
            
            st.success("✅ All sections generated and validated successfully!")
            
        except Exception as e:
            import traceback
            st.error(f"❌ Error generating sections: {type(e).__name__}: {str(e)}")
            with st.expander("🔍 Full Error Details (for debugging)"):
                st.code(traceback.format_exc())
            st.info("Please check your API key in the .env file and try again.")


def display_results():
    """Display generation results with LaTeX editor and chat interface."""
    
    st.header("📊 Generated Resume")
    
    # Calculate scores for all sections
    summary_val = st.session_state.validation_result
    exp_val = st.session_state.experience_validation_result
    skills_val = st.session_state.skills_validation_result
    
    # Check if validation exists before accessing score
    if not summary_val:
        st.error("❌ Validation failed. Please regenerate the sections.")
        return
    
    scores = [summary_val.score]
    if exp_val:
        scores.append(exp_val.score)
    if skills_val:
        scores.append(skills_val.score)
    overall_score = sum(scores) / len(scores)
    
    # Helper function for score color
    def get_score_color(score):
        if score >= 80:
            return "🟢"
        elif score >= 60:
            return "🟡"
        else:
            return "🔴"
    
    # Display scores in a grid
    st.subheader("📈 Validation Scores")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall",
            f"{get_score_color(overall_score)} {int(overall_score)}/100",
            delta=None
        )
    
    with col2:
        st.metric(
            "Summary",
            f"{get_score_color(summary_val.score)} {summary_val.score}/100",
            delta=f"{summary_val.keywords_matched}/{len(st.session_state.keywords)} keywords"
        )
    
    with col3:
        if exp_val:
            st.metric(
                "Experience",
                f"{get_score_color(exp_val.score)} {exp_val.score}/100",
                delta=f"{exp_val.keywords_matched}/{len(st.session_state.keywords)} keywords"
            )
        else:
            st.metric("Experience", "N/A")
    
    with col4:
        if skills_val:
            st.metric(
                "Skills",
                f"{get_score_color(skills_val.score)} {skills_val.score}/100",
                delta=f"{skills_val.keywords_matched}/{len(st.session_state.keywords)} keywords"
            )
        else:
            st.metric("Skills", "N/A")
    
    # Show all errors and warnings in one expander
    all_errors = []
    all_warnings = []
    
    if summary_val.errors:
        all_errors.extend([f"[Summary] {e}" for e in summary_val.errors])
    if summary_val.warnings:
        all_warnings.extend([f"[Summary] {w}" for w in summary_val.warnings])
    
    if exp_val:
        if exp_val.errors:
            all_errors.extend([f"[Experience] {e}" for e in exp_val.errors])
        if exp_val.warnings:
            all_warnings.extend([f"[Experience] {w}" for w in exp_val.warnings])
    
    if skills_val:
        if skills_val.errors:
            all_errors.extend([f"[Skills] {e}" for e in skills_val.errors])
        if skills_val.warnings:
            all_warnings.extend([f"[Skills] {w}" for w in skills_val.warnings])
    
    if all_errors or all_warnings:
        with st.expander(f"⚠️ Validation Details ({len(all_errors)} errors, {len(all_warnings)} warnings)"):
            if all_errors:
                st.markdown("**Errors:**")
                for error in all_errors:
                    st.error(error)
            if all_warnings:
                st.markdown("**Warnings:**")
                for warning in all_warnings:
                    st.warning(warning)
    
    # Regenerate button
    if st.button("🔄 Regenerate All Sections", use_container_width=True):
        generate_all_sections()
    
    st.markdown("---")
    
    # Editable sections with AI refinement
    st.subheader("✏️ Edit Generated Sections")
    
    tab1, tab2, tab3 = st.tabs(["📝 Summary", "💼 Experience", "🛠️ Skills"])
    
    with tab1:
        if st.session_state.generated_summary:
            # Header with copy button
            col_header1, col_header2 = st.columns([5, 1])
            with col_header1:
                st.markdown("**Summary LaTeX Code:**")
            with col_header2:
                if st.button("📋 Copy", key="copy_summary_btn", help="Click then select text below"):
                    st.toast("💡 Click in the text area below, press Cmd+A to select all, then Cmd+C to copy", icon="ℹ️")
            
            # Editable text area
            edited_summary = st.text_area(
                "Edit Summary",
                value=st.session_state.generated_summary,
                height=200,
                help="Edit the LaTeX code for the summary section",
                label_visibility="collapsed"
            )
            
            # Update if changed
            if edited_summary != st.session_state.generated_summary:
                st.session_state.generated_summary = edited_summary
                st.session_state.updated_latex = None  # Force regeneration
            
            # AI refinement for summary
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                summary_prompt = st.text_input(
                    "Refine summary",
                    placeholder="e.g., Make it more technical, Add more AI/ML keywords...",
                    key="summary_refine_prompt"
                )
            with col2:
                if st.button("🔄 Regenerate", key="regen_summary", use_container_width=True):
                    with st.spinner("Regenerating summary..."):
                        from api.claude_client import ClaudeClient
                        client = ClaudeClient()
                        new_summary = client.generate_summary(
                            st.session_state.old_summary,
                            st.session_state.job_description,
                            st.session_state.keywords
                        )
                        st.session_state.generated_summary = new_summary
                        st.session_state.updated_latex = None
                        st.success("✅ Summary regenerated!")
                        st.rerun()
            with col3:
                if st.button("✨ Refine", key="refine_summary"):
                    if summary_prompt:
                        refine_section("summary", summary_prompt)
        else:
            st.info("No summary generated")
    
    with tab2:
        if st.session_state.generated_experience:
            # Header with copy button
            col_header1, col_header2 = st.columns([5, 1])
            with col_header1:
                st.markdown("**Experience LaTeX Code:**")
            with col_header2:
                if st.button("📋 Copy", key="copy_experience_btn", help="Click then select text below"):
                    st.toast("💡 Click in the text area below, press Cmd+A to select all, then Cmd+C to copy", icon="ℹ️")
            
            edited_experience = st.text_area(
                "Edit Experience",
                value=st.session_state.generated_experience,
                height=300,
                help="Edit the LaTeX code for the experience section",
                label_visibility="collapsed"
            )
            
            # Update if changed
            if edited_experience != st.session_state.generated_experience:
                st.session_state.generated_experience = edited_experience
                st.session_state.updated_latex = None  # Force regeneration
            
            # AI refinement for experience
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                exp_prompt = st.text_input(
                    "Refine experience",
                    placeholder="e.g., Add more metrics, Emphasize leadership...",
                    key="exp_refine_prompt"
                )
            with col2:
                if st.button("🔄 Regenerate", key="regen_experience", use_container_width=True):
                    with st.spinner("Regenerating experience..."):
                        from api.claude_client import ClaudeClient
                        client = ClaudeClient()
                        new_experience = client.generate_experience(
                            st.session_state.old_experience,
                            st.session_state.job_description,
                            st.session_state.keywords
                        )
                        st.session_state.generated_experience = new_experience
                        st.session_state.updated_latex = None
                        st.success("✅ Experience regenerated!")
                        st.rerun()
            with col3:
                if st.button("✨ Refine", key="refine_experience"):
                    if exp_prompt:
                        refine_section("experience", exp_prompt)
        else:
            st.info("No experience generated")
    
    with tab3:
        if st.session_state.generated_skills:
            # Header with copy button
            col_header1, col_header2 = st.columns([5, 1])
            with col_header1:
                st.markdown("**Skills LaTeX Code:**")
            with col_header2:
                if st.button("📋 Copy", key="copy_skills_btn", help="Click then select text below"):
                    st.toast("💡 Click in the text area below, press Cmd+A to select all, then Cmd+C to copy", icon="ℹ️")
            
            edited_skills = st.text_area(
                "Edit Skills",
                value=st.session_state.generated_skills,
                height=200,
                help="Edit the LaTeX code for the skills section",
                label_visibility="collapsed"
            )
            
            # Update if changed
            if edited_skills != st.session_state.generated_skills:
                st.session_state.generated_skills = edited_skills
                st.session_state.updated_latex = None  # Force regeneration
            
            # AI refinement for skills
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                skills_prompt = st.text_input(
                    "Refine skills",
                    placeholder="e.g., Add cloud technologies, Reorganize by category...",
                    key="skills_refine_prompt"
                )
            with col2:
                if st.button("🔄 Regenerate", key="regen_skills", use_container_width=True):
                    with st.spinner("Regenerating skills..."):
                        from api.claude_client import ClaudeClient
                        client = ClaudeClient()
                        new_skills = client.generate_skills(
                            st.session_state.old_skills,
                            st.session_state.job_description,
                            st.session_state.keywords
                        )
                        st.session_state.generated_skills = new_skills
                        st.session_state.updated_latex = None
                        st.success("✅ Skills regenerated!")
                        st.rerun()
            with col3:
                if st.button("✨ Refine", key="refine_skills"):
                    if skills_prompt:
                        refine_section("skills", skills_prompt)
    
    st.markdown("---")
    
    # Main content: Full LaTeX Editor and Download
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Header with copy button
        col_header1, col_header2 = st.columns([5, 1])
        with col_header1:
            st.subheader("📝 Updated LaTeX Code")
        with col_header2:
            if st.session_state.updated_latex:
                if st.button("📋 Copy All", key="copy_full_latex", help="Copy entire LaTeX code", type="primary"):
                    # Just show toast - the text area below is already selectable
                    st.toast("✅ Select all text below (Cmd+A) and copy (Cmd+C)", icon="ℹ️")
        
        # Generate the updated LaTeX
        if st.session_state.updated_latex is None:
            st.session_state.updated_latex = apply_all_changes()
        
        # Display in text area for easy copying
        updated_code = st.text_area(
            "LaTeX Code (editable)",
            value=st.session_state.updated_latex,
            height=400,
            help="You can edit the code here before downloading",
            label_visibility="collapsed"
        )
        
        # Update session state if user edits
        if updated_code != st.session_state.updated_latex:
            st.session_state.updated_latex = updated_code
    
    with col2:
        st.subheader("📥 Download")
        
        # Download PDF button
        if st.button("🔨 Compile PDF", type="primary", use_container_width=True):
            compile_and_download()
        
        st.markdown("")
        
        # Download LaTeX button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📄 Download .tex",
            data=st.session_state.updated_latex,
            file_name=f"resume_{timestamp}.tex",
            mime="text/plain",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Quick stats
        st.caption("**Sections Updated:**")
        if st.session_state.generated_summary:
            st.caption("✅ Summary")
        if st.session_state.generated_experience:
            st.caption("✅ Experience")
        if st.session_state.generated_skills:
            st.caption("✅ Skills")
    
    st.markdown("---")
    
    # Strict HR ATS Match Checker
    st.subheader("🎯 Strict HR - ATS Match Check")
    
    if st.button("🔍 Run ATS Match Analysis", type="primary", use_container_width=True):
        run_ats_match_check()
    
    # Display ATS results if available
    if 'ats_result' in st.session_state and st.session_state.ats_result:
        result = st.session_state.ats_result
        
        # Match percentage and decision
        col1, col2 = st.columns(2)
        
        with col1:
            # Color code based on percentage
            if result['match_percentage'] >= 80:
                st.metric("Match Score", f"{result['match_percentage']}%", delta="Strong Match")
            elif result['match_percentage'] >= 60:
                st.metric("Match Score", f"{result['match_percentage']}%", delta="Moderate Match")
            else:
                st.metric("Match Score", f"{result['match_percentage']}%", delta="Weak Match", delta_color="inverse")
        
        with col2:
            if result['decision'] == 'YES':
                st.success(f"**Decision: ✅ {result['decision']}**")
                st.caption("Candidate is a fit for this role")
            else:
                st.error(f"**Decision: ❌ {result['decision']}**")
                st.caption("Candidate does not meet requirements")
        
        # Rationale
        st.markdown("**HR Rationale:**")
        st.info(result['rationale'])
        
        # Missing elements
        if result['missing_elements']:
            with st.expander("⚠️ Missing Requirements"):
                for item in result['missing_elements']:
                    st.markdown(f"- {item}")


def run_ats_match_check():
    """Run strict HR ATS match analysis on the generated resume."""
    try:
        with st.spinner("🔍 Running strict HR analysis..."):
            client = ClaudeClient()
            
            # Get the full updated resume
            if st.session_state.updated_latex is None:
                st.session_state.updated_latex = apply_all_changes()
            
            # Load and format ATS prompt from file
            from pathlib import Path
            
            prompt_path = Path(__file__).parent / "prompts" / "ats_match_prompt.md"
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            hr_prompt = prompt_template.format(
                job_description=st.session_state.job_description,
                resume_content=st.session_state.updated_latex
            )
            
            # Call Claude
            response = client.client.messages.create(
                model=client.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": hr_prompt}]
            )
            
            analysis = response.content[0].text.strip()
            
            # Parse the response
            import re
            
            match_pct = re.search(r'MATCH_PERCENTAGE:\s*(\d+)', analysis)
            decision = re.search(r'DECISION:\s*(YES|NO)', analysis)
            rationale = re.search(r'RATIONALE:\s*(.+?)(?=MISSING_ELEMENTS:|$)', analysis, re.DOTALL)
            missing = re.search(r'MISSING_ELEMENTS:\s*(.+)', analysis, re.DOTALL)
            
            # Extract missing elements
            missing_elements = []
            if missing:
                missing_text = missing.group(1).strip()
                missing_elements = [line.strip('- ').strip() for line in missing_text.split('\n') if line.strip().startswith('-')]
            
            # Store results
            st.session_state.ats_result = {
                'match_percentage': int(match_pct.group(1)) if match_pct else 0,
                'decision': decision.group(1) if decision else 'NO',
                'rationale': rationale.group(1).strip() if rationale else 'Analysis incomplete',
                'missing_elements': missing_elements
            }
            
            st.success("✅ ATS analysis complete!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error running ATS analysis: {str(e)}")


def refine_section(section_name: str, user_request: str):
    """Refine a specific section based on user request."""
    try:
        with st.spinner(f"🤔 Refining {section_name}..."):
            client = ClaudeClient()
            
            # Get current section content
            if section_name == "summary":
                current_content = st.session_state.generated_summary
                section_type = "Summary"
            elif section_name == "experience":
                current_content = st.session_state.generated_experience
                section_type = "Experience"
            elif section_name == "skills":
                current_content = st.session_state.generated_skills
                section_type = "Skills"
            else:
                st.error("Invalid section")
                return
            
            # Load and format refinement prompt from file
            from pathlib import Path
            
            prompt_path = Path(__file__).parent / "prompts" / "refinement_prompt.md"
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            refinement_prompt = prompt_template.format(
                section_type=section_type,
                user_request=user_request,
                current_content=current_content,
                keywords=', '.join(st.session_state.keywords)
            )
            
            # Call Claude
            response = client.client.messages.create(
                model=client.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": refinement_prompt}]
            )
            
            refined_content = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if refined_content.startswith("```"):
                refined_content = refined_content.split("```")[1]
                if refined_content.startswith("latex"):
                    refined_content = refined_content[5:]
                refined_content = refined_content.strip()
            
            # Update the appropriate section
            if section_name == "summary":
                st.session_state.generated_summary = refined_content
            elif section_name == "experience":
                st.session_state.generated_experience = refined_content
            elif section_name == "skills":
                st.session_state.generated_skills = refined_content
            
            # Force regeneration of full LaTeX
            st.session_state.updated_latex = None
            
            st.success(f"✅ {section_type} refined!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error refining {section_name}: {str(e)}")


def _latex_to_plain_text(latex_text: str) -> str:
    """Convert LaTeX text to plain text for preview."""
    import re
    
    # Remove common LaTeX commands but keep the content
    text = latex_text
    
    # Remove \resumeSubheading and extract content
    text = re.sub(r'\\resumeSubheading\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}', 
                  r'**\1** | \2\n\3 | \4\n', text)
    
    # Remove \resumeItem and keep content
    text = re.sub(r'\\resumeItem\{([^}]*)\}', r'• \1', text)
    
    # Remove \item and keep content
    text = re.sub(r'\\item\s+', r'• ', text)
    
    # Remove text formatting commands
    text = re.sub(r'\\textbf\{([^}]*)\}', r'**\1**', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'*\1*', text)
    text = re.sub(r'\\textcolor\{[^}]*\}\{([^}]*)\}', r'\1', text)
    
    # Remove other common LaTeX commands
    text = re.sub(r'\\small', '', text)
    text = re.sub(r'\\justifying', '', text)
    text = re.sub(r'\\begin\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{[^}]*\}', '', text)
    text = re.sub(r'\\section\{([^}]*)\}', r'## \1', text)
    
    # Remove remaining backslash commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()
    
    return text


def parse_item_bullets(text):
    """Parse \\item bullets from generated text, handling various formats."""
    if not text:
        return []
    
    lines = text.strip().split('\n')
    bullets = []
    
    for line in lines:
        line = line.strip()
        # Match \item with or without escaped backslash
        if line.startswith('\\item') or line.startswith(r'\item'):
            # Remove \item prefix using regex to handle both cases
            bullet = re.sub(r'^\\+item\s*', '', line)
            if bullet:
                bullets.append(bullet)
    
    return bullets


def display_summary_comparison():
    """Display old vs new summary."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Old Summary:**")
        if st.session_state.old_summary:
            for i, bullet in enumerate(st.session_state.old_summary, 1):
                st.write(f"{i}. {bullet}")
    
    with col2:
        st.markdown("**New Summary:**")
        if st.session_state.generated_summary:
            bullets = parse_item_bullets(st.session_state.generated_summary)
            for i, bullet in enumerate(bullets, 1):
                st.write(f"{i}. {bullet}")


def display_experience_comparison():
    """Display old vs new experience."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Old Experience:**")
        if st.session_state.old_experience:
            st.code(st.session_state.old_experience, language="latex")
    
    with col2:
        st.markdown("**New Experience:**")
        if st.session_state.generated_experience:
            st.code(st.session_state.generated_experience, language="latex")
        else:
            st.info("Experience section not generated")


def display_skills_comparison():
    """Display old vs new skills."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Old Skills:**")
        if st.session_state.old_skills:
            st.code(st.session_state.old_skills, language="latex")
    
    with col2:
        st.markdown("**New Skills:**")
        if st.session_state.generated_skills:
            st.code(st.session_state.generated_skills, language="latex")
        else:
            st.info("Skills section not generated")



def refine_with_chat(user_message: str):
    """Refine the resume based on user chat input."""
    try:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        with st.spinner("🤔 AI is thinking..."):
            client = ClaudeClient()
            
            # Create a refinement prompt
            refinement_prompt = f"""You are helping refine a resume. The user has requested the following change:

USER REQUEST: {user_message}

CURRENT RESUME (LaTeX):
{st.session_state.updated_latex}

Please provide:
1. A brief explanation of what you'll change (2-3 sentences)
2. The updated LaTeX code for the affected section(s)

Format your response as:
EXPLANATION: [your explanation]
UPDATED_CODE: [the updated LaTeX code]
"""
            
            # Call Claude
            response = client.client.messages.create(
                model=client.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": refinement_prompt}]
            )
            
            ai_response = response.content[0].text
            
            # Parse response
            if "EXPLANATION:" in ai_response and "UPDATED_CODE:" in ai_response:
                parts = ai_response.split("UPDATED_CODE:")
                explanation = parts[0].replace("EXPLANATION:", "").strip()
                updated_code = parts[1].strip()
                
                # Update the LaTeX in session state
                st.session_state.updated_latex = updated_code
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": explanation
                })
                
                st.success("✅ Resume updated!")
                st.rerun()
            else:
                # Just add the full response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"Sorry, I encountered an error: {str(e)}"
        })


def compile_and_download():
    """Compile LaTeX to PDF and offer download."""
    
    with st.spinner("📄 Compiling LaTeX to PDF..."):
        try:
            # Use the updated latex from session state (which may have been edited)
            updated_latex = st.session_state.updated_latex
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"resume_{timestamp}.pdf"
            
            success, error_msg = compile_latex_to_pdf(updated_latex, output_path)
            
            if success:
                with open(output_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                st.success("✅ PDF compiled successfully!")
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"tailored_resume_{timestamp}.pdf",
                    mime="application/pdf"
                )
                
                st.download_button(
                    label="📄 Download LaTeX Source",
                    data=updated_latex,
                    file_name=f"tailored_resume_{timestamp}.tex",
                    mime="text/plain"
                )
            else:
                st.error(f"❌ PDF compilation failed: {error_msg}")
                st.info("You can still download the LaTeX source and compile it manually.")
                
                st.download_button(
                    label="📄 Download LaTeX Source",
                    data=updated_latex,
                    file_name=f"tailored_resume_{timestamp}.tex",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def download_latex_only():
    """Download LaTeX source without compiling."""
    try:
        updated_latex = apply_all_changes()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📄 Download LaTeX Source",
            data=updated_latex,
            file_name=f"tailored_resume_{timestamp}.tex",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def apply_all_changes():
    """Apply all generated changes to the LaTeX content."""
    updated_latex = st.session_state.latex_content
    
    # Replace Summary
    if st.session_state.generated_summary:
        try:
            bullets = parse_item_bullets(st.session_state.generated_summary)
            if bullets:
                updated_latex = replace_summary_section(updated_latex, bullets)
        except Exception as e:
            st.error(f"Error in summary replacement: {type(e).__name__}: {str(e)}")
            raise
    
    # Replace Experience
    if st.session_state.generated_experience:
        try:
            updated_latex = replace_first_experience(updated_latex, st.session_state.generated_experience)
        except Exception as e:
            st.error(f"Error in experience replacement: {type(e).__name__}: {str(e)}")
            st.error(f"Generated experience type: {type(st.session_state.generated_experience)}")
            st.error(f"Generated experience (first 100 chars): {repr(st.session_state.generated_experience[:100])}")
            raise
    
    # Replace Skills
    if st.session_state.generated_skills:
        try:
            updated_latex = replace_skills_section(updated_latex, st.session_state.generated_skills)
        except Exception as e:
            st.error(f"Error in skills replacement: {type(e).__name__}: {str(e)}")
            raise
    
    return updated_latex



def display_job_board():
    """Display job board expander with recent job postings."""
    with st.expander("🔍 Job Board - Recent AI Engineer Jobs in Healthcare", expanded=False):
        st.markdown("*Fetch the latest job postings and auto-fill job descriptions*")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            role = st.text_input("Role", value="AI Engineer", key="job_role")
        with col2:
            industry = st.text_input("Industry", value="healthcare", key="job_industry")
        with col3:
            location = st.text_input("Location", value="United States", key="job_location")
        with col4:
            hours = st.number_input("Hours", min_value=1, max_value=168, value=24, key="job_hours")
        
        if st.button("🔄 Fetch Latest Jobs", type="primary", use_container_width=True):
            fetch_and_display_jobs(role, industry, hours, location)
        
        # Display jobs if available
        if st.session_state.jobs:
            st.markdown(f"**Found {len(st.session_state.jobs)} jobs:**")
            st.markdown("---")
            
            for job in st.session_state.jobs:
                display_job_card(job)
        elif 'jobs_fetched' in st.session_state and st.session_state.jobs_fetched:
            st.info("No jobs found matching your criteria. Try adjusting the filters.")


def fetch_and_display_jobs(role: str, industry: str, hours: int, location: str = "United States"):
    """Fetch jobs from API and update session state."""
    try:
        from api.job_fetcher import JobFetcher
        from config.settings import settings
        
        # Check if API keys are configured
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            st.error("❌ Adzuna API keys not configured. Please add ADZUNA_APP_ID and ADZUNA_APP_KEY to your .env file.")
            st.info("Sign up for free at: https://developer.adzuna.com/")
            return
        
        with st.spinner(f"🔍 Fetching {role} jobs in {industry} ({location}) from last {hours}h..."):
            fetcher = JobFetcher(settings.adzuna_app_id, settings.adzuna_app_key)
            
            # Map location to country code
            location_map = {
                "United States": "USA",
                "USA": "USA",
                "United Kingdom": "UK",
                "UK": "UK",
                "Canada": "CA",
                "Australia": "AU"
            }
            country_code = location_map.get(location, "USA")
            
            jobs = fetcher.fetch_jobs(
                role=role,
                industry=industry,
                hours=hours,
                location=country_code,
                max_results=settings.max_job_results
            )
            
            st.session_state.jobs = jobs
            st.session_state.jobs_fetched = True
            
            if jobs:
                st.success(f"✅ Found {len(jobs)} jobs!")
            else:
                st.warning("No jobs found. Try adjusting your search criteria.")
            
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error fetching jobs: {str(e)}")
        st.session_state.jobs = []
        st.session_state.jobs_fetched = True


def display_job_card(job: dict):
    """Display a single job card with 'Use This Job' button."""
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{job['title']}** at {job['company']}")
            st.caption(f"📍 {job['location']} • 🕒 Posted {job['posted_date']}")
            
            # Show job posting link
            if job.get('url'):
                st.markdown(f"🔗 [View Job Posting]({job['url']})")
            
            # Show salary if available
            if job.get('salary_min') and job.get('salary_max'):
                salary_min = f"${job['salary_min']:,.0f}"
                salary_max = f"${job['salary_max']:,.0f}"
                st.caption(f"💰 {salary_min} - {salary_max}")
            
            # Show snippet
            st.text(job['snippet'])
        
        with col2:
            if st.button("📋 Use This Job", key=f"use_job_{job['id']}", use_container_width=True, type="primary"):
                # Auto-fill job description in Step 2
                st.session_state.job_description = job['full_description']
                st.toast("✅ Job description loaded! Scroll down to Step 2.", icon="✅")
                st.rerun()
        
        st.markdown("---")


if __name__ == "__main__":
    main()
