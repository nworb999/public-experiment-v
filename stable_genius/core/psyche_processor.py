from typing import Dict, Any, List
from stable_genius.utils.response_processor import extract_json_from_text

def process_planning_response(raw_response: str, personality: str = "neutral", psyche=None) -> Dict[str, Any]:
    """Process response for planning prompts"""
    # Try to extract JSON
    parsed_result = extract_json_from_text(raw_response)
    
    # If successful, ensure required keys exist
    if parsed_result:
        # Do NOT fall back to default goals - preserve existing or set to None
        if 'goal' not in parsed_result:
            existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
            if existing_goal:
                parsed_result['goal'] = existing_goal
                print(f"LLM did not provide goal, keeping existing: {existing_goal}")
            else:
                print("LLM did not provide goal and no existing goal found - goal will be None")
                parsed_result['goal'] = None
        
        if "plan" not in parsed_result:
            parsed_result["plan"] = default_plan(personality)
        elif not isinstance(parsed_result["plan"], list):
            # If plan exists but is not a list, convert it
            parsed_result["plan"] = [parsed_result["plan"]]
            
        # Set active_tactic if missing
        if "active_tactic" not in parsed_result and parsed_result["plan"]:
            parsed_result["active_tactic"] = parsed_result["plan"][0]
            
        return parsed_result
        
    # If parsing fails, return response preserving existing goal
    existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
    default_tactics = default_plan(personality)
    return {
        "goal": existing_goal,
        "plan": default_tactics,
        "active_tactic": default_tactics[0] if default_tactics else None
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
        if "conversation_summary" not in parsed_response:
            parsed_response["conversation_summary"] = "No summary provided."
        return parsed_response
            
    # Fallback to constructing a response
    return {
        "action": "say",
        "speech": raw_response,
        "conversation_summary": "Processing the conversation."
    }

def default_goal(personality: str) -> str:
    """Return a default goal based on personality"""
    if "friendly" in personality:
        return "build rapport"
    elif "analytical" in personality:
        return "gather information"
    else:
        return "maintain conversation"
        
def default_plan(personality: str) -> List[str]:
    """Return a default plan based on personality"""
    if "friendly" in personality:
        return ["friendly conversation", "show empathy"]
    elif "analytical" in personality:
        return ["ask targeted questions", "analyze responses"]
    else:
        return ["balanced dialogue"] 