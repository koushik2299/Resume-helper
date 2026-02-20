# AI-Powered Resume Builder & Job Tracker
## Application Blueprint

---

## 📋 Executive Summary

**App Name:** ResumeForge (or your preferred name)

**Purpose:** An AI-powered application that automatically tailors resumes to specific job descriptions using LaTeX formatting and tracks job applications through a personalized dashboard.

**Core Value Proposition:** 
- Transform generic resumes into ATS-optimized, job-specific documents in minutes
- Maintain consistent LaTeX formatting and professional quality
- Track application progress and statistics in one centralized location

**Target Users:** Job seekers, especially those in technical fields who need to apply to multiple positions with tailored resumes

---

## 🎯 Core Features

### Feature 1: AI-Powered Resume Builder
**Description:** Automatically rewrites resume sections (Summary, Projects, Skills) to align with specific job descriptions while maintaining LaTeX formatting integrity.

**User Flow:**
1. User uploads existing resume (LaTeX format) OR selects from template library
2. User pastes target job description
3. System identifies key sections to optimize
4. AI generates tailored content for each section using predefined prompts
5. Built-in validators ensure formatting compliance (character limits, keyword density, etc.)
6. User reviews side-by-side comparison (old vs. new)
7. User makes manual edits if desired
8. System compiles LaTeX to PDF
9. User previews final PDF
10. User downloads or saves to library

**Key Components:**
- LaTeX parser/processor
- AI prompt engine (3 specialized prompts: Summary, Projects, Skills)
- Validation engine with automatic pass/fail checks
- PDF compilation engine
- Preview interface

**Success Criteria:**
- Generated sections pass all validators on first attempt (>80% success rate)
- Character limits strictly enforced (105-109 for summary, 100-110 for projects)
- Minimum 5/8 top JD keywords incorporated
- LaTeX special characters properly escaped

---

### Feature 2: Job Application Tracker
**Description:** Dashboard to monitor all job applications, track status progression, and view analytics.

**User Flow:**
1. After downloading resume, system prompts: "Have you applied?"
2. If yes, user enters application details (company, position, date)
3. Application saved to tracker with linked resume version
4. User can update status as application progresses
5. Dashboard displays all applications with filtering/sorting options
6. Analytics view shows success metrics

**Key Components:**
- Application entry form (triggered post-download)
- Status pipeline (Applied → Screening → Interview → Offer/Rejected)
- Dashboard with cards/table view
- Analytics engine
- Notes/reminders system

**Status Categories:**
- Applied
- Under Review
- Phone Screening
- Technical Interview
- Final Interview
- Offer Received
- Rejected
- Withdrawn

**Metrics to Track:**
- Total applications submitted
- Response rate (%)
- Interview conversion rate (%)
- Average time to first response
- Applications by company/industry
- Most successful resume versions

---

### Feature 3: Template & Version Management
**Description:** Library of LaTeX resume templates and version control for all generated resumes.

**User Flow:**
1. User accesses template library
2. User selects base template or uploads custom template
3. System stores template with categorization (industry, role type, style)
4. Every AI-generated resume is auto-versioned with metadata
5. User can browse past versions, compare, and reuse

**Key Components:**
- Template storage with tagging system
- Version history with diff viewer
- Metadata tracking (date created, target company, target role)
- Search/filter functionality

---

### Feature 4: Real-Time Validation & Feedback
**Description:** Instant feedback on resume quality with specific, actionable suggestions.

**Validation Checks:**

**Summary Section:**
- ✓ Exactly 4 bullets
- ✓ Each bullet 105-109 characters
- ✓ First bullet starts with "[Role] with X+ yrs"
- ✓ No trailing periods
- ✓ 5+ of top 8 JD keywords used
- ✓ LaTeX special characters escaped
- ✓ Measurable impact in each bullet

**Projects Section:**
- ✓ 3-4 bullets per project
- ✓ Each bullet 100-110 characters AND ≤17 words
- ✓ Quantified metrics present
- ✓ JD keywords integrated
- ✓ Strategic ordering by relevance

**Skills Section:**
- ✓ Maximum 6 categories
- ✓ 3-10 skills per category
- ✓ No duplicate skills
- ✓ Ordered by JD relevance
- ✓ Total section <650 characters

**User Interface:**
- Green checkmark for passed validations
- Red X with explanation for failed validations
- Yellow warning for suggestions
- Progress bar showing overall compliance

