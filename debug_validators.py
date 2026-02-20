"""Debug script to test Pydantic validators directly."""

from validators.summary_validator import SummaryBullet, SummaryValidationContext
from pydantic import ValidationError

# Create context
context = SummaryValidationContext(
    company_names=["R37", "R1"],
    role_level="Mid",
    max_experience_years=5,
    leadership_allowed=False
)

# Test bullets with violations
test_bullets = [
    ("AI Engineer with 6+ yrs building healthcare AI systems, leading cross-functional team solutions for R37", 
     ["company name R37", "leadership verb 'leading'", "experience 6+ yrs exceeds max 5"]),
    ("Led team experience initiatives implementing ML pipelines", 
     ["leadership verb 'Led'"]),
    ("Collaborated with stakeholders to deploy systems",
     ["should pass - no violations"]),
]

print("=" * 80)
print("Testing Pydantic Field Validators Directly")
print("=" * 80)

for bullet_text, expected_violations in test_bullets:
    print(f"\n📝 Testing: {bullet_text[:60]}...")
    print(f"   Expected: {', '.join(expected_violations)}")
    
    try:
        result = SummaryBullet(content=bullet_text, context=context)
        print(f"   ✅ PASSED (no validation errors)")
    except ValidationError as e:
        print(f"   ❌ FAILED with validation errors:")
        for error in e.errors():
            print(f"      - {error.get('msg', str(error))}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {type(e).__name__}: {str(e)}")

print("\n" + "=" * 80)
