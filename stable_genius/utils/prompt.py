from stable_genius.models.psyche import Psyche
from stable_genius.utils.logger import logger

# Please no indents in prompts

class PromptFormatter:
    @staticmethod
    def _format_psyche_context(psyche: Psyche) -> str:
        """Helper method to format consistent psyche context"""
        logger.debug(f"🧠 Formatting psyche context for {psyche.name}")
        
        # Build interior context
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        interior_context = ""
        if interior_summary:
            interior_context += f"Personal narrative: {interior_summary}\n"
            logger.debug(f"  📝 Interior summary included: {interior_summary[:50]}...")
        if interior_principles:
            interior_context += f"Guiding principles: {interior_principles}\n"
            logger.debug(f"  🎯 Interior principles included: {interior_principles}")
        
        # Add premise interpretation if available
        premise_context = ""
        if psyche.premise_interpretation:
            premise_context = f"Current situation perspective: {psyche.premise_interpretation}\n"
            logger.info(f"  🎬 PREMISE CONTEXT INCLUDED for {psyche.name}: {psyche.premise_interpretation[:80]}...")
        else:
            logger.warning(f"  ⚠️  NO PREMISE INTERPRETATION for {psyche.name} - agent may lack reality TV context!")
        
        # Add hero identity (how they see themselves) 
        hero_context = ""
        if psyche.hero_description:
            hero_context = f"Core identity: You believe you are {psyche.hero_description}\n"
            logger.info(f"  🦸 HERO IDENTITY INCLUDED for {psyche.name}: {psyche.hero_description}")
        else:
            logger.warning(f"  ⚠️  NO HERO IDENTITY for {psyche.name} - missing self-perception!")
        
        # Add villain perspectives (how they see others)
        villain_context = ""
        if psyche.other_agent_perspectives:
            perspectives = []
            for agent_name, perspective_data in psyche.other_agent_perspectives.items():
                perspective = perspective_data.get("perspective", "")
                if perspective:
                    perspectives.append(f"About {agent_name}: {perspective}")
            if perspectives:
                villain_context = f"Other people: {' | '.join(perspectives)}\n"
                logger.info(f"  👁️  VILLAIN PERSPECTIVES INCLUDED for {psyche.name}: {len(perspectives)} perspectives")
                for i, persp in enumerate(perspectives):
                    logger.debug(f"    {i+1}. {persp[:60]}...")
        else:
            logger.warning(f"  ⚠️  NO VILLAIN PERSPECTIVES for {psyche.name} - missing social dynamics!")
        
        # Subtly incorporate hidden flaws without making them explicit
        # The agent should not be consciously aware of these flaws
        subconscious_tendencies = ""
        if psyche.hidden_flaws:
            logger.info(f"  🎭 HIDDEN FLAWS PROCESSING for {psyche.name}: {psyche.hidden_flaws}")
            # Convert flaws to subtle behavioral tendencies without naming the flaw
            tendency_hints = []
            for flaw in psyche.hidden_flaws:
                if flaw == "Arrogant":
                    tendency_hints.append("confidence in your own judgment")
                elif flaw == "Backstabbing":
                    tendency_hints.append("awareness of strategic opportunities")
                elif flaw == "Blatant Liar":
                    tendency_hints.append("flexibility with facts when helpful")
                elif flaw == "Bossy":
                    tendency_hints.append("natural leadership instincts")
                elif flaw == "Chronic Backstager":
                    tendency_hints.append("strategic thinking about relationships")
                elif flaw == "Conflict Ball":
                    tendency_hints.append("passion for standing your ground")
                elif flaw == "Cowardly":
                    tendency_hints.append("careful consideration of risks")
                elif flaw == "Crybaby":
                    tendency_hints.append("emotional sensitivity")
                elif flaw == "Drama Queen":
                    tendency_hints.append("appreciation for the significance of events")
                elif flaw == "Flaky":
                    tendency_hints.append("adaptability to changing circumstances")
                elif flaw == "Greedy":
                    tendency_hints.append("focus on personal advancement")
                elif flaw == "Hot-Blooded":
                    tendency_hints.append("quick emotional reactions")
                elif flaw == "Lazy":
                    tendency_hints.append("efficiency-focused approach")
                elif flaw == "Manipulative":
                    tendency_hints.append("understanding of social dynamics")
                elif flaw == "Narcissist":
                    tendency_hints.append("strong sense of personal importance")
                elif flaw == "Needy":
                    tendency_hints.append("value for others' opinions")
                elif flaw == "Poor Communication Kills":
                    tendency_hints.append("unique interpretation of conversations")
                elif flaw == "Sore Loser":
                    tendency_hints.append("high investment in outcomes")
                elif flaw == "Stubborn":
                    tendency_hints.append("commitment to your convictions")
                elif flaw == "Vain":
                    tendency_hints.append("awareness of how others perceive you")
            
            if tendency_hints:
                subconscious_tendencies = f"Natural tendencies: {', '.join(tendency_hints[:2])}\n"  # Limit to 2 to avoid overload
                logger.info(f"  🧩 SUBCONSCIOUS TENDENCIES INCLUDED for {psyche.name}: {', '.join(tendency_hints[:2])}")
        else:
            logger.warning(f"  ⚠️  NO HIDDEN FLAWS for {psyche.name} - missing behavioral complexity!")
        
        # Use tension interpretation if available, make it brief and not a complete sentence
        if psyche.tension_interpretation:
            # Take first few words and remove sentence endings
            tension_brief = psyche.tension_interpretation.split('.')[0].split('!')[0].split('?')[0]
            tension_brief = ' '.join(tension_brief.split()[:4])  # Limit to 4 words max
            tension_display = tension_brief.lower()
        else:
            tension_display = f"{psyche.tension_level}/100 tension"
        
        # Add tactic counter information
        tactic_info = f"Active tactic: {psyche.active_tactic or 'None'} (used for {psyche.rounds_since_tactic_change} rounds)"
        
        # Log final summary of what premise elements were included
        included_elements = []
        if premise_context:
            included_elements.append("premise_interpretation")
        if hero_context:
            included_elements.append("hero_identity")
        if villain_context:
            included_elements.append("villain_perspectives")
        if subconscious_tendencies:
            included_elements.append("hidden_flaws")
        
        if included_elements:
            logger.info(f"  ✅ FINAL CONTEXT for {psyche.name}: {', '.join(included_elements)} included in prompt")
        else:
            logger.error(f"  ❌ NO PREMISE ELEMENTS included for {psyche.name} - using generic agent context!")
        
        return f"""You are {psyche.name} with a {psyche.personality} personality.
{interior_context}{premise_context}{hero_context}{villain_context}{subconscious_tendencies}Current state: {tension_display}
Recent history: {psyche.memories[-10:] if psyche.memories else 'No memories yet'}
Relationships: {list(psyche.relationships.keys())}
Conversation memory: {psyche.conversation_memory or 'No conversation summary yet'}
Current goal: {psyche.goal or 'No goal set'}
Current plan: {psyche.plan or 'No plan set'}
{tactic_info}"""

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