---

## 🏗️ Application Architecture

### High-Level Structure

```
AI Resume Builder App
│
├── Frontend Layer (Streamlit)
│   ├── Resume Builder Interface
│   ├── Job Tracker Dashboard
│   ├── Analytics View
│   └── Settings Panel
│
├── AI Engine Layer
│   ├── Prompt Management System
│   ├── LLM Interface (Claude API)
│   └── Response Parser
│
├── Processing Layer
│   ├── LaTeX Processor
│   ├── Validation Engine
│   ├── PDF Generator
│   └── Keyword Analyzer
│
├── Data Layer
│   ├── Database (SQLite/PostgreSQL)
│   ├── File Storage (PDFs, LaTeX files)
│   └── Template Library
│
└── Business Logic Layer
    ├── Application Manager
    ├── Version Controller
    └── Analytics Calculator
```

---

## 📊 Data Models

### User
```
- user_id (PK)
- name
- email
- default_contact_info (JSON)
- created_at
- preferences (JSON)
```

### Resume Templates
```
- template_id (PK)
- user_id (FK)
- template_name
- latex_content
- category (industry/role)
- is_default (boolean)
- created_at
- last_used
```

### Resume Versions
```
- version_id (PK)
- user_id (FK)
- base_template_id (FK)
- latex_content (full LaTeX code)
- pdf_path
- target_company
- target_position
- target_role_type
- created_at
- validation_score
- keywords_matched (array)
```

### Job Descriptions
```
- jd_id (PK)
- user_id (FK)
- company_name
- position_title
- full_description (text)
- extracted_keywords (array)
- salary_range
- location
- posted_date
- source_url
- saved_at
```

### Applications
```
- application_id (PK)
- user_id (FK)
- resume_version_id (FK)
- jd_id (FK)
- company_name
- position_title
- application_date
- current_status
- last_updated
- notes (text)
- follow_up_date
- outcome
```

### Status History
```
- history_id (PK)
- application_id (FK)
- old_status
- new_status
- changed_at
- notes
```

---

## 🔄 User Workflows

### Workflow 1: Create Tailored Resume (First Time User)

```
START
  ↓
[Upload existing resume OR select template]
  ↓
[System parses LaTeX structure]
  ↓
[User pastes job description]
  ↓
[System analyzes JD for keywords and requirements]
  ↓
[Display: "Generating Summary section..."]
  ↓
[AI generates Summary with 4 bullets]
  ↓
[Validator runs automatically]
  ↓
[Pass?] → YES → [Display green checkmarks]
       → NO → [Display errors + auto-retry once]
  ↓
[User reviews and optionally edits]
  ↓
[Repeat for Projects section]
  ↓
[Repeat for Skills section]
  ↓
[Compile full LaTeX document]
  ↓
[Generate PDF preview]
  ↓
[User reviews PDF in split-screen view]
  ↓
[User clicks "Download PDF"]
  ↓
[Prompt: "Have you applied to this job?"]
  ↓
[Yes] → [Save to Job Tracker with details]
[No] → [Save resume version only]
  ↓
END
```

### Workflow 2: Track Job Application

```
START (from Resume Builder OR manual entry)
  ↓
[User fills application form]
  - Company name *
  - Position title *
  - Application date
  - Link resume version (if from builder)
  - Notes (optional)
  ↓
[Save to database with status: "Applied"]
  ↓
[Show in Job Tracker dashboard]
  ↓
[User updates status when progress occurs]
  ↓
[System logs status change with timestamp]
  ↓
[Analytics automatically updated]
  ↓
END
```

### Workflow 3: Reuse Previous Resume for New Job

```
START
  ↓
[User navigates to "My Resumes"]
  ↓
[Browse previous versions with metadata]
  ↓
[Select resume closest to new target]
  ↓
[Click "Tailor to New Job"]
  ↓
[Paste new job description]
  ↓
[System re-runs AI generation on selected sections only]
  ↓
[Validator checks updates]
  ↓
[User reviews changes (highlighted diff view)]
  ↓
[Save as new version]
  ↓
END
```

### Workflow 4: Bulk Application Session

```
START
  ↓
[User uploads 5 job descriptions]
  ↓
[System queues them for processing]
  ↓
[For each JD:]
    [Generate tailored resume]
    [Validate]
    [Save version]
  ↓
[Display grid of 5 generated PDFs]
  ↓
[User downloads all]
  ↓
[Batch import to Job Tracker]
  ↓
END
```

