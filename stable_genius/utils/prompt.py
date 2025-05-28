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

    @staticmethod
    def reflection_prompt(psyche: Psyche, input_message: str, action: dict, tension: int, conversation_summary: str = None) -> str:
        """Format prompt for reflection cognitive process summary

        Args:
            psyche: The agent's psyche state
            input_message: The input message that was processed
            action: The action that was taken in response
            tension_before: Tension level before processing
            tension_after: Tension level after processing
            conversation_summary: Updated conversation summary if available
        """
        speech = action.get("speech", "")        

        # Get interior state
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        
        # Build interior context
        interior_context = ""
        if interior_summary:
            interior_context += f"Your personal narrative: {interior_summary}\n"
        if interior_principles:
            interior_context += f"Your guiding principles: {interior_principles}\n"
        
        return f"""You are {psyche.name} with a {psyche.personality} personality.

{interior_context}
You just processed this interaction:
Input: "{input_message}"
Your response: "{speech}"

Reflection details:
- Current tension level: {tension}/100
- Added to memory: "{input_message} -> Me: {speech}"
- Current conversation summary: {psyche.conversation_memory or 'No conversation summary yet'}
- Total memories stored: {len(psyche.memories) if psyche.memories else 0}

Reflect on this cognitive process and summarize what happened in your mind during this reflection step. Consider how this interaction relates to your personal narrative and guiding principles. Update your understanding of yourself and the situation.

IMPORTANT: Respond ONLY with valid JSON containing 'summary', 'interior_update', and 'principles_insight' keys.
- 'summary': Describe your internal cognitive process during reflection - what you learned, how you updated your understanding, and any insights gained.
- 'interior_update': Update to your personal narrative based on this interaction (can be empty string if no update needed).
- 'principles_insight': Any insights about how your principles applied or evolved in this interaction (can be empty string if no insight).

Example response: {{"summary": "I reflected on the conversation flow and updated my memory with this exchange. The slight tension increase suggests I'm becoming more engaged, and I'm building a clearer picture of the user's communication style through our ongoing dialogue.", "interior_update": "I'm becoming more confident in casual conversations and learning to read social cues better.", "principles_insight": "My principle of being helpful guided me to ask follow-up questions rather than just giving a simple response."}}"""