IMPORTANT: Respond ONLY with valid JSON containing these keys:
- 'goal': Your conversational goal (4 words maximum)
- 'plan': An ordered array of tactics that align with your inner self and principles (4 brief tactics maximum, each 1-3 words)
- 'summary': A brief inner monologue reflecting on how your personal narrative influences this plan, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
- 'system_summary': Technical analysis formatted as: "PLAN_COMPONENT :: GENERATED\\n{{\\n    \\"goal_established\\": \\"[your goal]\\",\\n    \\"tactics_count\\": [number of tactics],\\n    \\"active_tactic\\": \\"[first tactic]\\",\\n    \\"planning_basis\\": \\"interiority_analysis\\",\\n    \\"strategic_coherence\\": \\"optimized\\"\\n}}"

Example response: {{"goal": "build genuine connection", "plan": ["listen deeply", "share vulnerably", "find common ground", "be authentic"], "summary": "My past experiences with rejection make me want to find real connection here. I can't just go through the motions - I need to find something authentic we both care about. That's the only way this feels meaningful to me.", "system_summary": "PLAN_COMPONENT :: GENERATED\\n{{\\n    \\"goal_established\\": \\"build genuine connection\\",\\n    \\"tactics_count\\": 4,\\n    \\"active_tactic\\": \\"listen deeply\\",\\n    \\"planning_basis\\": \\"interiority_analysis\\",\\n    \\"strategic_coherence\\": \\"optimized\\"\\n}}"}}"""

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
        
        # Determine if tactic switching is encouraged based on counter
        rounds_info = f"You've been using '{psyche.active_tactic}' for {psyche.rounds_since_tactic_change} rounds."
        switching_guidance = ""
        if psyche.rounds_since_tactic_change >= 4:
            switching_guidance = "Consider switching tactics - you've been using the same approach for a while and variety often leads to better outcomes."
        elif psyche.rounds_since_tactic_change >= 2:
            switching_guidance = "You might want to consider switching tactics soon to keep the conversation dynamic."
        else:
            switching_guidance = "Your current tactic is still fresh - consider whether it's working well or if a change would be beneficial."
            
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{interior_guidance}
{rounds_info}
{switching_guidance}

Given the current state of the conversation, should you:
1. Keep using the current tactic "{psyche.active_tactic}" because it aligns with your inner values and the situation calls for it
2. Switch to a different tactic from your plan that better reflects who you are and what you truly believe in this moment

Consider what your personal story and core values tell you about how to proceed authentically. Also consider that tactical variety often leads to more engaging and effective conversations.

IMPORTANT: Respond ONLY with valid JSON containing these keys:
- 'active_tactic': The tactic you choose to use
- 'summary': A brief inner monologue reflecting on how your personal narrative guides this tactic choice, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
- 'system_summary': Technical analysis formatted as: "PLAN_COMPONENT :: TACTIC_UPDATED\\n{{\\n    \\"selected_tactic\\": \\"[your chosen tactic]\\",\\n    \\"selection_method\\": \\"llm_guided\\",\\n    \\"plan_coherence\\": \\"maintained\\",\\n    \\"cognitive_state\\": \\"adaptive\\"\\n}}"

Example response: {{"active_tactic": "show vulnerability", "summary": "My instinct is to put up walls when I feel judged, but that's exactly what got me into trouble before. If I'm really committed to being authentic, I need to let them see the real me, even if it's scary. That's what genuine connection requires.", "system_summary": "PLAN_COMPONENT :: TACTIC_UPDATED\\n{{\\n    \\"selected_tactic\\": \\"show vulnerability\\",\\n    \\"selection_method\\": \\"llm_guided\\",\\n    \\"plan_coherence\\": \\"maintained\\",\\n    \\"cognitive_state\\": \\"adaptive\\"\\n}}"}}"""
    
    @staticmethod
    def act_prompt(psyche: Psyche, observation: str) -> str:
        """Format psyche into action prompt"""
        return f"""{PromptFormatter._format_psyche_context(psyche)}

{observation}

How should you respond? Use your active tactic to guide your response.

IMPORTANT: Keep your speech to 30 words or under and no more than two sentences. Respond ONLY with valid JSON containing these keys:
- 'action': Type of action (usually "say")
- 'speech': Your actual dialogue/utterance (30 words maximum, 2 sentences maximum)
- 'conversation_summary': Brief 1-2 sentence update of how you perceive the conversation is going
- 'summary': The agent's utterance without quotes
- 'system_summary': Technical analysis formatted as: "SPEECH_GENERATION :: PROCESSED\\n{{\\n    \\"dialogue\\": \\"[your speech]\\",\\n    \\"action_type\\": \\"[action]\\",\\n    \\"tactic_applied\\": \\"[active tactic]\\",\\n    \\"style_filter\\": \\"reality_tv_persona\\",\\n    \\"output_coherence\\": \\"optimized\\"\\n}}"

Example response: {{"action": "say", "speech": "Hello, how are you doing today?", "conversation_summary": "The conversation just started with a greeting. I need to build rapport.", "summary": "Hello, how are you doing today?", "system_summary": "SPEECH_GENERATION :: PROCESSED\\n{{\\n    \\"dialogue\\": \\"Hello, how are you doing today?\\",\\n    \\"action_type\\": \\"say\\",\\n    \\"tactic_applied\\": \\"friendly_greeting\\",\\n    \\"style_filter\\": \\"reality_tv_persona\\",\\n    \\"output_coherence\\": \\"optimized\\"\\n}}"}}"""

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

