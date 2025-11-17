import openai
from typing import Dict, Any

# Mock mode for demo; set MOCK=False for real API
MOCK = True
GROK_API_KEY = "xai-3rAfxYqtSY3M4HOYcWWYmwspn8wB56z5TUBuLFZOJE46NPkdoPIQRoCTNdQRHAv0fvYBWb8dE6DL2pOA" 
client = openai.OpenAI(base_url="https://api.x.ai/v1", api_key=GROK_API_KEY) if not MOCK else None

def qualify_lead(lead_data: Dict, user_criteria: str) -> Dict[str, Any]:
    prompt = f"""
    You are a top SDR qualifying leads for xAI sales. Ideal Customer Profile (ICP): {user_criteria}.
    Lead: Name={lead_data['name']}, Company={lead_data['company']}, Notes={lead_data.get('notes', '')}.
    
    Step 1: Analyze fit (pain points, budget, authority, need, timeline - BANT framework).
    Step 2: Score 0-100 (100=perfect fit). Explain briefly.
    Step 3: Suggest next action (e.g., 'email outreach').
    
    Respond as JSON: {{"score": int, "explanation": str, "next_action": str}}
    """
    
    if MOCK:
        # Mock response based on simple heuristic (for demo)
        score = min(100, 50 + len(lead_data.get('notes', '')) * 2)  # Placeholder
        return {
            "score": score,
            "explanation": f"Strong fit for {lead_data['company']} based on {user_criteria}. Matches ICP well.",
            "next_action": "Send personalized email"
        }
    else:
        response = client.chat.completions.create(
            model="grok-beta",  # Or latest; check x.ai/api docs
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        # Parse JSON from response
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"score": 50, "explanation": "Parse error - fallback", "next_action": "Review manually"}

def generate_message(lead_data: Dict, next_action: str) -> str:
    prompt = f"""
    Craft a personalized cold email for SDR outreach to {lead_data['name']} at {lead_data['company']}.
    Context: {lead_data.get('notes', '')}. Action: {next_action}.
    Keep it concise (5-7 sentences), value-first, call-to-action for 15-min call.
    Sign off as: Alex from xAI Sales.
    """
    
    if MOCK:
        return f"Subject: Unlocking AI for {lead_data['company']}\n\nHi {lead_data['name']},\nSaw {lead_data['company']} is innovating in [industry]—Grok can supercharge your sales pipeline.\nLet's chat 15 mins?\nBest, Alex @ xAI"
    else:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()