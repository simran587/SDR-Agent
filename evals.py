import pytest
from grok_client import qualify_lead

SAMPLE_LEADS = [
    {"name": "Jane Smith", "company": "AI Startup", "notes": "Interested in Grok API for sales automation."},
    {"name": "Bob Lee", "company": "Legacy Corp", "notes": "No AI budget mentioned."}
]
ICP = "Tech companies with >50 employees seeking AI sales tools."

def test_qualification_accuracy():
    results = [qualify_lead(lead, ICP) for lead in SAMPLE_LEADS]
    assert all(r['score'] >= 0 and r['score'] <= 100 for r in results), "Scores out of range"
    # Qualitative: Check for BANT keywords
    explanations = [r['explanation'].lower() for r in results]
    assert any(word in exp for exp in explanations for word in ['budget', 'authority', 'need', 'timeline']), "Missing BANT analysis"

def test_consistency():
    # Run 3x on same lead, check variance <20
    lead = SAMPLE_LEADS[0]
    scores = [qualify_lead(lead, ICP)['score'] for _ in range(3)]
    assert max(scores) - min(scores) < 20, "High variance - tune temperature"

# Run with: pytest evals.py -v
# Actionable Recs: If fails, iterate prompt (e.g., add "Be consistent"). Log underperformers: Low-score edge cases like vague notes.