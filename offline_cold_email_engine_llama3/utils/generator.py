
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_email(name, role, company, industry, tone, notes):

    prompt = f"""
You are an elite cold email strategist.

Write a highly personalized cold email.

Prospect Details:
Name: {name}
Role: {role}
Company: {company}
Industry: {industry}
Extra Notes: {notes}

Tone: {tone}

Requirements:
- Strong personalized opening
- Mention their role and company
- Natural human tone
- Clear CTA for 15-min call
- Under 150 words
- Add compelling subject line
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]
