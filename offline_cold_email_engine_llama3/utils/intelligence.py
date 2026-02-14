import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def clean_json_response(response_text):
    """Extracts valid JSON from the LLM's raw response."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None

def analyze_web_data(research_data, objective):
    """
    Analyzes web data with a specific User Objective.
    Accepts: research_data (dict) AND objective (str).
    """
    
    snippets = "\n".join(research_data.get("google_snippets", []))
    company_text = "\n".join(research_data.get("company_website_text", []))
    public_text = "\n".join(research_data.get("additional_public_text", []))
    
    # Customize prompt based on the user's selected goal
    objective_instructions = "Focus on general professional fit."
    
    if "Job" in objective or "Internship" in objective:
        objective_instructions = "Focus on: Hiring authority, team culture, recent growth, tech stack overlap. 'Decision Maker Score' is their ability to hire me."
    elif "Clients" in objective:
        objective_instructions = "Focus on: Pain points, budget authority, business scaling needs. 'Decision Maker Score' is their ability to buy services."
    elif "Investors" in objective:
        objective_instructions = "Focus on: Investment thesis, recent fund activity, portfolio fit. 'Decision Maker Score' is likelihood to invest."
    elif "Referrals" in objective:
        objective_instructions = "Focus on: Shared connections, alumni status, willingness to mentor. 'Decision Maker Score' is likelihood to reply."
    elif "Recruiters" in objective:
         objective_instructions = "Focus on: Their active open roles, their recruiting niche (tech/sales/exec). 'Decision Maker Score' is relevance to my placement."
    
    prompt = f"""
You are an expert strategic analyst.
USER GOAL: {objective}

Analyze the target person specifically to help the user achieve this goal.
{objective_instructions}

---------------------------------------
INPUT DATA:
Name: {research_data.get('name_from_url')}
Web Snippets: {snippets}
Company Text: {company_text}
Public Mentions: {public_text}
---------------------------------------

Return ONLY valid JSON with this exact structure:

{{
  "identity": {{
    "full_name": "",
    "likely_current_role": "",
    "company": "",
    "industry": "",
    "location_if_known": "",
    "confidence": "Low | Medium | High"
  }},

  "professional_profile": {{
    "seniority_level": "Junior | Mid | Senior | Director | VP | Founder | Executive",
    "decision_maker_score_0_to_100": 0,
    "key_skills_and_expertise": [],
    "estimated_company_stage": "Early | Growth | Scale | Enterprise",
    "relevance_reasoning": "Why are they good for the specific USER GOAL?"
  }},

  "personal_interests": {{
    "topics_discussed_recently": [],
    "hobbies_or_passions": [],
    "recent_activity_summary": "One sentence on what they are posting about or doing recently (e.g. 'Speaking at AI conferences' or 'Hiring React devs')."
  }},

  "communication_analysis": {{
    "formality_score_0_to_100": 0,
    "tone_style": "Corporate | Startup | Technical | Casual | Mixed",
    "confidence": "Low | Medium | High"
  }},

  "behavioral_intelligence": {{
    "archetype": "Visionary | Analytical Thinker | Growth Hacker | Corporate Leader | Technical Builder | Operator"
  }},

  "buying_intent_signals": {{
    "intent_level": "Low | Medium | High",
    "signals_detected": [],
    "reasoning": "Signals related to USER GOAL"
  }},

  "outreach_strategy": {{
    "recommended_tone": "",
    "opening_hook_type": "Curiosity | Pain-Point | Social Proof | Direct Value | Shared Mission | Flattery",
    "cta_style": "Soft Ask | Direct Ask | Question-Based | Calendar Link",
    "personalization_angles": [],
    "psychological_triggers": []
  }}
}}
"""

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        return clean_json_response(response.json().get("response", ""))
    except Exception as e:
        return {"error": str(e)}

def analyze_prospect(profile_text, recent_posts, company_text):
    """Legacy helper for manual input tab."""
    prompt = f"""
    Analyze this prospect for general outreach.
    Profile: {profile_text}
    Posts: {recent_posts}
    Company: {company_text}
    Return the standard JSON structure.
    """
    payload = { "model": "llama3", "prompt": prompt, "stream": False }
    try:
        r = requests.post(OLLAMA_URL, json=payload)
        return clean_json_response(r.json().get("response", ""))
    except:
        return {"error": "Manual analysis failed"}