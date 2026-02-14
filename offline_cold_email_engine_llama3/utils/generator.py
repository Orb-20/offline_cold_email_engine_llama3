import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

def call_ollama(prompt, temperature=0.4):
    """
    Sends request to Ollama with error printing.
    """
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": 4096}
    }
    try:
        print(f"⚡ Sending request to LLaMA3... (Temp: {temperature})")
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        text = response.json().get("response", "")
        print("✅ LLaMA3 Responded.")
        return text
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return f"ERROR: {str(e)}"

def clean_json(text):
    """
    Ultra-robust cleaner. Extracts JSON even if buried in text.
    If parsing fails, returns raw text in a fallback dictionary.
    """
    if not text or "ERROR" in text:
        return {}

    # 1. Try finding JSON block between brackets
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except:
            # Fix common LLaMA3 JSON errors (like trailing commas)
            try:
                json_str = re.sub(r',\s*}', '}', json_str) # Remove trailing comma
                return json.loads(json_str)
            except:
                pass

    # 2. Fallback: If not valid JSON, return raw text mapped to keys
    # This ensures you NEVER get empty boxes.
    print("⚠️ JSON Parsing failed, returning raw text fallback.")
    return {
        "step1_connection_request": "Could not parse specific section. See raw output below.",
        "step2_email_subject": "Draft Subject",
        "step2_email_body": text, # Dump everything here so user can see it
        "step3_followup_body": "See email body above."
    }

def generate_outreach_sequence(analysis_json, user_notes, objective, user_resume=None):
    identity = analysis_json.get("identity", {})
    psyche = analysis_json.get("psychological_profile", {})
    align = analysis_json.get("resume_alignment", {})
    
    prompt = f"""
    Act as a Career Strategist.
    Goal: {objective}
    Target: {identity.get('full_name')} ({identity.get('likely_current_role')})
    Psychology: {psyche.get('communication_style')}
    Context: {user_notes}
    Alignment: {align.get('alignment_strategy')}
    
    Create a 3-part outreach sequence.
    
    STRICT FORMAT REQUIREMENT:
    Return raw JSON only. No markdown formatting. No intro text.
    
    {{
      "step1_connection_request": "Connection note (max 300 chars)",
      "step2_email_subject": "Email Subject",
      "step2_email_body": "Main Email Body",
      "step3_followup_body": "Short Follow-up (3 days later)"
    }}
    """
    raw = call_ollama(prompt, temperature=0.5)
    return clean_json(raw)

def optimize_profile(user_resume, target_role_analysis):
    prompt = f"""
    Act as a LinkedIn Expert.
    Resume: {user_resume}
    Target Role: {target_role_analysis}
    
    Optimize my profile. Return raw JSON only.
    {{
      "optimized_headline": "New Headline",
      "about_section_rewrite": "New About Section",
      "skills_to_add": ["Skill 1", "Skill 2"]
    }}
    """
    raw = call_ollama(prompt, temperature=0.3)
    return clean_json(raw)

# Keep legacy for compatibility
def generate_email(analysis_json, user_notes, objective="General Outreach"):
    return call_ollama(f"Write a cold email for {objective}. Context: {user_notes}")