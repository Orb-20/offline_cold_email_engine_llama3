import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def call_ollama(prompt, temperature=0.3):
    try:
        response = requests.post(
            OLLAMA_URL, 
            json={
                "model": "llama3", 
                "prompt": prompt, 
                "stream": False,
                "options": {"temperature": temperature, "num_ctx": 4096}
            }, 
            timeout=60
        )
        return response.json().get("response", "")
    except Exception as e:
        return f"ERROR: {e}"

def clean_json(text):
    if not text: return {}
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try: return json.loads(match.group(0))
        except: pass
    return {}

def generate_outreach_sequence(analysis_json, user_notes, objective, user_resume):
    """
    Generates professional emails using strict templates.
    """
    identity = analysis_json.get("identity", {})
    # Fallback if specific fields are missing
    name = identity.get('full_name', 'there')
    role = identity.get('role', 'Professional')
    company = identity.get('company', 'your company')
    
    prompt = f"""
    You are a Senior Copywriter.
    
    ### TARGET DATA
    - Name: {name}
    - Role: {role}
    - Company: {company}
    - Observed Interests/Posts: {analysis_json.get('personal_interests', {}).get('recent_activity_summary', 'None')}
    
    ### MY CONTEXT
    - My Pitch: {user_notes}
    - My Resume Summary: {user_resume}
    
    ### INSTRUCTIONS
    Write a 3-step outreach sequence.
    
    **Step 1: Connection Request (Max 250 chars)**
    - Friendly, low friction. Mention specific observation if possible.
    
    **Step 2: Cold Email (The "Value" Framework)**
    - Subject: Short, Relevant (Max 4 words)
    - Opening: "I was researching {company} and noticed..." (Show you did homework)
    - Problem: Mention a likely challenge they face in {role}.
    - Solution: Briefly mention how my background ({user_resume}) solves it.
    - CTA: "Worth a brief chat?" (Soft ask)
    
    **Step 3: Follow-Up (The "Asset" Framework)**
    - "Hi {name}, just floating this to the top. I also thought you might find this interesting..."
    - Provide a quick value-add idea based on my pitch.
    
    ### OUTPUT JSON STRICTLY
    {{
      "step1_connection_request": "...",
      "step2_email_subject": "...",
      "step2_email_body": "...",
      "step3_followup_body": "..."
    }}
    """
    raw = call_ollama(prompt, temperature=0.4)
    res = clean_json(raw)
    
    # Fallback if JSON fails
    if not res:
        return {
            "step1_connection_request": "Hi [Name], I've been following your work at [Company]...",
            "step2_email_subject": "Quick question about [Company]",
            "step2_email_body": raw, # Dump raw text so you see what happened
            "step3_followup_body": "Just floating this to the top..."
        }
    return res

# Keep imports valid for other files
def optimize_profile(a, b): return {}
def generate_email(a, b, c): return "Legacy Mode"