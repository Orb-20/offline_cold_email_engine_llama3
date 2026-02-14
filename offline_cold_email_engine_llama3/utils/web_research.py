import re
from duckduckgo_search import DDGS

def extract_linkedin_handle(url):
    """
    Extracts the handle/username from a LinkedIn URL.
    e.g., https://www.linkedin.com/in/satya-nadella-123/ -> satya-nadella-123
    """
    if not url:
        return None
    match = re.search(r'linkedin\.com/in/([^/?&]+)', url)
    return match.group(1) if match else None

def clean_name_from_handle(handle):
    """
    Converts 'john-doe-123' to 'John Doe'.
    """
    if not handle:
        return "Unknown Prospect"
    # Remove trailing numbers often added by LinkedIn
    clean = re.sub(r'-\d+$', '', handle)
    # Replace dashes with spaces and title case
    return clean.replace('-', ' ').title()

def perform_web_research(linkedin_url):
    """
    Orchestrates the deep web search pipeline:
    1. Extract Identity
    2. Search for Profile + Company
    3. Search for Interviews/Activity
    """
    handle = extract_linkedin_handle(linkedin_url)
    if not handle:
        return {"error": "Invalid LinkedIn URL format"}

    name_guess = clean_name_from_handle(handle)
    
    # Initialize searcher
    results = {
        "linkedin_url": linkedin_url,
        "name_from_url": name_guess,
        "google_snippets": [],
        "company_website_text": [],
        "additional_public_text": []
    }
    
    print(f"🔎 Researching: {name_guess}...")

    try:
        with DDGS() as ddgs:
            # Search 1: The Profile (to confirm Title/Company)
            # We search the handle explicitly to get the LinkedIn snippet
            profile_query = f'site:linkedin.com/in/ "{handle}"'
            profile_hits = list(ddgs.text(profile_query, max_results=2))
            
            for hit in profile_hits:
                results["google_snippets"].append(f"Title: {hit['title']}\nSnippet: {hit['body']}")

            # Search 2: Broader Context (Name + "LinkedIn" to catch slightly different indexing)
            context_query = f'"{name_guess}" LinkedIn'
            context_hits = list(ddgs.text(context_query, max_results=2))
            
            for hit in context_hits:
                 # Avoid duplicates
                if hit['title'] not in [h['title'] for h in profile_hits]:
                    results["google_snippets"].append(f"Source: {hit['title']}\nInfo: {hit['body']}")

            # Search 3: Interviews / Content (Buying Signals & Tone)
            # We assume the name is unique enough or combined with "interview"
            content_query = f'"{name_guess}" interview OR podcast OR "guest post"'
            content_hits = list(ddgs.text(content_query, max_results=3))
            
            for hit in content_hits:
                results["additional_public_text"].append(f"Type: Content\nTitle: {hit['title']}\nExcerpt: {hit['body']}")

            # Search 4: Company Info (Heuristic: Try to find company name in previous snippets)
            # This is a 'best effort' recursive find. 
            # For this version, we'll do a generic "Company" search if we found a likely company name in snippets?
            # To keep it fast/robust, we will just search the Name + "Company" 
            company_query = f'"{name_guess}" current company'
            company_hits = list(ddgs.text(company_query, max_results=2))
            for hit in company_hits:
                 results["company_website_text"].append(f"Potential Company Info: {hit['body']}")

    except Exception as e:
        return {"error": f"Search Engine Error: {str(e)}"}

    return results