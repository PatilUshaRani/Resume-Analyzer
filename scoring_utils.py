def calculate_resume_score(text):
    """Calculate résumé score based on presence of key sections"""
    lower_text = text.lower()
    score = 0
    tips = []
    for section in ["Objective","Projects","Experience","Skills","Education"]:
        if section.lower() in lower_text:
            score += 20
        else:
            tips.append(f"Add a **{section}** section.")
    return score, tips