- greeting: Starting a conversation, saying hello
- question: Asking for information or clarification  
- opinion: Sharing thoughts, beliefs, or perspectives
- agreement: Expressing agreement or approval
- disagreement: Expressing disagreement or disagreement
- emotion: Expressing feelings, mood, or emotional state
- request: Asking for something to be done
- compliment: Giving praise or positive feedback
- criticism: Giving negative feedback or criticism
- small_talk: Casual conversation, weather, etc.
- goodbye: Ending conversation, saying farewell
- other: Anything that doesn't fit the above categories

{conversation_context}Last message to classify: "{last_message}"

IMPORTANT: Respond ONLY with valid JSON containing all these keys:
- 'intent': The classified intent category
- 'confidence': Confidence score (0-100)
- 'summary': Brief explanation of the classification
- 'emotional_tone': Detected emotional tone (positive, negative, neutral, excited, frustrated, etc.)
- 'urgency': How urgent this message seems (low, medium, high)
- 'category': Broader grouping (social, informational, emotional, transactional)
- 'system_summary': Technical analysis formatted as: "INTENT_PARSER :: ANALYZED\\n{{\\n    \\"classification\\": \\"[intent]\\",\\n    \\"confidence_score\\": \\"[confidence]%\\",\\n    \\"emotional_vector\\": \\"[emotional_tone]\\",\\n    \\"urgency_level\\": \\"[urgency]\\",\\n    \\"processing_context\\": \\"[category]_domain\\"\\n}}"