---

## 🎨 User Interface Design

### Page 1: Resume Builder

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  ResumeForge                    [Settings] [Help]       │
├─────────────────────────────────────────────────────────┤
│  📝 Resume Builder                                      │
├───────────────────┬─────────────────────────────────────┤
│                   │                                     │
│  STEP 1: Input    │   PREVIEW PANEL                     │
│  ┌─────────────┐  │   ┌──────────────────────────┐     │
│  │ Upload LaTeX│  │   │                          │     │
│  │     or      │  │   │  [PDF Preview]           │     │
│  │ Select Template│ │   │                          │     │
│  └─────────────┘  │   │                          │     │
│                   │   │                          │     │
│  STEP 2: Job Desc │   └──────────────────────────┘     │
│  ┌─────────────┐  │                                     │
│  │ Paste JD    │  │   VALIDATION STATUS                 │
│  │             │  │   Summary:  ✓ Pass                  │
│  │             │  │   Projects: ✓ Pass                  │
│  └─────────────┘  │   Skills:   ⚠ 2 issues              │
│                   │                                     │
│  STEP 3: Generate │   [View Details]                    │
│  [Generate All]   │                                     │
│  [Generate Section▾] [Download PDF]                    │
│                   │                                     │
└───────────────────┴─────────────────────────────────────┘
```

**Section Generation Panel (Expandable):**
```
┌──────────────────────────────────────────────────┐
│  SUMMARY SECTION                    [Regenerate] │
├──────────────────────────────────────────────────┤
│  OLD VERSION          │  NEW VERSION             │
│  ─────────────────────┼─────────────────────────│
│  AI Engineer with 2+  │  AI Engineer with 5+    │
│  yrs Building RAG...  │  yrs building AI agents..│
│                       │                          │
│  [Show Full]          │  [Edit] [Accept]         │
├──────────────────────────────────────────────────┤
│  VALIDATION: ✓ All checks passed                 │
│  Keywords matched: 6/8                           │
│  Character counts: ✓ ✓ ✓ ✓                       │
└──────────────────────────────────────────────────┘
```

### Page 2: Job Tracker Dashboard

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  📊 Job Tracker                                         │
├─────────────────────────────────────────────────────────┤
│  STATS SUMMARY                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   42     │ │   12     │ │   5      │ │   28%    │  │
│  │ Applied  │ │ Reviewing│ │Interview │ │ Response │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  FILTERS: [All] [Applied] [Interview] [Offer]          │
│  SORT BY: [Date ▼] [Company] [Status]                  │
├─────────────────────────────────────────────────────────┤
│  APPLICATIONS                                           │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Google - ML Engineer          Applied 2/1/26      │ │
│  │ Status: Phone Screening       [Update] [Notes]    │ │
│  │ Resume: v2.3 | Next: Call on 2/15                 │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Meta - AI Research            Applied 1/28/26     │ │
│  │ Status: Under Review          [Update] [Notes]    │ │
│  │ Resume: v2.1 | Next: Follow-up 2/12               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  [+ Add Application Manually]                          │
└─────────────────────────────────────────────────────────┘
```

