from typing import Dict, Any
from stable_genius.utils.response_processor import extract_json_from_text

def process_planning_response(raw_response: str, personality: str = "neutral") -> Dict[str, Any]:
    """Process response for planning prompts"""
    # Try to extract JSON
    parsed_result = extract_json_from_text(raw_response)
    
    # If successful, ensure required keys exist
    if parsed_result:
        if 'goal' not in parsed_result:
            parsed_result['goal'] = default_goal(personality)
        if 'tactic' not in parsed_result:
            parsed_result['tactic'] = default_tactic(personality)
        return parsed_result
        
    # If parsing fails, return default response
    return {
        "goal": default_goal(personality),
        "tactic": default_tactic(personality)
    }

def process_action_response(raw_response: str) -> Dict[str, Any]:
    """Process response for action prompts"""
    # Try to extract JSON
    parsed_response = extract_json_from_text(raw_response)
    
    # If successful, ensure required keys exist
    if parsed_response and isinstance(parsed_response, dict):
        if "action" not in parsed_response:
            parsed_response["action"] = "say"
        if "speech" not in parsed_response:
            parsed_response["speech"] = raw_response
        return parsed_response
            
    # Fallback to constructing a response
    return {
        "action": "say",
        "speech": raw_response
    }

def default_goal(personality: str) -> str:
    """Return a default goal based on personality"""
    if "friendly" in personality:
        return "build rapport"
    elif "analytical" in personality:
        return "gather information"
    else:
        return "maintain conversation"
        
def default_tactic(personality: str) -> str:
    """Return a default tactic based on personality"""
    if "friendly" in personality:
        return "friendly conversation"
    elif "analytical" in personality:
        return "ask targeted questions"
    else:
        return "balanced dialogue" 