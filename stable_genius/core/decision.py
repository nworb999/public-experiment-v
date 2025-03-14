import json
from stable_genius.models.psyche import Psyche
from stable_genius.core.prompt import PromptFormatter
from stable_genius.utils.llm import OllamaLLM
from stable_genius.core.plan_processor import PlanProcessor
from stable_genius.core.action_processor import ActionProcessor
from stable_genius.utils.response_processor import create_error_response

class DecisionPipeline:
    def __init__(self, personality="neutral"):
        self.llm = OllamaLLM(personality)  # Initialize with personality
        self.plan_processor = PlanProcessor(personality)
        self.action_processor = ActionProcessor()
    
    async def react_cycle(self, observation: str, psyche: Psyche) -> dict:
        """ReAct-style loop: Plan -> Act -> Reflect"""
        # Plan phase
        plan_prompt = PromptFormatter.plan_prompt(psyche)
        raw_plan_response = self.llm.generate(plan_prompt)
        plan = self.plan_processor.process(raw_plan_response)
        psyche.current_goal = plan.get('goal', 'understand the situation')
        
        # Act phase
        action_prompt = PromptFormatter.act_prompt(psyche, observation)
        raw_action_response = self.llm.generate(action_prompt)
        action_response = self.action_processor.process(raw_action_response)
        
        # Ensure action_response has required keys
        if 'action' not in action_response:
            action_response['action'] = 'say'
        if 'speech' not in action_response:
            action_response['speech'] = "I'm not sure what to say right now."
        
        # Reflect phase
        self._update_tension(psyche, action_response.get('action', ''))
        psyche.memories.append(f"{observation} -> {action_response.get('speech', '')}")
        
        # Note: We don't save the psyche here - that's the agent's responsibility
        
        return action_response
    
    def _update_tension(self, psyche: Psyche, action: str):
        """Update tension meter based on action"""
        if "confront" in action:
            psyche.tension_level = min(psyche.tension_level + 20, 100)
        elif "cooperate" in action or "say" in action:
            psyche.tension_level = max(psyche.tension_level - 10, 0)
        elif "ask" in action:
            # Asking questions slightly reduces tension
            psyche.tension_level = max(psyche.tension_level - 5, 0) 