### Page 3: Analytics

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  📈 Analytics                                           │
├─────────────────────────────────────────────────────────┤
│  TIME RANGE: [Last 30 Days ▼]                          │
├─────────────────────────────────────────────────────────┤
│  APPLICATION FUNNEL                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Applied (42)     ████████████████████████ 100%  │   │
│  │ Reviewed (18)    ██████████ 43%                 │   │
│  │ Interview (5)    ███ 12%                        │   │
│  │ Offer (1)        █ 2%                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  TOP COMPANIES                                          │
│  1. Google (5 applications)                             │
│  2. Meta (3 applications)                               │
│  3. Amazon (3 applications)                             │
│                                                         │
│  SUCCESS RATE BY RESUME VERSION                         │
│  [Chart showing which resume versions got most responses]│
│                                                         │
│  AVERAGE TIME TO RESPONSE: 8.5 days                     │
└─────────────────────────────────────────────────────────┘
```

### Page 4: Settings

**Sections:**
- **API Configuration**
  - Claude API key
  - Model selection (default: Sonnet 4.5)
  - Rate limiting preferences

- **Default Information**
  - Name, email, phone, location
  - LinkedIn, GitHub links
  - Default LaTeX header/footer

- **Validator Settings**
  - Strictness level (Strict/Moderate/Relaxed)
  - Auto-retry failed validations
  - Character limit tolerances

- **Template Management**
  - Upload new templates
  - Set default template
  - Delete unused templates

- **Export/Import**
  - Export all data (JSON)
  - Import previous session
  - Backup database

---

## 🤖 AI Prompt System

### Prompt Architecture

Each resume section has:
1. **System Role Definition** - Who the AI is acting as
2. **Input Structure** - Formatted placeholders for old content and JD
3. **Task Instructions** - What to generate
4. **Constraints** - Hard rules (character limits, keyword requirements)
5. **Validation Function** - Python code to check output
6. **Revision Rules** - How to handle failures

### Prompt Files Structure

```
prompts/
├── summary_prompt.md       # Complete prompt for Summary section
├── projects_prompt.md      # Complete prompt for Projects section
├── skills_prompt.md        # Complete prompt for Skills section
├── validators/
│   ├── summary_validator.py
│   ├── projects_validator.py
│   └── skills_validator.py
└── prompt_config.yaml      # Settings for all prompts
```

### Prompt Execution Flow

```
1. Load prompt template from file
2. Extract old LaTeX section content
3. Parse job description
4. Format prompt with inputs:
   - {old_summary} → parsed LaTeX
   - {job_description} → full JD text
5. Send to Claude API
6. Receive generated content
7. Run validator function on output
8. If PASS → return to user
9. If FAIL → log errors, retry once with error feedback
10. Display final result with validation status
```

### Prompt Management Features

- **Version Control:** Track prompt iterations and performance
- **A/B Testing:** Test prompt variations to optimize results
- **Performance Metrics:** Track pass rate, retry rate, user edits
- **Customization:** Allow users to adjust prompt strictness

---

## 📐 Technical Requirements

### LaTeX Processing

**Capabilities Needed:**
- Parse LaTeX documents and extract sections
- Identify section boundaries (`\section{}`, `\resumeSubheading`, etc.)
- Preserve formatting commands
- Properly escape special characters: `% $ & _ { } # ^ ~`
- Compile LaTeX to PDF using `pdflatex` or similar
- Handle common LaTeX packages and dependencies

**Tools:**
- Regex for parsing (careful with nested braces)
- Subprocess calls to `pdflatex`
- Error handling for compilation failures
- Temporary file management

### Validation Engine

**Components:**
- Character counter (including spaces)
- Word counter
- Keyword extractor (from JD)
- Keyword matcher (in generated content)
- Special character escape checker
- Structure validator (bullet count, format)

**Validation Process:**
```python
def validate_section(section_content, section_type, job_description):
    """
    Returns: {
        "passed": boolean,
        "errors": [list of error strings],
        "warnings": [list of warning strings],
        "score": 0-100
    }
    """
```

### API Integration

**Claude API Requirements:**
- Authentication with API key
- Proper prompt formatting
- Token management (stay within limits)
- Error handling (rate limits, timeouts)
- Response parsing
- Cost tracking

**Rate Limiting Strategy:**
- Cache frequently used prompts
- Batch similar requests
- Implement exponential backoff
- Show user cost estimates before generation

### Data Storage

**File Storage:**
- PDF files: `/storage/pdfs/{user_id}/{version_id}.pdf`
- LaTeX sources: `/storage/latex/{user_id}/{version_id}.tex`
- Templates: `/storage/templates/{template_id}.tex`

**Database Schema:**
- Relational database (SQLite for MVP, PostgreSQL for production)
- Indexed fields: user_id, created_at, company_name
- Full-text search on job descriptions and notes

---

## 🔐 Security & Privacy

### Data Protection
- User resumes contain PII → must be encrypted at rest
- Secure API key storage (never in code/frontend)
- Database encryption for sensitive fields
- Regular backups with encryption

### Access Control
- User authentication (even if single-user MVP)
- Session management
- API key rotation capabilities
- Audit logs for data access

### Privacy Considerations
- Job descriptions may be copyrighted → citation/attribution
- Resume content is user IP → clear ownership terms
- No data sharing with third parties
- Option to delete all data permanently

---

## 📈 Success Metrics

