from typing import Dict, Any, List
import json
from stable_genius.utils.logger import logger

class PlanProcessor:
    """Processes planning responses from LLMs into structured plan data"""
    
    def __init__(self, personality: str = "neutral"):
        """
        Initialize the plan processor
        
        Args:
            personality: Personality trait to influence default behaviors
        """
        self.personality = personality
    
    def process(self, raw_response: str, has_plan: bool = False) -> Dict[str, Any]:
        """Process a planning response into a structured plan
        
        Args:
            raw_response: The raw response from the LLM
            has_plan: Whether the psyche already has a plan
        """
        # Check if this is an error response
        if raw_response.startswith("Error:"):
            logger.info(f"Planning error encountered: {raw_response}")
            if has_plan:
                # For tactic selection errors, return default active tactic
                return {"active_tactic": self._get_first_tactic_from_default_plan()}
            else:
                # For plan generation errors, return default plan
                plan = self._default_plan()
                return {
                    "goal": self._default_goal(),
                    "plan": plan,
                    "active_tactic": plan[0] if plan else None
                }
            
        try:
            # Extract JSON from response
            try:
                json_data = json.loads(raw_response)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start = raw_response.find('{')
                end = raw_response.rfind('}') + 1
                if start >= 0 and end > 0:
                    json_str = raw_response[start:end]
                    try:
                        json_data = json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.info(f"Failed to parse JSON from response: {raw_response}")
                        if has_plan:
                            return {"active_tactic": self._get_first_tactic_from_default_plan()}
                        else:
                            default_plan = self._default_plan()
                            return {
                                "goal": self._default_goal(),
                                "plan": default_plan,
                                "active_tactic": default_plan[0] if default_plan else None
                            }
                else:
                    # Fallback to default
                    logger.info(f"No JSON found in response: {raw_response}")
                    if has_plan:
                        return {"active_tactic": self._get_first_tactic_from_default_plan()}
                    else:
                        default_plan = self._default_plan()
                        return {
                            "goal": self._default_goal(),
                            "plan": default_plan,
                            "active_tactic": default_plan[0] if default_plan else None
                        }
            
            # Process based on whether we're selecting a tactic or generating a plan
            if has_plan:
                # For tactic selection, we only need active_tactic
                if "active_tactic" not in json_data:
                    json_data["active_tactic"] = self._get_first_tactic_from_default_plan()
                return {"active_tactic": json_data["active_tactic"]}
            else:
                # For plan generation
                if "goal" not in json_data:
                    json_data["goal"] = self._default_goal()
                    
                if "plan" not in json_data:
                    json_data["plan"] = self._default_plan()
                elif not isinstance(json_data["plan"], list):
                    # If plan exists but is not a list, convert it
                    json_data["plan"] = [json_data["plan"]]
                    
                # Set active_tactic to first tactic in plan
                json_data["active_tactic"] = json_data["plan"][0] if json_data["plan"] else None
                    
                return json_data
            
        except Exception as e:
            logger.info(f"Error processing plan: {str(e)}")
            # Fallback based on context
            if has_plan:
                return {"active_tactic": self._get_first_tactic_from_default_plan()}
            else:
                default_plan = self._default_plan()
                return {
                    "goal": self._default_goal(), 
                    "plan": default_plan,
                    "active_tactic": default_plan[0] if default_plan else None
                }
    
    def _default_goal(self) -> str:
        """Return a default goal based on personality"""
        if "friendly" in self.personality:
            return "build rapport"
        elif "analytical" in self.personality:
            return "gather information"
        else:
            return "maintain conversation"
            
    def _default_plan(self) -> List[str]:
        """Return a default plan based on personality"""
        if "friendly" in self.personality:
            return ["friendly conversation", "show empathy"]
        elif "analytical" in self.personality:
            return ["ask targeted questions", "analyze responses"]
        else:
            return ["balanced dialogue"]
            
    def _get_first_tactic_from_default_plan(self) -> str:
        """Get the first tactic from the default plan"""
        default_plan = self._default_plan()
        return default_plan[0] if default_plan else "balanced dialogue" 