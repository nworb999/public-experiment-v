import json
import logging
from stable_genius.models.psyche import Psyche
from stable_genius.core.prompt import PromptFormatter
from stable_genius.utils.llm import OllamaLLM
from stable_genius.core.plan_processor import PlanProcessor
from stable_genius.core.action_processor import ActionProcessor
from stable_genius.utils.response_processor import create_error_response
from stable_genius.utils.logger import logger

class DecisionPipeline:
    """Manages the agent's decision-making process"""
    
    def __init__(self, personality="neutral"):
        self.personality = personality
        self.callbacks = []
        self.llm = OllamaLLM(personality)  # Initialize with personality
        self.plan_processor = PlanProcessor(personality)
        self.action_processor = ActionProcessor()
    
    def register_callback(self, callback):
        """Register a callback function to receive pipeline updates
        
        The callback should accept (stage_name, data) parameters
        """
        self.callbacks.append(callback)
    
    def notify_callbacks(self, stage, data):
        """Notify all registered callbacks with pipeline stage updates"""
        for callback in self.callbacks:
            try:
                callback(stage, data)
            except Exception as e:
                logger.error(f"Error in pipeline callback: {e}")
    
    async def react_cycle(self, observation: str, psyche: Psyche) -> dict:
        """ReAct-style loop: Observe -> Plan -> Act -> Reflect"""
        # Notify start of processing
        self.notify_callbacks("observe", {"input": observation})
        
        # Plan phase
        plan_prompt = PromptFormatter.plan_prompt(psyche)
        raw_plan_response = self.llm.generate(plan_prompt)
        plan = self.plan_processor.process(raw_plan_response)
        psyche.current_goal = plan.get('goal', 'understand the situation')
        
        # Notify planning result
        self.notify_callbacks("planning", plan)
        
        # Act phase
        action_prompt = PromptFormatter.act_prompt(psyche, observation)
        raw_action_response = self.llm.generate(action_prompt)
        action_response = self.action_processor.process(raw_action_response)
        
        # Ensure action_response has required keys
        if 'action' not in action_response:
            action_response['action'] = 'say'
        if 'speech' not in action_response:
            action_response['speech'] = "I'm not sure what to say right now."
        
        # Notify action result
        self.notify_callbacks("action", action_response)
        
        # Reflect phase
        self._update_tension(psyche, action_response.get('action', ''))
        psyche.memories.append(f"{observation} -> {action_response.get('speech', '')}")
        
        # Return the combined response with plan information
        result = {
            "speech": action_response.get('speech', "I don't know what to say."),
            "plan": plan,
            "action": action_response
        }
        
        # Notify complete cycle
        self.notify_callbacks("complete", {"result": result})
        
        return result
    
    def _update_tension(self, psyche: Psyche, action: str):
        """Update tension meter based on action"""
        if "confront" in action:
            psyche.tension_level = min(psyche.tension_level + 20, 100)
        elif "cooperate" in action or "say" in action:
            psyche.tension_level = max(psyche.tension_level - 10, 0)
        elif "ask" in action:
            # Asking questions slightly reduces tension
            psyche.tension_level = max(psyche.tension_level - 5, 0) 