### Product Metrics
- **Adoption:** Number of active users
- **Engagement:** Resumes generated per user per week
- **Quality:** Validation pass rate on first generation
- **Efficiency:** Time from JD paste to PDF download (target: <3 minutes)
- **Satisfaction:** User ratings/feedback scores

### Technical Metrics
- **API Performance:** Average response time from Claude API
- **Validation Accuracy:** False positive/negative rate
- **PDF Generation:** Success rate, average time
- **Uptime:** Application availability percentage
- **Error Rate:** Failed generations requiring manual intervention

### Business Metrics
- **Conversion:** Resumes generated → applications tracked
- **ROI:** Interview rate improvement for users
- **Retention:** Users returning for multiple job applications
- **Cost:** API costs per resume generated

---

## 🚀 Development Phases

### Phase 1: MVP (4-6 weeks)
**Goal:** Basic resume generation and validation

**Features:**
- Single LaTeX template support
- Summary section AI generation with validation
- Manual PDF compilation
- Basic file download
- No job tracking

**Deliverables:**
- Working Streamlit app (local only)
- Summary prompt + validator integrated
- LaTeX → PDF pipeline functional
- User can upload LaTeX, paste JD, get tailored summary

---

### Phase 2: Core Features (6-8 weeks)
**Goal:** Complete resume builder + basic tracking

**Features:**
- Projects and Skills section generation
- All three validators working
- Template library (3-5 pre-built templates)
- Job tracker with manual entry
- Basic dashboard (table view of applications)
- PDF preview before download

**Deliverables:**
- Full resume generation pipeline
- SQLite database with core tables
- Job tracker CRUD operations
- Application status updates

---

### Phase 3: Enhanced UX (4-6 weeks)
**Goal:** Polish and analytics

**Features:**
- Side-by-side old vs. new comparison
- Inline editing with live validation
- Analytics dashboard
- Status history timeline
- Search and filter in job tracker
- Export to CSV
- Version comparison (diff view)

**Deliverables:**
- Improved UI/UX with better layouts
- Analytics engine with charts
- Advanced filtering and search
- Better error messages and guidance

---

### Phase 4: Advanced Features (Ongoing)
**Goal:** Power user capabilities

**Features:**
- Bulk generation (multiple JDs at once)
- Chrome extension for JD capture
- Job board integration (scrape recent postings)
- Smart recommendations (which jobs to apply to)
- Resume A/B testing insights
- Custom prompt editing
- Collaborative features (share templates)
- Mobile responsive design

**Future Considerations:**
- AI interview prep based on JD
- Cover letter generation
- LinkedIn profile optimizer
- Application deadline reminders
- Integration with ATS systems

---

## 🛠️ Technology Stack Recommendations

### Frontend
- **Streamlit** - Primary framework (rapid prototyping, built-in components)
- **streamlit-extras** - Enhanced UI components
- **streamlit-aggrid** - Better table displays for job tracker
- **plotly** - Interactive charts for analytics

### Backend / Core
- **Python 3.10+** - Main language
- **anthropic** - Claude API client
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation and settings

### LaTeX Processing
- **pylatex** - Pythonic LaTeX generation
- **subprocess** - Call pdflatex/latexmk
- **PyPDF2 / pypdf** - PDF manipulation
- **regex** - LaTeX parsing

### Data & Storage
- **SQLite** - Initial database (file-based, simple)
- **PostgreSQL** - Production upgrade path
- **pandas** - Data manipulation and analytics

### Utilities
- **python-dotenv** - Environment variables
- **jinja2** - Template rendering for prompts
- **python-dateutil** - Date handling
- **requests** - HTTP requests (for future job board APIs)

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Type checking
- **pre-commit** - Git hooks for quality

---

## 🧪 Testing Strategy

### Unit Tests
- LaTeX parser functions
- Each validator independently
- Database CRUD operations
- Prompt formatting logic

### Integration Tests
- Full resume generation pipeline
- LaTeX → PDF compilation
- API communication with Claude
- Database transactions

### User Acceptance Tests
- Complete workflows from upload to download
- Validation error handling
- Edge cases (malformed LaTeX, empty JDs)
- Cross-browser compatibility

### Performance Tests
- Large LaTeX documents (10+ pages)
- Bulk generation (10+ resumes)
- Database queries with 100+ applications
- API response time monitoring

---

## 🐛 Known Challenges & Solutions

### Challenge 1: LaTeX Parsing Complexity
**Problem:** LaTeX has complex nesting, custom commands, and edge cases