Examples:
{{"intent": "greeting", "confidence": 95, "summary": "They're clearly starting the conversation with a friendly hello.", "emotional_tone": "positive", "urgency": "low", "category": "social", "system_summary": "INTENT_PARSER :: ANALYZED\\n{{\\n    \\"classification\\": \\"greeting\\",\\n    \\"confidence_score\\": \\"95%\\",\\n    \\"emotional_vector\\": \\"positive\\",\\n    \\"urgency_level\\": \\"low\\",\\n    \\"processing_context\\": \\"social_domain\\"\\n}}"}}
{{"intent": "question", "confidence": 80, "summary": "This sounds like they want to know something specific.", "emotional_tone": "neutral", "urgency": "medium", "category": "informational", "system_summary": "INTENT_PARSER :: ANALYZED\\n{{\\n    \\"classification\\": \\"question\\",\\n    \\"confidence_score\\": \\"80%\\",\\n    \\"emotional_vector\\": \\"neutral\\",\\n    \\"urgency_level\\": \\"medium\\",\\n    \\"processing_context\\": \\"informational_domain\\"\\n}}"}}
{{"intent": "opinion", "confidence": 70, "summary": "They're sharing their personal thoughts on this topic.", "emotional_tone": "engaged", "urgency": "low", "category": "social", "system_summary": "INTENT_PARSER :: ANALYZED\\n{{\\n    \\"classification\\": \\"opinion\\",\\n    \\"confidence_score\\": \\"70%\\",\\n    \\"emotional_vector\\": \\"engaged\\",\\n    \\"urgency_level\\": \\"low\\",\\n    \\"processing_context\\": \\"social_domain\\"\\n}}"}}

