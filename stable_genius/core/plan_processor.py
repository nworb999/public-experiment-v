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
    
    def process(self, raw_response: str, has_plan: bool = False, psyche=None) -> Dict[str, Any]:
        """Process a planning response into a structured plan
        
        Args:
            raw_response: The raw response from the LLM
            has_plan: Whether the psyche already has a plan
            psyche: The agent's psyche for interiority-based fallbacks
        """
        # Check if this is an error response
        if raw_response.startswith("Error:"):
            logger.info(f"Planning error encountered: {raw_response}")
            if has_plan:
                # For tactic selection errors, return default active tactic
                return {
                    "active_tactic": self._get_first_tactic_from_default_plan(psyche),
                    "summary": """PLAN_PROCESSOR :: ERROR_RECOVERY
{
    "error_type": "processing_error",
    "fallback_action": "default_tactic_selection",
    "system_state": "degraded_mode"
}"""
                }
            else:
                # For plan generation errors, return existing goal and default plan
                existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
                plan = self._default_plan(psyche)
                return {
                    "goal": existing_goal,
                    "plan": plan,
                    "active_tactic": plan[0] if plan else None,
                    "summary": """PLAN_PROCESSOR :: ERROR_RECOVERY
{
    "error_type": "planning_error",
    "fallback_action": "preserve_existing_goal",
    "interiority_based": "true"
}"""
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
                            return {
                                "active_tactic": self._get_first_tactic_from_default_plan(psyche),
                                "summary": """PLAN_PROCESSOR :: JSON_PARSE_FAILED
{
    "parse_status": "failed",
    "fallback_action": "default_tactic_selection",
    "recovery_mode": "active"
}"""
                            }
                        else:
                            existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
                            default_plan = self._default_plan(psyche)
                            return {
                                "goal": existing_goal,
                                "plan": default_plan,
                                "active_tactic": default_plan[0] if default_plan else None,
                                "summary": """PLAN_PROCESSOR :: JSON_PARSE_FAILED
{
    "parse_status": "failed",
    "fallback_action": "preserve_existing_goal",
    "interiority_based": "true"
}"""
                            }
                else:
                    # Fallback to default
                    logger.info(f"No JSON found in response: {raw_response}")
                    if has_plan:
                        return {
                            "active_tactic": self._get_first_tactic_from_default_plan(psyche),
                            "summary": """PLAN_PROCESSOR :: NO_JSON_FOUND
{
    "json_detection": "failed",
    "fallback_action": "default_tactic_selection",
    "parser_state": "emergency_mode"
}"""
                        }
                    else:
                        existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
                        default_plan = self._default_plan(psyche)
                        return {
                            "goal": existing_goal,
                            "plan": default_plan,
                            "active_tactic": default_plan[0] if default_plan else None,
                            "summary": """PLAN_PROCESSOR :: NO_JSON_FOUND
{
    "json_detection": "failed",
    "fallback_action": "preserve_existing_goal",
    "interiority_based": "true"
}"""
                        }
            
            # Process based on whether we're selecting a tactic or generating a plan
            if has_plan:
                # For tactic selection, we only need active_tactic
                if "active_tactic" not in json_data:
                    json_data["active_tactic"] = self._get_first_tactic_from_default_plan(psyche)
                if "summary" not in json_data:
                    json_data["summary"] = """PLAN_PROCESSOR :: TACTIC_SELECTED
{
    "selection_basis": "conversation_state",
    "interiority_guided": "true",
    "cognitive_mode": "adaptive"
}"""
                return {
                    "active_tactic": json_data["active_tactic"],
                    "summary": json_data.get("summary")
                }
            else:
                # For plan generation - DO NOT fall back to default goals
                # Keep existing goal if LLM doesn't provide one
                if "goal" not in json_data:
                    existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
                    if existing_goal:
                        json_data["goal"] = existing_goal
                        logger.warning(f"LLM did not provide goal, keeping existing: {existing_goal}")
                    else:
                        logger.warning("LLM did not provide goal and no existing goal found - goal will be None")
                        json_data["goal"] = None
                    
                if "plan" not in json_data:
                    json_data["plan"] = self._default_plan(psyche)
                elif not isinstance(json_data["plan"], list):
                    # If plan exists but is not a list, convert it
                    json_data["plan"] = [json_data["plan"]]
                    
                # Set active_tactic to first tactic in plan
                json_data["active_tactic"] = json_data["plan"][0] if json_data["plan"] else None
                
                # Add summary if missing
                if "summary" not in json_data:
                    json_data["summary"] = """PLAN_PROCESSOR :: PLAN_GENERATED
{
    "generation_basis": "interiority_analysis",
    "goal_alignment": "dynamic",
    "tactical_coherence": "stable"
}"""
                    
                return json_data
            
        except Exception as e:
            logger.info(f"Error processing plan: {str(e)}")
            # Fallback based on context
            if has_plan:
                return {
                    "active_tactic": self._get_first_tactic_from_default_plan(psyche),
                    "summary": f"""PLAN_PROCESSOR :: EXCEPTION_HANDLED
{{
    "exception_type": "{type(e).__name__}",
    "fallback_action": "default_tactic_selection",
    "error_recovery": "successful"
}}"""
                }
            else:
                existing_goal = psyche.goal if psyche and hasattr(psyche, 'goal') and psyche.goal else None
                default_plan = self._default_plan(psyche)
                return {
                    "goal": existing_goal, 
                    "plan": default_plan,
                    "active_tactic": default_plan[0] if default_plan else None,
                    "summary": f"""PLAN_PROCESSOR :: EXCEPTION_HANDLED
{{
    "exception_type": "{type(e).__name__}",
    "fallback_action": "preserve_existing_goal",
    "error_recovery": "successful"
}}"""
                }
    
    def _default_goal(self, psyche=None) -> str:
        """Return a default goal based on interiority, fallback to personality"""
        if psyche:
            interior_summary = psyche.get_interior_summary()
            interior_principles = psyche.get_interior_principles()
            
            # Try to derive goal from interiority
            if interior_summary or interior_principles:
                # Generate goals based on interiority patterns
                combined_interior = f"{interior_summary or ''} {interior_principles or ''}".lower()
                
                if any(word in combined_interior for word in ["connect", "relationship", "understand", "empathy"]):
                    return "build genuine connection"
                elif any(word in combined_interior for word in ["help", "support", "care", "protect"]):
                    return "provide meaningful support"
                elif any(word in combined_interior for word in ["truth", "honest", "authentic", "real"]):
                    return "seek authentic understanding"
                elif any(word in combined_interior for word in ["learn", "grow", "discover", "explore"]):
                    return "explore and learn together"
                elif any(word in combined_interior for word in ["safe", "comfort", "peace", "calm"]):
                    return "create a safe space"
                else:
                    return "honor my values in this interaction"
        
        # Fallback to personality-based goals
        if "friendly" in self.personality:
            return "build rapport"
        elif "analytical" in self.personality:
            return "gather information"
        else:
            return "maintain conversation"
            
    def _default_plan(self, psyche=None) -> List[str]:
        """Return a default plan based on interiority, fallback to personality"""
        if psyche:
            interior_summary = psyche.get_interior_summary()
            interior_principles = psyche.get_interior_principles()
            
            # Try to derive tactics from interiority
            if interior_summary or interior_principles:
                combined_interior = f"{interior_summary or ''} {interior_principles or ''}".lower()
                tactics = []
                
                # Build tactics based on interior themes
                if any(word in combined_interior for word in ["listen", "hear", "understand"]):
                    tactics.append("listen deeply")
                if any(word in combined_interior for word in ["honest", "truth", "authentic", "real"]):
                    tactics.append("be authentic")
                if any(word in combined_interior for word in ["empathy", "feel", "emotion", "compassion"]):
                    tactics.append("show empathy")
                if any(word in combined_interior for word in ["share", "open", "vulnerable"]):
                    tactics.append("share meaningfully")
                if any(word in combined_interior for word in ["help", "support", "care"]):
                    tactics.append("offer support")
                if any(word in combined_interior for word in ["curious", "ask", "question", "explore"]):
                    tactics.append("ask thoughtful questions")
                if any(word in combined_interior for word in ["respect", "honor", "value"]):
                    tactics.append("respect boundaries")
                
                # Ensure we have at least one tactic
                if not tactics:
                    tactics = ["stay true to my values"]
                    
                return tactics
        
        # Fallback to personality-based plans
        if "friendly" in self.personality:
            return ["friendly conversation", "show empathy"]
        elif "analytical" in self.personality:
            return ["ask targeted questions", "analyze responses"]
        else:
            return ["balanced dialogue"]
            
    def _get_first_tactic_from_default_plan(self, psyche=None) -> str:
        """Get the first tactic from the default plan"""
        default_plan = self._default_plan(psyche)
        return default_plan[0] if default_plan else "balanced dialogue" 