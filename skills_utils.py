def detect_fields(text):
    """Detect skills / career fields from text"""
    lower_text = text.lower()
    field_map = {
        "Data Science": ["python","machine learning","tensorflow","keras","pandas","numpy","data"],
        "Web Development": ["html","css","javascript","react","django","flask"],
        "Android": ["android","kotlin","java","flutter"],
        "iOS": ["ios","swift","objective-c","xcode"],
        "UI/UX": ["figma","xd","photoshop","illustrator","ux","ui"]
    }
    detected = [f for f, keys in field_map.items() if any(k in lower_text for k in keys)]
    return detected