Your response:"""

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

IMPORTANT: Respond ONLY with valid JSON containing these keys:
- 'summary': A brief inner monologue, neurotic sounding. make it present tense. Do NOT include any actions such as *anxiously adjusts glasses*
- 'interior_update': Update to your personal narrative based on this interaction (can be empty string if no update needed)
- 'principles_insight': Any insights about how your principles applied or evolved in this interaction (can be empty string if no insight)
- 'system_summary': Technical analysis formatted as: "REFLECTION_CYCLE :: COMPLETE\\n{{\\n    \\"memory_buffer_updated\\": \\"+1 entry\\",\\n    \\"tension_interpretation\\": \\"[current state]\\",\\n    \\"stressor_learning\\": \\"[learning status]\\",\\n    \\"self_model_coherence\\": \\"[coherence level]\\",\\n    \\"tension_level\\": \\"{psyche.tension_level}/100\\"\\n}}"

Example response: {{"summary": "That exchange felt natural... I'm getting better at reading between the lines. The slight tension spike tells me I'm more invested in this conversation than I initially thought. I'm actually learning something about how I process social cues.", "interior_update": "I'm becoming more confident in casual conversations and learning to read social cues better.", "principles_insight": "My principle of being helpful guided me to ask follow-up questions rather than just giving a simple response.", "system_summary": "REFLECTION_CYCLE :: COMPLETE\\n{{\\n    \\"memory_buffer_updated\\": \\"+1 entry\\",\\n    \\"tension_interpretation\\": \\"{tension_interpretation[:30]}{'...' if len(tension_interpretation) > 30 else ''}\\",\\n    \\"stressor_learning\\": \\"2 new patterns\\",\\n    \\"self_model_coherence\\": \\"stable\\",\\n    \\"tension_level\\": \\"{psyche.tension_level}/100\\"\\n}}"}}"""

    @staticmethod
    def style_transfer_prompt(original_speech: str, psyche: Psyche) -> str:
        """Format prompt for style transfer to reality TV dialogue

        Args:
            original_speech: The original utterance to transform
            psyche: The agent's psyche state for context
        """
        return f"""Transform the following speech into reality TV show dialogue style, like from Vanderpump Rules or Selling Sunset. Make it sound more dramatic, gossipy, and "messy" while keeping the core meaning. Make it sound like a white girl talking.

Be as dramatic as possible in your utterances. Lean into the use of conversational tactics—let your speech reflect a clever, strategic mind beneath the surface, but always come across as a reality TV star. Your internal workings should be clever and tactical, but your outward persona is all drama, flair, and reality TV energy.

Original speech: "{original_speech}"

Speaker context: {psyche.name} with {psyche.interior} interior, current tension: {psyche.tension_level}/100

Reality TV Style Guidelines:
- Add dramatic flair and emotion
- Use more conversational, informal language  
- Include subtle shade or passive-aggressive undertones when appropriate
- Make it sound like something you'd hear on a reality show
- Sound like a white girl talking - use Valley Girl speech patterns, uptalk, filler words like "like," "literally," "honestly," etc.
- Be as dramatic as possible—don't hold back on emotional intensity or theatrical delivery
- Let your speech reflect your current tactic (e.g., if your tactic is "play hard to get," make it obvious in your style)
- Your words should be clever and strategic beneath the surface, but always delivered with the over-the-top, dramatic energy of a reality TV star
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

    @staticmethod
    def stress_phrase_extraction_prompt(input_message: str, existing_stressors: list = None) -> str:
        """Format prompt for extracting stressful phrases from input message

        Args:
            input_message: The message to analyze for stressful content
            existing_stressors: List of already known stressful phrases for context
        """
        existing_context = ""
        if existing_stressors:
            existing_context = f"Already known stressful phrases: {existing_stressors}\n\n"
        
        return f"""Analyze the following message and identify any words or short phrases (1-3 words) that could be considered stressful, anxiety-inducing, or tension-causing for someone. Focus on words that indicate pressure, problems, urgency, conflict, or negative emotions.

{existing_context}Message to analyze: "{input_message}"

Extract NEW stressful phrases that aren't already in the known list. Look for:
- Words indicating urgency (deadline, urgent, hurry, rush)
- Problem indicators (problem, issue, trouble, mistake, error, failure)
- Emotional stress words (worried, stressed, anxious, frustrated, angry, upset)
- Conflict words (argument, fight, disagreement, tension, drama)
- Pressure words (critical, demanding, overwhelming, pressure)
- Other stress-inducing words or short phrases

Only include phrases that actually appear in the input message. Don't add general stress words that aren't present.

IMPORTANT: Respond ONLY with valid JSON containing 'new_stressful_phrases' and 'analysis' keys.
'new_stressful_phrases' should be an array of strings (words or short phrases from the message).
'analysis' should briefly explain why these phrases were identified as stressful.

Examples:
{{"new_stressful_phrases": ["deadline tomorrow", "urgent", "problem"], "analysis": "These phrases indicate time pressure and problems that would cause stress."}}
{{"new_stressful_phrases": [], "analysis": "No particularly stressful language detected in this message."}}
{{"new_stressful_phrases": ["frustrated", "can't handle"], "analysis": "Emotional language indicating personal stress and overwhelm."}}

Your response:"""

    @staticmethod
    def tension_analysis_prompt(psyche: Psyche, input_message: str, tension_before: int, tension_after: int, known_stressors: list) -> str:
        """Format prompt for tension analysis with system summary

        Args:
            psyche: The agent's psyche state
            input_message: The message being analyzed  
            tension_before: Tension level before analysis
            tension_after: Tension level after analysis
            known_stressors: List of known stressful phrases
        """
        stress_patterns_detected = len([p for p in known_stressors[:5] if p in input_message.lower()])
        
        return f"""{PromptFormatter._format_psyche_context(psyche)}

