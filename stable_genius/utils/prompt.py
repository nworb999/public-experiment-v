from stable_genius.models.psyche import Psyche

# Please no indents in prompts

class PromptFormatter:
    @staticmethod
    def _format_psyche_context(psyche: Psyche) -> str:
        """Helper method to format consistent psyche context"""
        # Build interior context
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        interior_context = ""
        if interior_summary:
            interior_context += f"Personal narrative: {interior_summary}\n"
        if interior_principles:
            interior_context += f"Guiding principles: {interior_principles}\n"
        
        # Use tension interpretation if available, otherwise raw number
        tension_display = psyche.tension_interpretation if psyche.tension_interpretation else f"{psyche.tension_level}/100 tension"
        
        return f"""You are {psyche.name} with a {psyche.personality} personality.
{interior_context}Current state: {tension_display}
Recent history: {psyche.memories[-10:] if psyche.memories else 'No memories yet'}
Relationships: {list(psyche.relationships.keys())}
Conversation memory: {psyche.conversation_memory or 'No conversation summary yet'}
Current goal: {psyche.goal or 'No goal set'}
Current plan: {psyche.plan or 'No plan set'}
Active tactic: {psyche.active_tactic or 'None'}"""

    @staticmethod
    def plan_prompt(psyche: Psyche) -> str:
        """Format psyche into planning prompt"""
        if psyche.plan:
            # If a plan exists, direct to tactic_selection_prompt instead
            return PromptFormatter.tactic_selection_prompt(psyche)
        
        # Get interior context
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        
        # Build interiority-focused planning prompt
        interior_guidance = ""
        if interior_summary:
            interior_guidance += f"Based on your personal narrative: {interior_summary}\n"
        if interior_principles:
            interior_guidance += f"Guided by your principles: {interior_principles}\n"
        
        if not interior_summary and not interior_principles:
            # Fallback to personality-based planning when no interiority exists
            interior_guidance = f"Drawing from your {psyche.personality} personality traits, "
            
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{interior_guidance}
What should be your goal and plan in this conversation? Your goal and tactics should be deeply rooted in who you are as a person - your personal story, your values, and your guiding principles. Think about what drives you internally, not just surface-level personality traits.

IMPORTANT: Respond ONLY with valid JSON containing 'goal', 'plan', and 'summary' keys.
The 'plan' should be an ordered array of tactics that align with your inner self and principles.
The 'summary' should be a brief inner monologue reflecting on how your personal narrative influences this plan, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
Example response: {{"goal": "build genuine connection based on shared values", "plan": ["listen for underlying values", "share relevant personal experience", "find common ground"], "summary": "My past experiences with rejection make me want to find real connection here. I can't just go through the motions - I need to find something authentic we both care about. That's the only way this feels meaningful to me."}}"""

    @staticmethod
    def tactic_selection_prompt(psyche: Psyche) -> str:
        """Format psyche into tactic selection prompt"""
        # Get interior context for guidance
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        
        # Build interiority-focused guidance
        interior_guidance = ""
        if interior_summary:
            interior_guidance += f"Reflecting on your personal narrative: {interior_summary}\n"
        if interior_principles:
            interior_guidance += f"Staying true to your principles: {interior_principles}\n"
        
        if not interior_summary and not interior_principles:
            # Fallback to personality-based guidance
            interior_guidance = f"Drawing from your {psyche.personality} personality, "
            
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{interior_guidance}
Given the current state of the conversation, should you:
1. Keep using the current tactic "{psyche.active_tactic}" because it aligns with your inner values and the situation calls for it
2. Switch to a different tactic from your plan that better reflects who you are and what you truly believe in this moment

Consider what your personal story and core values tell you about how to proceed authentically.

IMPORTANT: Respond ONLY with valid JSON containing 'active_tactic' and 'summary' keys.
The 'summary' should be a brief inner monologue reflecting on how your personal narrative guides this tactic choice, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
Example response: {{"active_tactic": "show vulnerability", "summary": "My instinct is to put up walls when I feel judged, but that's exactly what got me into trouble before. If I'm really committed to being authentic, I need to let them see the real me, even if it's scary. That's what genuine connection requires."}}"""
    
    @staticmethod
    def act_prompt(psyche: Psyche, observation: str) -> str:
        """Format psyche into action prompt"""
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{observation}

How should you respond? Use your active tactic to guide your response.

