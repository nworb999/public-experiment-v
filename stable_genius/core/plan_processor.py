from typing import Dict, Any
import json

class PlanProcessor:
    """Processes planning responses from LLMs into structured plan data"""
    
    def __init__(self, personality: str = "neutral"):
        """
        Initialize the plan processor
        
        Args:
            personality: Personality trait to influence default behaviors
        """
        self.personality = personality
    
    def process(self, raw_response: str) -> Dict[str, Any]:
        """Process a planning response into a structured plan"""
        # Check if this is an error response
        if raw_response.startswith("Error:"):
            print(f"Planning error encountered: {raw_response}")
            # Return a default plan if there's an error
            return {
                "goal": self._default_goal(),
                "tactic": self._default_tactic()
            }
            
        try:
            # Extract JSON from response
            # First try parsing directly
            try:
                plan = json.loads(raw_response)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start = raw_response.find('{')
                end = raw_response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = raw_response[start:end]
                    try:
                        plan = json.loads(json_str)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON from response: {raw_response}")
                        plan = {
                            "goal": self._default_goal(),
                            "tactic": self._default_tactic()
                        }
                else:
                    # Fallback to default plan
                    print(f"No JSON found in response: {raw_response}")
                    plan = {
                        "goal": self._default_goal(),
                        "tactic": self._default_tactic()
                    }
            
            # Validate required fields
            if "goal" not in plan:
                plan["goal"] = self._default_goal()
            if "tactic" not in plan:
                plan["tactic"] = self._default_tactic()
                
            return plan
            
        except Exception as e:
            print(f"Error processing plan: {str(e)}")
            # Fallback to default plan
            return {
                "goal": self._default_goal(), 
                "tactic": self._default_tactic()
            }
    
    def _default_goal(self) -> str:
        """Return a default goal based on personality"""
        if "friendly" in self.personality:
            return "build rapport"
        elif "analytical" in self.personality:
            return "gather information"
        else:
            return "maintain conversation"
            
    def _default_tactic(self) -> str:
        """Return a default tactic based on personality"""
        if "friendly" in self.personality:
            return "friendly conversation"
        elif "analytical" in self.personality:
            return "ask targeted questions"
        else:
            return "balanced dialogue" 