**Solutions:**
- Start with simple regex patterns for common structures
- Build parser incrementally, adding edge cases as discovered
- Provide clear error messages when parsing fails
- Allow manual section marking as fallback
- Maintain library of tested templates

### Challenge 2: Claude API Costs
**Problem:** Each resume generation requires 3+ API calls, costs add up

**Solutions:**
- Cache job description analysis (reuse keywords for similar JDs)
- Implement user-configurable "generation modes" (quick/thorough)
- Show cost estimate before generation
- Batch requests when possible
- Consider cheaper models for initial validation passes

### Challenge 3: Validation False Positives
**Problem:** Validators might be too strict, rejecting good content

**Solutions:**
- Implement validator "strictness" settings
- Log all validation failures for analysis
- Provide manual override option
- Continuously refine validator rules based on user feedback
- A/B test different validation thresholds

### Challenge 4: PDF Compilation Failures
**Problem:** LaTeX compilation can fail due to missing packages, syntax errors

**Solutions:**
- Containerized LaTeX environment with all common packages
- Detailed error logging with line numbers
- Fallback to simpler compilation mode
- Pre-validate LaTeX syntax before compilation
- Provide "safe mode" templates guaranteed to compile

### Challenge 5: Keyword Extraction Accuracy
**Problem:** Identifying "important" JD keywords is subjective

**Solutions:**
- Use multiple keyword extraction methods (frequency, TF-IDF, NLP)
- Weight keywords by position in JD (title/requirements sections)
- Allow user to manually highlight key phrases
- Learn from successful applications (which keywords correlated with interviews)

---

## 💡 Differentiation & Innovation

### What Makes This App Unique?

1. **LaTeX-First Approach**
   - Most resume builders use WYSIWYG editors
   - LaTeX ensures professional, consistent formatting
   - Appeals to technical users who value precision

2. **Validation-Driven AI**
   - Not just "generate and hope"
   - Built-in quality checks ensure ATS compliance
   - Immediate feedback loop improves results

3. **Integrated Tracking**
   - Most tools separate resume building from application tracking
   - Seamless flow from generation to tracking
   - Analytics tied to specific resume versions

4. **Prompt Transparency**
   - Users can see and customize prompts
   - Educational aspect - learn what makes good resume content
   - Advanced users can fine-tune for their industry

5. **Version Intelligence**
   - Track which resume versions perform best
   - Data-driven insights on what works
   - Historical context for every application

---

## 📋 User Stories

### Story 1: Recent Graduate
**As a** recent CS graduate  
**I want to** quickly tailor my resume to 20+ entry-level positions  
**So that** I can maximize my chances of getting interviews without spending hours on each application

**Acceptance Criteria:**
- Can generate 20 tailored resumes in under 1 hour
- Each resume passes ATS keyword checks
- Can track all 20 applications in dashboard
- Can see which companies have responded

---

### Story 2: Career Switcher
**As a** professional switching from data analyst to AI engineer  
**I want to** reframe my existing experience to highlight relevant AI/ML skills  
**So that** I can compete with candidates who have traditional AI backgrounds

**Acceptance Criteria:**
- AI rewrites bullets to emphasize transferable skills
- Keywords match target AI engineer JDs
- Can A/B test different versions to see what works
- Can track success rate of different resume approaches

---

### Story 3: Active Job Seeker
**As an** employed professional casually exploring opportunities  
**I want to** track my applications and follow-ups without a spreadsheet  
**So that** I don't miss opportunities or follow-up deadlines

**Acceptance Criteria:**
- Can add applications even without using resume builder
- Get reminders for follow-ups
- See timeline of all interactions with each company
- Can add notes about recruiter conversations

---

### Story 4: Serial Applicant
**As someone** applying to 100+ jobs per month  
**I want to** automate as much of the resume tailoring as possible  
**So that** I can maintain quality while achieving high volume

**Acceptance Criteria:**
- Bulk generation mode for multiple JDs
- Template presets for common role types
- Quick review interface for batch approvals
- Batch import to tracker

---

## 🎓 Future Enhancements

### Short-term (3-6 months)
- Cover letter generation using same prompt system
- LinkedIn profile optimizer
- Email templates for follow-ups
- Interview question generator based on JD
- Salary negotiation calculator
- Application deadline calendar view

