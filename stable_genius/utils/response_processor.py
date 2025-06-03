import json
from typing import Dict, Any, Optional
import re

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from text if present, with basic repair for unterminated strings."""
    try:
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = text[json_start:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                # Try to repair unterminated string by truncating at the last valid quote or brace
                # Remove any trailing incomplete string
                # This is a best-effort fix for common LLM errors
                # Remove any trailing comma
                json_str = re.sub(r',\s*}$', '}', json_str)
                # Remove any unterminated string at the end
                last_quote = json_str.rfind('"')
                last_brace = json_str.rfind('}')
                if last_brace > last_quote:
                    json_str = json_str[:last_brace+1]
                else:
                    json_str = json_str[:last_quote]
                try:
                    return json.loads(json_str)
                except Exception:
                    pass
    except (json.JSONDecodeError, KeyError, IndexError, ValueError):
        pass
    return None

def process_llm_response_for_json(raw_response: str, fallback_message: str = None) -> Dict[str, Any]:
    """Process LLM response, robustly extracting JSON or returning a standard error response."""
    parsed_response = extract_json_from_text(raw_response)
    if parsed_response and isinstance(parsed_response, dict):
        return parsed_response
    # If not valid JSON, return a standard error response
    return {
        "error": "Failed to parse JSON from LLM response.",
        "raw_response": raw_response,
        "speech": fallback_message or "Sorry, I couldn't process that response."
    }

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
