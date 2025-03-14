import json
from typing import Dict, Any, Optional

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text if present"""
    try:
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = text[json_start:json_end]
            return json.loads(json_str)
    except (json.JSONDecodeError, KeyError, IndexError, ValueError):
        pass
    return None

def process_generic_response(raw_response: str) -> Dict[str, Any]:
    """Process generic (non-specific) responses"""
    # Try to extract JSON first
    parsed_response = extract_json_from_text(raw_response)
    if parsed_response and isinstance(parsed_response, dict):
        return parsed_response
        
    # For non-JSON responses, wrap in a simple structure
    return {
        "content": raw_response
    }

def create_error_response(message: str) -> Dict[str, Any]:
    """Create standard error response"""
    return {
        "action": "say",
        "speech": message
    }