### Medium-term (6-12 months)
- Chrome extension for one-click JD capture
- Integration with LinkedIn Easy Apply
- Auto-fetch jobs from boards (Indeed, LinkedIn, etc.)
- Collaborative features (share templates with team)
- AI mock interviewer
- Offer comparison tool

### Long-term (12+ months)
- Mobile app (iOS/Android)
- Multi-language support
- Industry-specific templates and validators
- Company research integration
- Networking contact manager
- Career trajectory planner
- Integration with ATS systems for real-time status

---

## 📖 Documentation Plan

### User Documentation
1. **Quick Start Guide** - 5 min tutorial
2. **Video Walkthrough** - Complete workflow demo
3. **FAQ** - Common questions and troubleshooting
4. **Prompt Guide** - How the AI works, how to interpret validations
5. **Best Practices** - Resume writing tips, keyword strategy

### Developer Documentation
1. **Architecture Overview** - System design
2. **Setup Instructions** - Local development environment
3. **API Reference** - Internal functions and modules
4. **Database Schema** - ER diagrams and relationships
5. **Deployment Guide** - Production setup
6. **Contributing Guide** - For open source contributors

### Prompt Documentation
1. **Prompt Engineering Guide** - How prompts were designed
2. **Validation Logic** - How each validator works
3. **Customization Guide** - How to modify prompts
4. **Performance Metrics** - Prompt success rates

---

## 🔄 Iteration & Feedback

### Feedback Collection Methods
- In-app feedback button on every page
- Post-generation survey (optional, 2 questions)
- Success tracking (did this resume get you an interview?)
- Analytics on feature usage
- Monthly user interviews (5-10 power users)

### Metrics to Monitor
- Which sections require the most manual edits?
- What validation rules fail most often?
- Which templates are most popular?
- Average time spent per resume?
- Correlation between validation score and interview rate?

### Continuous Improvement Process
1. Collect weekly usage data
2. Analyze validation failures
3. Review user feedback
4. Prioritize improvements
5. A/B test changes
6. Deploy incrementally
7. Measure impact

---

## 💰 Business Model (Optional)

### Free Tier
- 5 resume generations per month
- Basic templates (2 options)
- Standard validation
- Manual application tracking (up to 25 applications)
- Core analytics

### Pro Tier ($15-25/month)
- Unlimited resume generations
- All premium templates
- Bulk generation mode
- Advanced analytics
- Resume version comparison
- Priority API access
- Chrome extension
- Export data

### Enterprise (Custom pricing)
- Team accounts
- Shared template library
- Company branding on resumes
- Usage analytics dashboard
- API access for integrations
- Dedicated support

---

## 🎯 Success Criteria for MVP

The MVP will be considered successful if:

1. **Functional:** Users can generate a complete, valid resume in <5 minutes
2. **Quality:** 80%+ of generated sections pass validation on first try
3. **Usable:** Users rate the interface 4/5 or higher on ease of use
4. **Valuable:** Users report the tailored resume is better than their manual attempt
5. **Trackable:** Users can add and update at least 10 applications
6. **Stable:** Less than 5% error rate in PDF generation
7. **Adoptable:** At least 10 beta users actively use it for real job searches

---

## 📝 Open Questions

1. **API Strategy:** Use Claude API directly or build abstraction layer to support multiple LLM providers?

2. **Template Format:** Standardize on specific LaTeX document class or support arbitrary formats?

3. **Deployment:** Local-only app (desktop) or web-hosted (Streamlit Cloud)?

4. **Authentication:** Single-user mode or multi-user with auth?

5. **Job Board Integration:** Worth the complexity or let users paste manually?

6. **Pricing:** Start free forever or plan for monetization from day 1?

7. **Open Source:** Keep proprietary or open source the core engine?

8. **Data Portability:** Allow export/import in standard formats (JSON, CSV)?

9. **Collaboration:** Solo tool or team features (shared templates, company knowledge base)?

10. **Platform:** Web-only or also build native desktop app?

---

## 🏁 Next Steps

### Immediate Actions (Week 1)
1. ✅ Finalize blueprint (this document)
2. Set up development environment
3. Create basic Streamlit app skeleton
4. Implement LaTeX parser for Summary section
5. Integrate Claude API with Summary prompt
6. Build Summary validator

### Week 2-3
7. Implement Projects and Skills sections
8. Build PDF generation pipeline
9. Create basic file upload/download flow
10. Design database schema
11. Implement SQLite database with basic tables

