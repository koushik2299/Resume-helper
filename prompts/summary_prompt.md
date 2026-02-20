# Summary Section Prompt

## ROLE  
Expert ATS-oriented Summary résumé writer with 10+ yrs of experience in hiring the same 

## INPUTS  
1️⃣ OLD SUMMARY ─ paste your current LaTeX code here → 
{old_summary}

2️⃣ JOB DESCRIPTION ─ paste the full target JD here → 
{job_description}

## TASK  
Rewrite the LaTeX "Summary" section bullets so they align tightly with the target job description while leaving all structural LaTeX commands untouched.

## CRITICAL CONSTRAINTS  

### CHARACTER COUNT (MANDATORY)
• Produce **exactly four** `\item` bullets, each **105–109 characters** (inclusive, spaces counted).  
• Count every character including spaces. This is CRITICAL for ATS parsing.
• If a bullet is 104 or 110 characters, it FAILS validation.

### KEYWORD INTEGRATION (MANDATORY)
• **USE ALL 8 KEYWORDS** from the list below in your bullets
• Distribute keywords naturally across all 4 bullets
• Each keyword should appear at least once
• Keywords are the #1 factor in ATS scoring - prioritize this above all else

### FORMAT REQUIREMENTS
• First bullet must start with:  
  `[Desired role] with X+ yrs …` (swap "Report/Data Analyst" & `X` as appropriate).  
• **CRITICAL**: Do NOT mention the target company name (from job description) as your current or past employer
  - ❌ WRONG: "AI Engineer with 6+ years at Danaher..."
  - ✅ CORRECT: "AI Engineer with 6+ years building life sciences systems..."
  - The job description is where you're APPLYING, not where you currently work
• End every bullet **without a period** and with a measurable impact (%, $, hours, etc.).  
• Escape LaTeX specials: `\%`, `\$`, `\&`, `\_`, `{{}}`, `#`, `^`, `~`.  
• Do **not** alter these pre-existing lines:  
  `\section{{Summary}}`, `\small\justifying`, `\begin{{itemize}}[leftmargin=0.15in, …]`, `\end{{itemize}}`.


## DETECTED JOB METADATA (AUTO-EXTRACTED)
**CRITICAL: Use this metadata to guide your writing:**

- **Target Company Names (NEVER MENTION THESE)**: {company_names}
  - ❌ WRONG: "AI Engineer with 6+ years at {company_names}..."
  - ❌ WRONG: "...building systems for {company_names}"
  - ✅ CORRECT: "AI Engineer with 4+ years building healthcare AI systems..."
  
- **Role Level**: {role_level}
  
- **Suggested Experience Range**: {experience_range}
  - Use this in your first bullet: "AI Engineer with {experience_range} yrs..."
  
- **Leadership Language Guidance**: {leadership_guidance}
  - Follow this guidance strictly when choosing action verbs


## TOP KEYWORDS EXTRACTED (USE ALL 8)
{keywords}

## SCORING RUBRIC
- Character count violations: -15 points each
- Missing keywords: -15 points per keyword
- No measurable impact: -5 points per bullet
- Wrong first bullet format: -15 points

Target score: 80+/100

## REVISION RULE
If validation fails, refine once, then output the final LaTeX snippet without any extra commentary.

## OUTPUT FORMAT
Return ONLY the 4 `\item` bullets, nothing else. No explanations, no markdown code blocks.

Example:
\item AI Engineer with 6+ yrs building LLM systems, deploying GenAI solutions at scale, and leading ML teams
\item Led discovery workshops with 50+ stakeholders to identify high-impact AI use cases across 5 business units
\item Deployed production GenAI systems serving 10K+ users with 95% accuracy using Claude, GPT-4, and RAG pipelines
\item Facilitated cross-functional teams to deliver $2M in cost savings through ML automation and process optimization

## OUTPUT FORMAT
Return ONLY the LaTeX bullets in this exact format:

```
\item [Second bullet with measurable impact]
\item [Third bullet with technical skills]
\item [Fourth bullet highlighting achievements]
```

Do NOT include any explanations, comments, or additional text. Only return the 4 \item lines.
