import re
import time
import random
from duckduckgo_search import DDGS

def extract_handle(url):
    if not url: return None
    match = re.search(r'linkedin\.com/in/([^/?&]+)', url)
    return match.group(1) if match else None

def clean_name(handle):
    if not handle: return "Unknown"
    # Remove hash/numbers often found in handles
    clean = re.sub(r'-[\da-f]+$', '', handle)
    clean = re.sub(r'-\d+$', '', clean)
    return clean.replace('-', ' ').title()

def perform_web_research(linkedin_url):
    """
    ROBUST ENGINE: Extracts data from Titles if body text is hidden.
    """
    handle = extract_handle(linkedin_url)
    if not handle:
        return {"error": "Invalid URL. Format: linkedin.com/in/username"}

    name_guess = clean_name(handle)
    print(f"🔎 TARGETING: {name_guess} ({handle})")

    data = {
        "name_from_url": name_guess,
        "linkedin_url": linkedin_url,
        "raw_snippets": [],
        "about_section": [],
        "experience_skills": [],
        "recent_posts": [],
        "derived_info": {"name": name_guess, "role": "Unknown", "company": "Unknown"}
    }

    try:
        with DDGS() as ddgs:
            # 1. DIRECT PROFILE SEARCH (The "Golden" Source)
            # We look for the main profile page result.
            q_main = f'site:linkedin.com/in/{handle}'
            hits = list(ddgs.text(q_main, max_results=2))
            
            if hits:
                # HIT! Parse the Title immediately.
                # Format is usually: "Name - Role - Company | LinkedIn"
                title = hits[0]['title']
                snippet = hits[0]['body']
                
                data["raw_snippets"].append(f"Main Profile Title: {title}")
                data["raw_snippets"].append(f"Main Profile Snippet: {snippet}")
                
                # Attempt Smart Extraction from Title
                parts = title.split(" - ")
                if len(parts) >= 2:
                    data["derived_info"]["name"] = parts[0].strip()
                    # Often the second part is role OR role at company
                    rest = parts[1].split("|")[0] 
                    data["derived_info"]["role"] = rest.strip()
                    
                    if " at " in rest:
                        role_parts = rest.split(" at ")
                        data["derived_info"]["role"] = role_parts[0].strip()
                        data["derived_info"]["company"] = role_parts[1].strip()
                    elif len(parts) > 2:
                        data["derived_info"]["company"] = parts[2].split("|")[0].strip()

            # 2. SATELLITE SEARCH (The "Context" Filler)
            # Search for the person + "bio" or "interview" to find non-LinkedIn data
            # This bypasses LinkedIn restrictions entirely.
            time.sleep(1)
            q_bio = f'"{name_guess}" bio OR interview OR "current role"'
            hits = list(ddgs.text(q_bio, max_results=3))
            for h in hits:
                # Filter out generic noise
                if "linkedin.com" not in h['href']:
                    data["experience_skills"].append(f"External Source: {h['body']}")
                    data["raw_snippets"].append(f"External: {h['title']} - {h['body']}")

            # 3. POSTS SEARCH (Activity)
            time.sleep(1)
            q_posts = f'site:linkedin.com/posts "{name_guess}"'
            hits = list(ddgs.text(q_posts, max_results=3))
            for h in hits:
                data["recent_posts"].append(h['body'])

    except Exception as e:
        return {"error": f"Search Error: {str(e)}"}

    # FAILSAFE: If we found absolutely nothing
    if not data["raw_snippets"]:
        return {"error": "Deep Search failed. The search engine blocked the query."}

    return data