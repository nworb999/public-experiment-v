import json
from typing import Dict, Any
from stable_genius.utils.logger import logger

class ActionProcessor:
    """Processes action responses from LLMs into structured action data"""
    
    def __init__(self):
        """Initialize the action processor"""
        pass
    
    def process(self, raw_response: str) -> Dict[str, Any]:
        """
        Process raw LLM response into structured action data
        
        Args:
            raw_response: Raw text response from the LLM
            
        Returns:
            Dictionary with 'action', 'speech' and 'conversation_summary' keys
        """
        # Check if this is an error response
        if raw_response.startswith("Error:"):
            logger.info(f"Action error encountered: {raw_response}")
            # Return a default action if there's an error
            return {
                "action": "say",
                "speech": f"I'm having trouble with my connection. {raw_response}",
                "conversation_summary": "There was an error in processing."
            }
            
        try:
            # Extract JSON from response
            # First try parsing directly
            try:
                action = json.loads(raw_response)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start = raw_response.find('{')
                end = raw_response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = raw_response[start:end]
                    try:
                        action = json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.info(f"Failed to parse JSON from action response: {raw_response}")
                        action = {
                            "action": "say",
                            "speech": "I'm having trouble understanding. Let's try again.",
                            "conversation_summary": "Having difficulties understanding the conversation."
                        }
                else:
                    # Fallback to default action
                    logger.info(f"No JSON found in action response: {raw_response}")
                    action = {
                        "action": "say",
                        "speech": "I'm not sure what to say right now.",
                        "conversation_summary": "Struggling to formulate a response."
                    }
            
            # Validate required fields
            if "action" not in action:
                action["action"] = "say"
            if "speech" not in action:
                action["speech"] = "I'm not sure what to say."
            if "conversation_summary" not in action:
                action["conversation_summary"] = "No summary provided."
                
            return action
            
        except Exception as e:
            logger.info(f"Error processing action: {str(e)}")
            # Fallback to default action
            return {
                "action": "say",
                "speech": f"I encountered an error in my thinking: {str(e)}",
                "conversation_summary": "Encountered an error in processing."
            } 