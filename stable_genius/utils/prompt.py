from stable_genius.models.psyche import Psyche

# Please no indents in prompts

class PromptFormatter:
    @staticmethod
    def plan_prompt(psyche: Psyche) -> str:
        """Format psyche into planning prompt"""
        if psyche.plan:
            # If a plan exists, direct to tactic_selection_prompt instead
            return PromptFormatter.tactic_selection_prompt(psyche)
            
        return f"""You are {psyche.name} with a {psyche.personality} personality.
Current state: {psyche.tension_level}/100 tension
Recent history: {psyche.memories[-3:] if psyche.memories else 'No memories yet'}
Relationships: {list(psyche.relationships.keys())}
Conversation memory: {psyche.conversation_memory or 'No conversation summary yet'}

What should be your goal and plan in this conversation?

IMPORTANT: Respond ONLY with valid JSON containing 'goal' and 'plan' keys.
The 'plan' should be an ordered array of tactics to achieve your goal.
Example response: {{"goal": "convince them to buy your product", "plan": ["ask questions to show interest", "provide a demo", "ask for the sale"]}}"""

    @staticmethod
    def tactic_selection_prompt(psyche: Psyche) -> str:
        """Format psyche into tactic selection prompt"""
        return f"""You are {psyche.name} with a {psyche.personality} personality.
Current state: {psyche.tension_level}/100 tension
Recent history: {psyche.memories[-3:] if psyche.memories else 'No memories yet'}
Relationships: {list(psyche.relationships.keys())}
Conversation memory: {psyche.conversation_memory or 'No conversation summary yet'}
Current goal: {psyche.goal or 'No goal set'}
Current plan: {psyche.plan}
Active tactic: {psyche.active_tactic or 'None'}

Given the current state of the conversation, should you:
1. Keep using the current tactic "{psyche.active_tactic}" because it's working or not yet complete
2. Switch to a different tactic from your plan

IMPORTANT: Respond ONLY with valid JSON containing 'active_tactic' key with the tactic you want to use.
Example response: {{"active_tactic": "show empathy"}}"""
    
    @staticmethod
    def act_prompt(psyche: Psyche, observation: str) -> str:
        """Format psyche into action prompt"""
        return f"""You are {psyche.name} with a {psyche.personality} personality.
{observation}
Current goal: {psyche.goal or 'None'}
Active tactic: {psyche.active_tactic or 'None'}
Conversation memory: {psyche.conversation_memory or 'No conversation summary yet'}
Available actions: {psyche.pending_actions or ['say', 'ask', 'express']}

How should you respond? Use your active tactic to guide your response.

IMPORTANT: Respond ONLY with valid JSON containing 'action', 'speech', and 'conversation_summary' keys.
'conversation_summary' should be a brief 1-2 sentence update of how you perceive the conversation is going.
Example response: {{"action": "say", "speech": "Hello, how are you doing today?", "conversation_summary": "The conversation just started with a greeting. I need to build rapport."}}"""

    @staticmethod
    def intent_classification_prompt(observation: str) -> str:
        """Format prompt for intent classification"""
        return f"""Classify the intent of the following message into one of these categories:
- question
- statement
- command
- greeting
- farewell
- small_talk
- other

Message: "{observation}"

Respond with a JSON object containing:
{{"intent": "category", "confidence": 0-100}}"""