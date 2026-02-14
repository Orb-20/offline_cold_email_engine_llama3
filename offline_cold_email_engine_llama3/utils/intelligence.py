import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def clean_json_response(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try: return json.loads(match.group(0))
        except: pass
    return {}

def analyze_web_data(research_data, objective, user_resume=None):
    # Combine all data sources
    derived = research_data.get("derived_info", {})
    snippets = "\n".join(research_data.get("raw_snippets", []))
    posts = "\n".join(research_data.get("recent_posts", []))
    ext_sources = "\n".join(research_data.get("experience_skills", []))
    
    # Construct a rich prompt
    full_text = f"""
    DERIVED FROM TITLE: 
    Name: {derived.get('name')}
    Role: {derived.get('role')}
    Company: {derived.get('company')}
    
    SEARCH SNIPPETS:
    {snippets}
    
    EXTERNAL SOURCES:
    {ext_sources}
    
    RECENT ACTIVITY:
    {posts}
    """
    
    resume_block = f"USER RESUME:\n{user_resume}\n" if user_resume else "No resume provided."

    prompt = f"""
    Act as a Senior Recruiter Intelligence Analyst.
    GOAL: {objective}
    
    ### DATA SOURCE
    {full_text}
    {resume_block}
    
    ### INSTRUCTIONS
    1. **Identity:** prioritize the 'DERIVED FROM TITLE' data.
    2. **Hiring Intelligence:** Infer from company name (e.g. if 'Startup', likely high growth).
    3. **Psychology:** If no posts, assume 'Professional' tone.
    4. **Alignment:** Map User Resume to the inferred Role.
    
    ### OUTPUT JSON (Strict)
    {{
      "identity": {{
        "full_name": "{derived.get('name')}",
        "role": "{derived.get('role')}",
        "company": "{derived.get('company')}",
        "location": "Inferred from snippets or Unknown"
      }},
      "recruiter_intelligence": {{
        "hiring_status": "Active | Passive | Unknown",
        "activity_score": 0,
        "company_growth_signals": ["Signal 1"],
        "hiring_focus": "..."
      }},
      "psychological_profile": {{
        "communication_style": "Analytical | Driver | Amiable | Expressive",
        "tone_preference": "Direct | Casual | Formal",
        "motivations": "..."
      }},
      "resume_alignment": {{
        "match_score": 0,
        "key_matches": [],
        "alignment_strategy": "..."
      }},
      "strategic_advice": {{
        "response_probability": 0,
        "recommended_approach": "..."
      }}
    }}
    """
    
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": "llama3", "prompt": prompt, "stream": False, "options": {"num_ctx": 4096}
        }, timeout=90)
        return clean_json_response(res.json().get("response", ""))
    except Exception as e:
        return {"error": str(e)}

def analyze_prospect(p, r, c):
    return analyze_web_data({"raw_snippets": [p], "recent_posts": [r], "experience_skills": [c]}, "Manual")