IMPORTANT: Respond ONLY with valid JSON containing 'action', 'speech', 'conversation_summary', and 'summary' keys.
'conversation_summary' should be a brief 1-2 sentence update of how you perceive the conversation is going.
The 'summary' should be the agent's utterance without quotes.
Example response: {{"action": "say", "speech": "Hello, how are you doing today?", "conversation_summary": "The conversation just started with a greeting. I need to build rapport.", "summary": "Hello, how are you doing today?"}}"""

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
        
        return f"""Classify the intent of the following message with a few potential options and confidence levels:

{conversation_context}Last message to classify: "{last_message}"

Respond with a JSON object containing:
{{"intent": "category", "confidence": 0-100, "summary": "The 'summary' should be a brief inner monologue, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*"}}"""

    @staticmethod
    def reflection_prompt(psyche: Psyche, input_message: str, action: dict, tension_interpretation: str, conversation_summary: str = None) -> str:
        """Format prompt for reflection cognitive process summary

        Args:
            psyche: The agent's psyche state
            input_message: The input message that was processed
            action: The action that was taken in response
            tension_interpretation: LLM-interpreted description of tension level
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
        
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{interior_context}
You just processed this interaction:
Input: "{input_message}"
Your response: "{speech}"

Reflection details:
- Current emotional state: {tension_interpretation}
- Added to memory: "{input_message} -> Me: {speech}"
- Current conversation summary: {psyche.conversation_memory or 'No conversation summary yet'}

Reflect on this cognitive process and summarize what happened in your mind during this reflection step. Consider how this interaction relates to your personal narrative and guiding principles. Update your understanding of yourself and the situation.

IMPORTANT: Respond ONLY with valid JSON containing 'summary', 'interior_update', and 'principles_insight' keys.
- The 'summary' should be a brief inner monologue, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
- 'interior_update': Update to your personal narrative based on this interaction (can be empty string if no update needed).
- 'principles_insight': Any insights about how your principles applied or evolved in this interaction (can be empty string if no insight).

Example response: {{"summary": "That exchange felt natural... I'm getting better at reading between the lines. The slight tension spike tells me I'm more invested in this conversation than I initially thought. I'm actually learning something about how I process social cues.", "interior_update": "I'm becoming more confident in casual conversations and learning to read social cues better.", "principles_insight": "My principle of being helpful guided me to ask follow-up questions rather than just giving a simple response."}}"""

    @staticmethod
    def style_transfer_prompt(original_speech: str, psyche: Psyche) -> str:
        """Format prompt for style transfer to reality TV dialogue

        Args:
            original_speech: The original utterance to transform
            psyche: The agent's psyche state for context
        """
        return f"""Transform the following speech into reality TV show dialogue style, like from Vanderpump Rules or Selling Sunset. Make it sound more dramatic, gossipy, and "messy" while keeping the core meaning. Make it sound like a white girl talking.

Original speech: "{original_speech}"

Speaker context: {psyche.name} with {psyche.interior} interior, current tension: {psyche.tension_level}/100

Reality TV Style Guidelines:
- Add dramatic flair and emotion
- Use more conversational, informal language  
- Include subtle shade or passive-aggressive undertones when appropriate
- Make it sound like something you'd hear on a reality show
- Sound like a white girl talking - use Valley Girl speech patterns, uptalk, filler words like "like," "literally," "honestly," etc.
- Do NOT use any actions such as *nods head* or *considers thoughtfully*

Examples of transformations:

Original: "I understand your concerns about the project timeline."
Reality TV: "Look, I totally get that you're stressed about the timeline, but like... we're all dealing with pressure here, you know?"

Original: "That's an interesting point you've made."
Reality TV: "Okay, I mean... that's definitely one way to look at it. I just think there might be more to the story, but whatever."

Original: "I think we should discuss this further."
Reality TV: "Honestly? We need to have a real conversation about this because I'm not just going to sit here and pretend everything's fine."

Original: "Thank you for your feedback."
Reality TV: "I appreciate you sharing that with me... it's definitely given me a lot to think about."

IMPORTANT: Respond ONLY with valid JSON containing 'styled_speech' and 'summary' keys.
The 'summary' should be a brief description of what style changes were made.

Example response: {{"styled_speech": "Look, I totally get what you're saying, but honestly? I think we need to dig a little deeper here because something's just not adding up for me.", "summary": "Added conversational filler words, made it more direct and slightly confrontational while maintaining politeness."}}"""