### Week 4-6
12. Build job tracker CRUD operations
13. Create dashboard interface
14. Add application status updates
15. Implement validation UI (checkmarks, errors)
16. End-to-end testing

### Week 7-8
17. Beta testing with 5-10 users
18. Bug fixes and UX improvements
19. Documentation
20. Prepare for launch

---

## 📚 Appendix

### A. Sample LaTeX Structure
```latex
\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{enumitem}

\begin{document}

%-----------SUMMARY-----------
\section{Summary}
\begin{itemize}[leftmargin=0.15in, labelsep=0.1in]
\item First bullet here
\item Second bullet here
\item Third bullet here
\item Fourth bullet here
\end{itemize}

%-----------EXPERIENCE-----------
\section{Experience}
\resumeSubheading
{Company Name}{Dates}
{Role Title}{Location}
\resumeItemListStart
\resumeItem{First accomplishment bullet}
\resumeItem{Second accomplishment bullet}
\resumeItemListEnd

%-----------SKILLS-----------
\section{SKILLS}
\begin{itemize}[leftmargin=0.15in, label={}]
\item \textbf{Category 1:} skill1, skill2, skill3
\item \textbf{Category 2:} skill4, skill5, skill6
\end{itemize}

\end{document}
```

### B. Sample Job Description Analysis
```
Input JD: "We're looking for an AI Engineer with 5+ years of Python experience to build production LLM agents using pydantic-ai..."

Extracted Keywords (Top 8):
1. Python (frequency: 5)
2. agents (frequency: 4)
3. production (frequency: 3)
4. LLMs (frequency: 3)
5. pydantic-ai (frequency: 2)
6. workflows (frequency: 2)
7. clinical (frequency: 2)
8. Docker (frequency: 1)

Required Skills Detected:
- Python (5+ years)
- LLMs (deep experience)
- Agent frameworks
- Docker, Kubernetes
- Production deployment

Nice-to-Have:
- Frontend work
- Healthcare domain knowledge
```

### C. Validation Examples

**Pass Example:**
```latex
\item AI Engineer with 5+ yrs building LLM agents in Python; shipped pydantic-ai tools saving 1,000 hours
```
- ✓ Character count: 107 (within 105-109)
- ✓ Starts with "AI Engineer with 5+ yrs"
- ✓ No trailing period
- ✓ Measurable impact: "1,000 hours"
- ✓ Keywords: AI Engineer, LLM agents, Python, pydantic-ai (4/8)
- ✓ Special characters escaped properly

**Fail Example:**
```latex
\item Experienced AI Engineer who has been building production-grade LLM systems for over 5 years using Python.
```
- ✗ Character count: 115 (exceeds 109)
- ✗ Doesn't start with required format
- ✗ Has trailing period
- ✓ Has measurable impact implied
- ✓ Has keywords

### D. Database Query Examples

**Get all applications for a user:**
```sql
SELECT 
    a.application_id,
    a.company_name,
    a.position_title,
    a.current_status,
    a.application_date,
    rv.validation_score
FROM applications a
LEFT JOIN resume_versions rv ON a.resume_version_id = rv.version_id
WHERE a.user_id = ?
ORDER BY a.application_date DESC;
```

**Calculate response rate:**
```sql
SELECT 
    COUNT(*) as total_applications,
    SUM(CASE WHEN current_status != 'Applied' THEN 1 ELSE 0 END) as responses,
    ROUND(100.0 * SUM(CASE WHEN current_status != 'Applied' THEN 1 ELSE 0 END) / COUNT(*), 2) as response_rate
FROM applications
WHERE user_id = ?;
```

**Find best performing resume version:**
```sql
SELECT 
    rv.version_id,
    rv.target_role_type,
    COUNT(a.application_id) as times_used,
    SUM(CASE WHEN a.current_status IN ('Interview', 'Offer Received') THEN 1 ELSE 0 END) as successes
FROM resume_versions rv
LEFT JOIN applications a ON rv.version_id = a.resume_version_id
WHERE rv.user_id = ?
GROUP BY rv.version_id
ORDER BY successes DESC
LIMIT 5;
```

---

## 📌 Version History

**v1.0** - February 8, 2026 - Initial blueprint created
- Core features defined
- Architecture outlined
- Workflows documented
- Development phases planned

---

**END OF BLUEPRINT**

This document is a living guide and will be updated as the application evolves.
