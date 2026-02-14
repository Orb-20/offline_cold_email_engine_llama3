import re
import time
import random
from duckduckgo_search import DDGS

def extract_linkedin_handle(url):
    if not url: return None
    match = re.search(r'linkedin\.com/in/([^/?&]+)', url)
    return match.group(1) if match else None

def clean_name_from_handle(handle):
    if not handle: return "Unknown Prospect"
    clean = re.sub(r'-\d+$', '', handle)
    return clean.replace('-', ' ').title()

# Feature 10: Rate Limiting
def random_delay():
    time.sleep(random.uniform(1.0, 2.5))

def perform_web_research(linkedin_url):
    handle = extract_linkedin_handle(linkedin_url)
    if not handle:
        return {"error": "Invalid LinkedIn URL"}

    name_guess = clean_name_from_handle(handle)
    
    results = {
        "linkedin_url": linkedin_url,
        "name_from_url": name_guess,
        "google_snippets": [],
        "company_website_text": [],
        "additional_public_text": [],
        "company_hiring_intel": [] # Feature 6
    }
    
    print(f"🔎 Researching: {name_guess}...")

    try:
        with DDGS() as ddgs:
            # 1. Profile
            random_delay()
            hits = list(ddgs.text(f'site:linkedin.com/in/ "{handle}"', max_results=2))
            for h in hits: results["google_snippets"].append(f"{h['title']}\n{h['body']}")

            # 2. Context
            random_delay()
            hits = list(ddgs.text(f'"{name_guess}" LinkedIn', max_results=2))
            for h in hits: results["google_snippets"].append(f"{h['title']}\n{h['body']}")
            
            # 3. Posts/Activity (Feature 2)
            random_delay()
            hits = list(ddgs.text(f'site:linkedin.com/posts/ "{name_guess}"', max_results=3))
            for h in hits: results["additional_public_text"].append(f"Post: {h['body']}")

            # 4. Company Hiring Intel (Feature 6)
            random_delay()
            hits = list(ddgs.text(f'"{name_guess}" company hiring OR funding OR growth', max_results=2))
            for h in hits: results["company_hiring_intel"].append(f"Intel: {h['body']}")

    except Exception as e:
        return {"error": f"Search Error: {str(e)}"}

    return results