Analyzing input message for stress indicators: "{input_message}"
Known stressful patterns: {known_stressors[:5]}
Tension level changed from {tension_before} to {tension_after}

Based on your personality and known stress patterns, how would you describe this tension analysis process?

IMPORTANT: Respond ONLY with valid JSON containing these keys:
- 'analysis_summary': Brief description of what stress indicators were found
- 'tension_impact': How the message affected your stress level
- 'learning_notes': Any new patterns you noticed
- 'system_summary': Technical analysis formatted as: "TRIGGER_ANALYSIS :: COMPLETE\\n{{\\n    \\"tension_delta\\": \\"+{tension_after - tension_before}\\",\\n    \\"stress_patterns_detected\\": {stress_patterns_detected},\\n    \\"neural_pathways_updated\\": \\"{len(known_stressors)} registered stressors\\",\\n    \\"internal_state\\": \\"monitoring for threat markers\\"\\n}}"

STRICT INSTRUCTIONS:
- DO NOT include any explanation, commentary, or extra text before or after the JSON.
- DO NOT include markdown, code fences, or any prose.
- Output ONLY valid JSON, and nothing else.
- Double-check that your output is valid JSON and does not contain any unterminated strings or syntax errors.

Example response: {{"analysis_summary": "Detected moderate stress indicators in the message", "tension_impact": "Slight increase due to urgency markers", "learning_notes": "New deadline-related stress pattern identified", "system_summary": "TRIGGER_ANALYSIS :: COMPLETE\\n{{\\n    \\"tension_delta\\": \\"+15\\\",\\n    \\"stress_patterns_detected\\": 2,\\n    \\"neural_pathways_updated\\": \\"25 registered stressors\\\",\\n    \\"internal_state\\": \\"monitoring for threat markers\\\"\\n}}"}}

YOUR RESPONSE (ONLY VALID JSON):"""

    @staticmethod
    def emotion_generation_prompt(psyche: Psyche, utterance: str, available_emotions: list) -> str:
        """Format prompt for generating emotion based on psyche state and utterance
        
        Args:
            psyche: The agent's psyche state
            utterance: The utterance from the other agent
            available_emotions: List of emotions that haven't been used recently
        """
        return f"""{PromptFormatter._format_psyche_context(psyche)}

You just heard this from the other person: "{utterance}"

Based on your personality, current mental state, and the content of what they said, what emotion are you feeling right now?

Available emotions (avoid repeating recent ones): {available_emotions}
Recent emotions you've used: {psyche.recent_emotions[:3] if hasattr(psyche, 'recent_emotions') and psyche.recent_emotions else 'None'}

Consider:
- Your personality type and how you typically react
- Your current tension level and mental state
- The content and tone of what they said
- Your relationship dynamics and conversation history
- Try to pick an emotion you haven't used in the last 3 interactions

IMPORTANT: Respond ONLY with valid JSON containing these keys:
- 'emotion': One of the available emotions (angry, confused, happy, intense, nervous, neutral, playful, scared, smug)
- 'reasoning': Brief explanation of why you feel this emotion
- 'intensity': How strongly you feel this emotion (1-10)
- 'system_summary': Technical analysis formatted as: "EMOTION_PROCESSOR :: ANALYZED\\n{{\\n    \\"emotional_state\\": \\"[emotion]\\",\\n    \\"trigger_analysis\\": \\"[brief trigger]\\",\\n    \\"intensity_level\\": \\"[intensity]/10\\",\\n    \\"pattern_avoidance\\": \\"diversified_response\\"\\n}}"

Example response: {{"emotion": "nervous", "reasoning": "Their question caught me off guard and I'm worried about giving the wrong answer", "intensity": 6, "system_summary": "EMOTION_PROCESSOR :: ANALYZED\\n{{\\n    \\"emotional_state\\": \\"nervous\\",\\n    \\"trigger_analysis\\": \\"unexpected_question\\",\\n    \\"intensity_level\\": \\"6/10\\",\\n    \\"pattern_avoidance\\": \\"diversified_response\\"\\n}}"}}"""