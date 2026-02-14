import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def clean_json_response(response_text):
    try:
        return json.loads(response_text)
    except:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except: pass
    return {"error": "JSON Parsing Failed", "raw": response_text}

def analyze_web_data(research_data, objective, user_resume=None):
    """
    Master Intelligence Engine (Features 1, 2, 3, 5, 6, 7, 9, 14)
    """
    snippets = "\n".join(research_data.get("google_snippets", []))
    company_intel = "\n".join(research_data.get("company_hiring_intel", []))
    posts = "\n".join(research_data.get("additional_public_text", []))
    
    resume_block = f"USER RESUME:\n{user_resume}\n" if user_resume else "No resume provided."

    prompt = f"""
    You are 'Recruiter Intelligence OS'. 
    USER GOAL: {objective}
    
    ### INPUT DATA
    - Name: {research_data.get('name_from_url')}
    - Web Snippets: {snippets}
    - Company Hiring Signals: {company_intel}
    - Recent Posts: {posts}
    - {resume_block}
    
    ### ANALYSIS TASKS
    1. **Identity:** Extract basics.
    2. **Hiring Intelligence:** Is the company growing? Are they hiring? (Score 0-100).
    3. **Psychology:** Analyze tone (DiSC profile).
    4. **Alignment:** Match User Resume vs. Target Needs.
    5. **Strategy:** Predict response probability.

    ### OUTPUT FORMAT (Strict JSON)
    {{
      "identity": {{
        "full_name": "...",
        "likely_current_role": "...",
        "company": "...",
        "location": "..."
      }},
      "recruiter_intelligence": {{
        "hiring_status": "Active Hiring | Passive | Networking",
        "activity_score": 50,
        "company_growth_signals": ["Series A", "Layoffs", "Stable"],
        "hiring_focus": "..."
      }},
      "psychological_profile": {{
        "communication_style": "Analytical | Driver | Expressive | Amiable",
        "tone_preference": "Direct | Casual | Formal",
        "motivations": "..."
      }},
      "resume_alignment": {{
        "match_score": 0,
        "key_matches": [],
        "missing_skills": [],
        "alignment_strategy": "..."
      }},
      "strategic_advice": {{
        "response_probability": 0,
        "recommended_approach": "..."
      }}
    }}
    """
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 4096}
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        return clean_json_response(response.json().get("response", ""))
    except Exception as e:
        return {"error": str(e)}

# Legacy Wrapper
def analyze_prospect(profile_text, recent_posts, company_text):
    return analyze_web_data({
        "name_from_url": "Manual Entry",
        "google_snippets": [profile_text],
        "company_hiring_intel": [company_text],
        "additional_public_text": [recent_posts]
    }, "General Networking")