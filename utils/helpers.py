import json

def extract_and_parse_json(text: str) -> dict:
    """
    Robustly extracts and parses a JSON object from text.
    Handles triple backticks, leading/trailing text, and missing close braces.
    """
    text_stripped = text.strip()
    
    # Try to find JSON inside triple backticks
    if "```" in text_stripped:
        parts = text_stripped.split("```")
        for part in parts:
            part_str = part.strip()
            if part_str.startswith("json"):
                part_str = part_str[4:].strip()
            if part_str.startswith("{") and part_str.endswith("}"):
                try:
                    return json.loads(part_str)
                except json.JSONDecodeError:
                    pass
            # Try to find substring with curly braces inside this part
            start = part_str.find("{")
            end = part_str.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(part_str[start:end+1])
                except json.JSONDecodeError:
                    pass

    # If no backticks or backticks split failed, search globally in the string
    start = text_stripped.find("{")
    end = text_stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text_stripped[start:end+1])
        except json.JSONDecodeError:
            pass

    # Fallback to direct json.loads
    return json.loads(text_stripped)
