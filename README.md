# ResumeForge - AI-Powered Resume Builder

Phase 1 MVP: AI-powered resume tailoring with Summary section generation, validation, and PDF compilation.

## 🚀 Features

- **AI-Powered Generation**: Uses Claude API to tailor your resume summary to specific job descriptions
- **Intelligent Validation**: Automatic checks for character limits, keyword integration, and formatting
- **LaTeX Support**: Maintains professional LaTeX formatting throughout
- **PDF Compilation**: One-click compilation to PDF (requires LaTeX installation)
- **Keyword Analysis**: Extracts and matches top keywords from job descriptions

## 📋 Prerequisites

1. **Python 3.10 or higher**
   ```bash
   python --version
   ```

2. **LaTeX Distribution** (for PDF compilation)
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Download [MiKTeX](https://miktex.org/download)
   - **Linux**: `sudo apt-get install texlive-full`

3. **Claude API Key**
   - Sign up at [Anthropic](https://console.anthropic.com/)
   - Generate an API key

## 🛠️ Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd /Users/koushik/Documents/ResumeBuilder
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Claude API key:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

## 🎯 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **In your browser** (opens automatically at http://localhost:8501):
   
   - **Step 1**: Upload your LaTeX resume (.tex file) or load the sample template
   - **Step 2**: Paste the job description you're targeting
   - **Step 3**: Click "Generate Summary" to create tailored content
   - **Review**: Check validation results and compare old vs new
   - **Download**: Compile to PDF and download

## 📁 Project Structure

```
ResumeBuilder/
├── app.py                      # Main Streamlit application
├── config/
│   └── settings.py            # Configuration management
├── api/
│   └── claude_client.py       # Claude API integration
├── prompts/
│   └── summary_prompt.md      # AI prompt template
├── validators/
│   └── summary_validator.py   # Validation logic
├── utils/
│   ├── latex_parser.py        # LaTeX parsing
│   ├── keyword_analyzer.py    # Keyword extraction
│   └── pdf_generator.py       # PDF compilation
├── templates/
│   └── sample_resume.tex      # Sample LaTeX template
└── requirements.txt           # Python dependencies
```

## ✅ Validation Checks

The system validates generated summaries against these criteria:

1. ✓ Exactly 4 bullet points
2. ✓ Each bullet 105-109 characters
3. ✓ First bullet starts with "[Role] with X+ yrs"
4. ✓ No trailing periods
5. ✓ At least 5/8 top keywords included
6. ✓ LaTeX special characters properly escaped
7. ✓ Measurable impact in each bullet

## 🔧 Configuration

You can customize validation settings in `.env`:

```bash
# Character limits for summary bullets
SUMMARY_CHAR_MIN=105
SUMMARY_CHAR_MAX=109

# Number of bullets required
SUMMARY_BULLET_COUNT=4

# Keyword matching requirements
MIN_KEYWORDS_REQUIRED=5
TOP_KEYWORDS_COUNT=8

# Claude model
CLAUDE_MODEL=claude-sonnet-4-6
```

## 🐛 Troubleshooting

### "pdflatex not found"
- Install a LaTeX distribution (see Prerequisites)
- Verify installation: `pdflatex --version`
- You can still generate and download LaTeX source without PDF compilation

### "Claude API error"
- Check your API key in `.env`
- Verify you have API credits at https://console.anthropic.com/
- Check your internet connection

### "Could not find Summary section"
- Ensure your LaTeX file has a section marked with `%-----------SUMMARY-----------`
- Use the sample template as a reference
- Check that the section uses `\begin{itemize}...\end{itemize}` format

### Validation failures
- Review specific error messages in the UI
- Click "Regenerate" to try again
- The AI may need 1-2 attempts to meet all requirements

## 💡 Tips for Best Results

1. **Use detailed job descriptions**: More content = better keyword extraction
2. **Review and iterate**: Use the regenerate button if first attempt isn't perfect
3. **Check validation**: Address any errors before downloading
4. **Keep your base resume updated**: Better input = better output

## 🚧 Phase 1 Limitations

This MVP focuses on the Summary section only. Future phases will include:
- Projects section generation
- Skills section generation
- Job application tracking
- Analytics dashboard
- Multiple resume templates

## 📝 License

This project is for personal use.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the implementation plan in the artifacts directory
3. Check Claude API documentation at https://docs.anthropic.com/

---

**Built with**: Python, Streamlit, Claude API, LaTeX
