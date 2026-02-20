"""Test script to verify JD analyzer and validation with R37 job description."""

from utils.jd_analyzer import JDAnalyzer
from validators.summary_validator import SummaryValidator, SummaryValidationContext

# R37 Job Description
JD = """R1 is thrilled to introduce R37 committed to transforming healthcare financial performance so providers can focus on delivering exceptional care. R37 is pioneering an AI-driven approach to revolutionize revenue cycle management. Today we serve 95 of the top 100 hospital systems in the US and R37 will serve as the AI platform layer delivering results for our customers. Joining R37 offers the dynamic energy of a startup, backed by solid revenue, clear business value, and strong investment support. 

As an AI Engineer II in R37, you will contribute to AI-driven solutions that support business outcomes while developing your technical expertise. You will work on AI systems for unstructured data problems in healthcare, implement models under guidance from senior team members, and help build systems that measure AI performance."""

# Bad summary (with violations)
BAD_SUMMARY = """\\item AI Engineer with 6+ yrs building healthcare AI systems, leading cross-functional team solutions for R37
\\item Collaborated with business stakeholders to deploy production GenAI systems, reducing manual work by 40%
\\item Built AI-driven solutions for unstructured healthcare data using PyTorch and AWS, serving 95+ hospital systems
\\item Led team experience initiatives implementing ML pipelines that delivered \\$2M in cost savings annually"""

print("=" * 80)
print("Testing JD Analyzer with R37 Job Description")
print("=" * 80)

# Test JD Analysis
analyzer = JDAnalyzer()
metadata = analyzer.analyze(JD)

print("\n📋 JD Analysis Results:")
print(f"  Company Names: {metadata.company_names}")
print(f"  Role Level: {metadata.role_level}")
print(f"  Experience Min: {metadata.experience_years_min}")
print(f"  Experience Max: {metadata.experience_years_max}")
print(f"  Suggested Experience: {metadata.get_suggested_experience_years()}")
print(f"  Leadership Required: {metadata.leadership_required}")
print(f"  Leadership Guidance: {metadata.get_leadership_guidance()}")

# Create validation context
context = SummaryValidationContext(
    company_names=metadata.company_names,
    role_level=metadata.role_level,
    max_experience_years=metadata.experience_years_max,
    leadership_allowed=metadata.leadership_required
)

print("\n" + "=" * 80)
print("Testing Validation with BAD Summary (should catch violations)")
print("=" * 80)

# Test validation
validator = SummaryValidator()
result = validator.validate(BAD_SUMMARY, ["AI", "healthcare", "GenAI", "PyTorch"], context=context)

print(f"\n📊 Validation Results:")
print(f"  Passed: {result.passed}")
print(f"  Score: {result.score}/100")
print(f"  Keywords Matched: {result.keywords_matched}")

if result.errors:
    print(f"\n❌ Errors ({len(result.errors)}):")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print(f"\n⚠️  Warnings ({len(result.warnings)}):")
    for warning in result.warnings:
        print(f"  - {warning}")

print("\n" + "=" * 80)
print("Expected Violations:")
print("  1. Company name 'R37' in first bullet")
print("  2. Leadership verb 'leading' in first bullet (Mid-level role)")
print("  3. Leadership verb 'Led' in fourth bullet (Mid-level role)")
print("  4. Experience '6+ yrs' exceeds max for Mid-level role")
print("=" * 80)
