from typing import Dict, Any, Optional
from stable_genius.models.psyche import Psyche
from stable_genius.core.components import PipelineComponent
from stable_genius.core.prompt import PromptFormatter
from stable_genius.utils.llm import OllamaLLM
from stable_genius.core.plan_processor import PlanProcessor
from stable_genius.core.action_processor import ActionProcessor
from stable_genius.utils.logger import logger

class ObserveComponent(PipelineComponent):
    """Processes observations and prepares context for planning"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Process observation and update the context with relevant information"""
        # Extract and format observation
        observation = context.get("input", "")
        
        # Update context with observation information
        context["observation"] = observation
        context["observation_processed"] = True
        
        return context

class PlanComponent(PipelineComponent):
    """Plans based on observation and psyche state"""
    
    def __init__(self, name: str, personality: str):
        super().__init__(name)
        self.llm = OllamaLLM(personality)
        self.plan_processor = PlanProcessor(personality)
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Generate a plan based on observation and psyche state"""
        # Generate planning prompt
        plan_prompt = PromptFormatter.plan_prompt(psyche)
        
        # Generate and process plan
        raw_plan_response = self.llm.generate(plan_prompt)
        plan = self.plan_processor.process(raw_plan_response)
        
        # Update psyche with new goal
        psyche.current_goal = plan.get('goal', 'understand the situation')
        
        # Update context with plan
        context["plan"] = plan
        
        return context

class ActionComponent(PipelineComponent):
    """Determines action based on plan, observation, and psyche state"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.llm = OllamaLLM()
        self.action_processor = ActionProcessor()
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Generate an action based on the plan and observation"""
        # Extract observation from context
        observation = context.get("observation", "")
        
        # Generate action prompt
        action_prompt = PromptFormatter.act_prompt(psyche, observation)
        
        # Generate and process action
        raw_action_response = self.llm.generate(action_prompt)
        action_response = self.action_processor.process(raw_action_response)
        
        # Ensure action_response has required keys
        if 'action' not in action_response:
            action_response['action'] = 'say'
        if 'speech' not in action_response:
            action_response['speech'] = "I'm not sure what to say right now."
        
        # Update context with action
        context["action"] = action_response
        context["speech"] = action_response.get("speech")
        
        return context

class ReflectComponent(PipelineComponent):
    """Updates the psyche based on plan, action, and observation"""
    
    def __init__(self, name: str):
        super().__init__(name)
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Update psyche based on the planning and action results"""
        # Extract data from context
        observation = context.get("observation", "")
        action = context.get("action", {})
        speech = action.get("speech", "")
        action_type = action.get("action", "say")
        
        # Update tension based on action
        self._update_tension(psyche, action_type)
        
        # Add to memories
        psyche.memories.append(f"{observation} -> {speech}")
        
        # Update context with reflection results
        context["reflection"] = {
            "tension_level": psyche.tension_level,
            "memory_added": f"{observation} -> {speech}"
        }
        
        return context
        
    def _update_tension(self, psyche: Psyche, action: str):
        """Update tension meter based on action"""
        if "confront" in action:
            psyche.tension_level = min(psyche.tension_level + 20, 100)
        elif "cooperate" in action or "say" in action:
            psyche.tension_level = max(psyche.tension_level - 10, 0)
        elif "ask" in action:
            # Asking questions slightly reduces tension
            psyche.tension_level = max(psyche.tension_level - 5, 0)

class IntentClassifierComponent(PipelineComponent):
    """Classifies user intent from input text"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.llm = OllamaLLM()
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Classify intent of the input and add to context"""
        observation = context.get("observation", "")
        
        # Generate intent classification prompt
        prompt = f"""
        Classify the intent of the following message into one of these categories:
        - question
        - statement
        - command
        - greeting
        - farewell
        - small_talk
        - other
        
        Message: "{observation}"
        
        Respond with a JSON object containing:
        {{"intent": "category", "confidence": 0-100}}
        """
        
        raw_response = self.llm.generate(prompt)
        
        try:
            # Extract JSON or create default
            import json
            start = raw_response.find('{')
            end = raw_response.rfind('}') + 1
            
            if start >= 0 and end > 0:
                intent_data = json.loads(raw_response[start:end])
            else:
                intent_data = {"intent": "other", "confidence": 50}
                
        except Exception as e:
            logger.error(f"Error processing intent classification: {e}")
            intent_data = {"intent": "other", "confidence": 50}
            
        # Add to context
        context["intent"] = intent_data
        
        return context 