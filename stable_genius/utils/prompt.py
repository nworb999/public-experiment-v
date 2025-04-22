from stable_genius.models.psyche import Psyche

# Please no indents in prompts

class PromptFormatter:
    @staticmethod
    def plan_prompt(psyche: Psyche) -> str:
        """Format psyche into planning prompt"""
        return f"""You are {psyche.name} with a {psyche.personality} personality.
Current state: {psyche.tension_level}/100 tension
Recent history: {psyche.memories[-3:] if psyche.memories else 'No memories yet'}
Relationships: {list(psyche.relationships.keys())}
Goals: {psyche.goal or 'None'}

What should you do next? 

IMPORTANT: Respond ONLY with valid JSON containing 'goal' and 'tactic' keys.
Example response: {{"goal": "understand situation", "tactic": "ask questions"}}"""
    
    @staticmethod
    def act_prompt(psyche: Psyche, observation: str) -> str:

        """Format psyche into action prompt"""
        return f"""You are {psyche.name} with a {psyche.personality} personality.
{observation}
Current goal: {psyche.goal}
Available actions: {psyche.pending_actions or ['say', 'ask', 'express']}

How should you respond?

IMPORTANT: Respond ONLY with valid JSON containing 'action' and 'speech' keys.
Example response: {{"action": "say", "speech": "Hello, how are you doing today?"}}"""