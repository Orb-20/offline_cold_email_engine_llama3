
def detect_tone(text):
    text = text.lower()
    if any(word in text for word in ["!", "😊", "🔥", "awesome", "excited"]):
        return "Casual"
    elif any(word in text for word in ["regards", "sincerely", "professional"]):
        return "Professional"
    return "Friendly"
