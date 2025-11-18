import re

def extract_entities(user_input: str):
    """Mock NLP: extract simple entities from plain text."""
    entities = {}

    # Detect cancer types (very simplified for Week 1)
    for ctype in ["breast", "prostate", "lung", "colon", "leukemia"]:
        if ctype in user_input.lower():
            entities["cancer_type"] = ctype.capitalize()

    # Detect stage
    match = re.search(r"stage\s*(\d+)", user_input.lower())
    if match:
        entities["stage"] = f"Stage {match.group(1)}"

    # Detect location
    for loc in ["texas", "california", "new york", "florida"]:
        if loc in user_input.lower():
            entities["location"] = loc.capitalize()

    # Intent recognition (find trials vs FAQ)
    if "trial" in user_input.lower() or "study" in user_input.lower():
        entities["intent"] = "find_trials"
    else:
        entities["intent"] = "faq"

    return entities