import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_email(analysis_json, user_notes, objective="General Outreach"):
    """
    Generates an email tailored to the specific User Objective.
    CRITICAL: Accepts 'objective' to switch personas (Candidate vs Sales vs Founder).
    """
    
    basics = analysis_json.get("basic_info", {})
    dna = analysis_json.get("communication_dna", {})
    strategy = analysis_json.get("outreach_strategy", {})
    traits = analysis_json.get("behavioral_traits", {})
    
    # DYNAMIC PERSONA SWITCHING
    sender_persona = "Professional"
    context_instruction = "Write a standard business email."
    
    if "Job" in objective or "Internship" in objective:
        sender_persona = "Ambitious, skilled candidate"
        context_instruction = "Frame the email as a high-value job application or networking request. Focus on how I can solve their problems. NOT a desperate plea."
    elif "Clients" in objective:
        sender_persona = "Expert Consultant / Agency Owner"
        context_instruction = "Frame the email as a B2B sales outreach. Focus on ROI, case studies, and solving pain points."
    elif "Investors" in objective:
        sender_persona = "Visionary Founder"
        context_instruction = "Frame the email as a deal flow opportunity. Focus on traction, market size, and FOMO."
    elif "Referrals" in objective:
        sender_persona = "Industry Peer / Aspiring Professional"
        context_instruction = "Frame the email as a request for advice or a virtual coffee. Be respectful of their time. Flattery works here."
    elif "Recruiters" in objective:
        sender_persona = "Top Talent Candidate"
        context_instruction = "Frame the email as a brief introduction to a headhunter. Highlight specific skills and availability."

    prompt = f"""
You are an expert copywriter acting as: {sender_persona}.
Goal: {objective}

Write a cold email to {basics.get('full_name', 'the prospect')} based on this analysis.

### STRATEGY BLUEPRINT
- **Target Archetype:** {traits.get('archetype', 'Professional')}
- **Tone:** {strategy.get('recommended_tone', 'Professional')}
- **Hook:** {strategy.get('opening_hook_type', 'Direct Value')}
- **CTA:** {strategy.get('cta_style', 'Direct Ask')}

### COMMUNICATION DNA (Mimic their style)
- **Formality:** {dna.get('formality_score_0_to_100', 50)}/100
- **Style:** {dna.get('tone_style', 'Professional')}

### CONTEXT
- **My Context/Pitch:** {user_notes}
- **Detected Signals:** {', '.join(analysis_json.get('buying_intent_signals', {}).get('signals_detected', []))}

### INSTRUCTIONS
1. {context_instruction}
2. Keep it under 150 words.
3. Use the specific CTA defined above.
4. Do NOT use generic openings like "I hope this email finds you well."

Output ONLY the email body and subject line.
"""

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=45)
        response.raise_for_status()
        return response.json().get("response", "Error: No response generated.")
    
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except Exception as e:
        return f"ERROR: {str(e)}"