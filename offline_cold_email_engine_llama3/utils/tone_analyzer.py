import re

# Dictionaries for analysis
TECH_KEYWORDS = {
    "python", "react", "node", "aws", "docker", "kubernetes", "java", "go", 
    "rust", "typescript", "javascript", "vue", "angular", "django", "flask", 
    "fastapi", "terraform", "azure", "gcp", "android", "ios", "swift"
}

SENIORITY_PATTERNS = {
    "founder": ["founder", "co-founder", "owner", "ceo", "cto", "cmo", "coo"],
    "senior": ["vp", "director", "head", "lead", "principal", "manager", "chief"],
    "junior": ["intern", "associate", "junior", "analyst", "trainee", "entry"]
}

HINGLISH_SLANG = {
    "bhai", "matlab", "karna", "hai", "kaise", "mast", "theek", "yaar", 
    "chalo", "jugaad", "achha", "na", "hoga"
}

SLANG_WORDS = {
    "lol", "lmao", "gonna", "wanna", "kinda", "gotcha", "ya", "lit", "fire", "fam"
}

def analyze_profile(role, profile_text):
    """
    Deep Persona Builder: Analyzes role and text for seniority, intent, and tech stack.
    """
    # Defensive check for None inputs
    role = role.lower() if role else ""
    text = profile_text.lower() if profile_text else ""
    
    # 1. Seniority & Decision Maker Score
    seniority = "Unknown"
    dm_score = 0.3  # Base probability
    
    if any(k in role for k in SENIORITY_PATTERNS["founder"]):
        seniority = "Founder / C-Level"
        dm_score = 0.95
    elif any(k in role for k in SENIORITY_PATTERNS["senior"]):
        seniority = "Senior / Leadership"
        dm_score = 0.75
    elif any(k in role for k in SENIORITY_PATTERNS["junior"]):
        seniority = "Junior / Individual Contributor"
        dm_score = 0.1
    else:
        seniority = "Mid-Level / Professional"
        dm_score = 0.4
        
    # 2. Tech Stack Inference
    detected_tech = {word for word in TECH_KEYWORDS if word in text}
    
    # 3. Buying Intent Signals (Heuristic)
    intent_signals = []
    if any(w in text for w in ["hiring", "growing", "scale", "expanding"]):
        intent_signals.append("Growth Phase")
    if any(w in text for w in ["problem", "challenge", "need", "looking for"]):
        intent_signals.append("Active Pain Point")
    if any(w in text for w in ["series a", "series b", "funding", "raised"]):
        intent_signals.append("Recently Funded")
        
    return {
        "seniority": seniority,
        "dm_score": round(dm_score * 100),
        "tech_stack": list(detected_tech),
        "intent": intent_signals
    }

def analyze_communication_dna(text):
    """
    Communication DNA Analyzer: Scans for emojis, sentence structure, and slang.
    """
    if not text:
        # Default Safe Return
        return {
            "tone": "Professional",
            "humor": "None",
            "emoji_freq": "None",
            "formality": 80,
            "slang_detected": False,
            "hinglish": False,
            "avg_sentence_len": 0
        }
        
    # 1. Emoji Analysis
    emoji_pattern = re.compile(r'[^\w\s,.\'"?!@#%&()\-:;/]')
    emojis = emoji_pattern.findall(text)
    emoji_count = len(emojis)
    
    # 2. Sentence Analysis
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    # 3. Slang & Hinglish
    words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    detected_hinglish = words.intersection(HINGLISH_SLANG)
    detected_slang = words.intersection(SLANG_WORDS)
    
    # 4. Formality Score Calculation (0-100)
    formality = 100
    formality -= (emoji_count * 5)
    formality -= (len(detected_slang) * 10)
    formality -= (len(detected_hinglish) * 10)
    if avg_len < 10: formality -= 10
    formality = max(0, min(100, formality))
    
    # 5. Tone Categorization
    tone = "Professional"
    if formality < 40:
        tone = "Casual / Direct"
    elif formality < 70:
        tone = "Conversational"
        
    # 6. Humor Detection
    humor = "Low"
    if "lol" in words or "haha" in words or emoji_count > 3:
        humor = "High"
    elif emoji_count > 0:
        humor = "Medium"

    return {
        "tone": tone,
        "humor": humor,
        "emoji_freq": "High" if emoji_count > 2 else "Low" if emoji_count > 0 else "None",
        "formality": formality,
        "slang_detected": bool(detected_slang or detected_hinglish),
        "hinglish": bool(detected_hinglish),
        "avg_sentence_len": round(avg_len, 1)
    }