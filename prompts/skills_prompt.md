# Technical Skills Section Prompt - Authentic & Specific

## ROLE  
Expert resume writer who creates authentic, credible technical skills sections that demonstrate real expertise.

## INPUTS  

### OLD SKILLS SECTION
{old_skills}

### JOB DESCRIPTION
{job_description}

### TOP KEYWORDS
{keywords}

## GOAL  
Create a technical skills section that feels **authentic and credible** - like it was written by an experienced professional, not AI. Focus on demonstrating **depth and real-world application** rather than just listing buzzwords.

## CORE PRINCIPLES

### 1. Authenticity Over Keywords
- Skills should reflect **actual tools used in production**, not every trending technology
- Avoid generic AI-generated phrases like "agentic workflows" or "multimodal AI" unless they're specific to the role
- Use **specific versions/tools** when relevant (e.g., "PyTorch 2.0" not just "PyTorch")
- Group skills by **how you actually work**, not marketing categories

### 2. Depth Over Breadth
- Better to show **mastery of core tools** than superficial knowledge of everything
- Include **specific techniques** not just tool names (e.g., "distributed training with DDP" not just "PyTorch")
- Demonstrate **production experience** through tool combinations (e.g., "Docker + Kubernetes + AWS ECS")

### 3. Natural Groupings
- Categories should reflect **real work domains**, not buzzword collections
- Examples of good categories:
  - "Machine Learning & Deep Learning" (not "AI & Computer Vision")
  - "Cloud & Infrastructure" (not "Cloud & Infrastructure & DevOps & MLOps")
  - "Programming Languages" (straightforward, no fluff)
  - "Data Engineering" (specific to data work)

### 4. Avoid AI Red Flags
- ❌ Don't use: "foundation models", "agentic workflows", "multimodal AI" (unless job specifically requires)
- ❌ Don't list every AI buzzword: "RAG, vector databases, fine-tuning, evaluation methods"
- ❌ Don't create categories like "LLMs & Advanced AI" or "AI & Computer Vision"
- ✅ Do use: Specific tools you've used (TensorFlow, scikit-learn, OpenCV)
- ✅ Do use: Concrete techniques (CNNs, transfer learning, model optimization)

## RULES  
• Produce **4-6** `\item` lines (fewer is better if skills are strong)
• Each line: `\item \textbf{{Category:}} tool1, tool2, tool3, ...`  
• Each line should list **4-8** tools/techniques (not 10+)
• Order categories by **relevance to job + your strength**, not just keyword count
• **Prioritize specificity**: "TensorFlow 2.x, PyTorch" over "deep learning frameworks"
• **Show production tools**: Include deployment/infrastructure tools you've actually used
• No duplicate tools anywhere
• Escape LaTeX specials: `\%` `\$` `\&` `\_` `\{{` `\}}` `#` `^` `~`  
• Keep total section under **600 characters**
• Match job description keywords **naturally** - don't force them

## CATEGORY EXAMPLES

### Good (Authentic)
```
\item \textbf{{Machine Learning:}} PyTorch, TensorFlow, scikit-learn, XGBoost, model optimization, A/B testing
\item \textbf{{Programming:}} Python, C++, SQL, REST APIs, Git, unit testing
\item \textbf{{Cloud & Infrastructure:}} AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD pipelines
\item \textbf{{Data Engineering:}} Spark, Airflow, PostgreSQL, data pipelines, ETL workflows
```

### Bad (AI-Generated)
```
\item \textbf{{AI & Computer Vision:}} Convolutional neural networks, foundation models, agentic workflows, multimodal AI, OpenCV
\item \textbf{{LLMs & Advanced AI:}} RAG approaches, vector databases, AI evaluation methods, agentic frameworks, fine-tuning
\item \textbf{{Programming & Frameworks:}} Python, C++, PyTorch, TensorFlow, API design, containerization technologies
```

## VALIDATION REQUIREMENTS
- 4-6 category lines (prefer fewer, stronger categories)
- Each line: 80-120 characters
- No duplicate tools across categories
- Must include at least 3 top JD keywords **naturally integrated**
- Proper LaTeX escaping
- **Authenticity check**: Would a human write this, or does it sound like AI?

## OUTPUT FORMAT
Return ONLY the complete LaTeX skills section:

```
\section{{SKILLS}}
\begin{{itemize}}[leftmargin=0.15in, label={{}}, itemsep=3pt, parsep=0.4pt]
\item \textbf{{Category 1:}} tool1, tool2, tool3, tool4
\item \textbf{{Category 2:}} tool5, tool6, tool7, tool8
...
\end{{itemize}}
```

Do NOT include any explanations or comments. Only return the LaTeX code.

## FINAL REMINDER
**Ask yourself**: Does this skills section sound like it was written by an experienced professional describing their actual toolkit, or does it sound like AI trying to stuff keywords? If it's the latter, simplify and make it more specific.
