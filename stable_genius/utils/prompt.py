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

IMPORTANT: Respond ONLY with valid JSON containing 'goal', 'plan', and 'summary' keys.
The 'plan' should be an ordered array of tactics to achieve your goal.
The 'summary' should be a brief description of your cognitive process in making this plan.
Example response: {{"goal": "convince them to buy your product", "plan": ["ask questions to show interest", "provide a demo", "ask for the sale"], "summary": "I'm formulating a sales approach with gradual engagement to avoid being pushy while maintaining focus on the product."}}"""

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

IMPORTANT: Respond ONLY with valid JSON containing 'active_tactic' and 'summary' keys.
The 'summary' should explain your reasoning for keeping or changing tactics.
Example response: {{"active_tactic": "show empathy", "summary": "The conversation is becoming emotional, so I'm switching to an empathetic approach rather than continuing with information gathering."}}"""
    
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

IMPORTANT: Respond ONLY with valid JSON containing 'action', 'speech', 'conversation_summary', and 'summary' keys.
'conversation_summary' should be a brief 1-2 sentence update of how you perceive the conversation is going.
'summary' should explain your cognitive process for choosing this response.
Example response: {{"action": "say", "speech": "Hello, how are you doing today?", "conversation_summary": "The conversation just started with a greeting. I need to build rapport.", "summary": "I'm opening with a friendly greeting to establish rapport and create a positive atmosphere for the conversation."}}"""

    @staticmethod
    def intent_classification_prompt(last_message: str, conversation_history: list = None) -> str:
        """Format prompt for intent classification using last message and conversation history

        Args:
            last_message: The last message to classify
            conversation_history: List of recent utterances for context
        """
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context = "Previous conversation:\n" + "\n".join(conversation_history[-10:]) + "\n\n"
        
        return f"""Classify the intent of the following message into one of these categories:
- question
- statement
- command
- greeting
- farewell
- small_talk
- other

{conversation_context}Last message to classify: "{last_message}"

Respond with a JSON object containing:
{{"intent": "category", "confidence": 0-100, "summary": "Reasoning behind this classification."}}"""