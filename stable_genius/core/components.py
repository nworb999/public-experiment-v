import fasttext
import time
import os
from pathlib import Path
import tempfile
import random
import json

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from stable_genius.models.psyche import Psyche
from stable_genius.utils.prompt import PromptFormatter
from stable_genius.utils.llm import OllamaLLM
from stable_genius.core.plan_processor import PlanProcessor
from stable_genius.core.action_processor import ActionProcessor
from stable_genius.utils.logger import logger
from stable_genius.utils.response_processor import process_llm_response_for_json



class PipelineComponent(ABC):
    """Base class for all pipeline components"""
    
    step_title: str = "Component"  # Default step title
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """
        Process input context and return updated context
        
        Args:
            context: The current pipeline context data
            psyche: The agent's psyche state
            
        Returns:
            Updated context dictionary
        """
        pass 

    def _update_step_details(self, context: Dict[str, Any]) -> None:
        """Update context with component's step title and summary"""
        context["step_title"] = self.step_title

        if "summary" in context:
            context["pipeline_summary"] = context["summary"]


class PlanComponent(PipelineComponent):
    """Plans based on observation and psyche state"""
    
    step_title = "Planning"
    
    def __init__(self, name: str, personality: str, llm: OllamaLLM = None):
        super().__init__(name)
        self.llm = llm if llm else OllamaLLM()
        self.personality = personality
        self.processor = PlanProcessor(personality)
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Generate a plan based on observation and psyche state"""
        # Check if psyche already has a plan
        has_plan = psyche.plan is not None and len(psyche.plan) > 0
        
        # Increment tactic counter every round (for tactic switching frequency tracking)
        psyche.increment_tactic_counter()
        
        # Generate appropriate prompt based on whether plan exists
        plan_prompt = PromptFormatter.plan_prompt(psyche)
        
        # Notify before LLM call
        context.update({
            "llm_call_start": True,
            "prompt": plan_prompt
        })
        
        # Generate and process plan
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add agent-specific context to track in LLM interactions
        agent_context = {
            "agent_name": psyche.name,
            "personality": self.personality,
            "component": self.name
        }
        
        # Start time tracking
        start_time = time.time()
        
        raw_plan_response = self.llm.generate(plan_prompt, agent_context)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Notify after LLM call with prompt and response
        context.update({
            "llm_call": True,
            "prompt": plan_prompt,
            "response": raw_plan_response,
            "timestamp": timestamp,
            "elapsed_time": f"{elapsed_time:.2f}",
        })
        
        # Process the plan response based on whether plan exists
        plan_result = self.processor.process(raw_plan_response, has_plan, psyche)
        
        logger.debug(f"Plan processor returned: {plan_result}")
        logger.debug(f"Goal in plan_result: {plan_result.get('goal')}")
        
        if has_plan:
            # If plan exists, we're just updating the active tactic
            if "active_tactic" in plan_result:
                # Use the new method to update tactic and handle counter properly
                psyche.update_active_tactic(plan_result["active_tactic"])
                context.update({
                    "active_tactic": plan_result["active_tactic"],
                    "tactic_rounds": psyche.rounds_since_tactic_change,
                    "summary": plan_result.get("system_summary", f"""PLAN_COMPONENT :: TACTIC_UPDATED
{{
    "selected_tactic": "{plan_result['active_tactic']}",
    "selection_method": "llm_guided",
    "rounds_since_change": {psyche.rounds_since_tactic_change},
    "plan_coherence": "maintained",
    "cognitive_state": "adaptive"
}}""")
                })
        else:
            # If no plan exists, update psyche with new goal and plan
            if "goal" in plan_result:
                logger.debug(f"Updating psyche goal from {psyche.goal} to {plan_result['goal']}")
                psyche.goal = plan_result["goal"]
                logger.debug(f"Updated psyche goal to: {plan_result['goal']}")
            else:
                logger.warning(f"No goal found in plan_result: {plan_result}")
            
            if "plan" in plan_result:
                psyche.plan = plan_result["plan"]
                
            if "active_tactic" in plan_result:
                psyche.update_active_tactic(plan_result["active_tactic"])
            
            # Update context with full plan - ensure goal is included even if None
            context.update({
                "plan": plan_result,
                "goal": plan_result.get("goal"),  # Explicitly include goal in context
                "tactic_rounds": psyche.rounds_since_tactic_change,
                "summary": plan_result.get("system_summary", f"""PLAN_COMPONENT :: GENERATED
{{
    "goal_established": "{plan_result.get('goal', 'undefined')}",
    "tactics_count": {len(plan_result.get('plan', []))},
    "active_tactic": "{plan_result.get('active_tactic', 'none')}",
    "rounds_since_change": {psyche.rounds_since_tactic_change},
    "planning_basis": "interiority_analysis",
    "strategic_coherence": "optimized"
}}""")
            })
        
        self._update_step_details(context)
        return context

class ActionComponent(PipelineComponent):
    """Determines action based on plan, observation, and psyche state"""
    
    step_title = "Action"
    
    def __init__(self, name: str, llm: OllamaLLM = None):
        super().__init__(name)
        self.llm = llm if llm else OllamaLLM()
        self.processor = ActionProcessor()
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Generate an action based on the plan and observation"""
        # Extract observation from context
        observation = context.get("input", context.get("observation", ""))
        
        # Store observation in context for later components
        context["observation"] = observation
        
        # Generate action prompt
        action_prompt = PromptFormatter.act_prompt(psyche, observation)
        
        # Notify before LLM call
        context.update({
            "llm_call_start": True,
            "prompt": action_prompt
        })
        
        # Generate and process action
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add agent-specific context to track in LLM interactions
        agent_context = {
            "agent_name": psyche.name,
            "component": self.name
        }
        
        # Start time tracking
        start_time = time.time()
        
        raw_action_response = self.llm.generate(action_prompt, agent_context)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Notify after LLM call with prompt and response
        context.update({
            "llm_call": True,
            "prompt": action_prompt,
            "response": raw_action_response,
            "timestamp": timestamp,
            "elapsed_time": f"{elapsed_time:.2f}"
        })
        
        action_response = self.processor.process(raw_action_response)
        
        # Ensure action_response has required keys
        if 'action' not in action_response:
            action_response['action'] = 'say'
        if 'speech' not in action_response:
            action_response['speech'] = "I'm not sure what to say right now."
        
        # Store original speech before style transfer
        original_speech = action_response.get("speech", "")
        
        # Apply style transfer to the speech
        styled_speech = await self._apply_style_transfer(original_speech, psyche, context)
        
        # Update action_response with styled speech
        action_response['speech'] = styled_speech
        
        # Update psyche with conversation summary if provided
        if 'conversation_summary' in action_response:
            psyche.update_conversation_memory(action_response['conversation_summary'])
        
        # Update context with action
        context.update({
            "action": action_response,
            "speech": styled_speech,
            "original_speech": original_speech
        })
        
        # Add style transfer details to context
        context["style_transfer"] = {
            "original_speech": original_speech,
            "styled_speech": styled_speech
        }
        
        # Set the dialogue as the summary for this step  
        context["summary"] = action_response.get("system_summary", f"""SPEECH_GENERATION :: PROCESSED
{{
    "dialogue": "{styled_speech}",
    "original_length": "{len(original_speech.split())} tokens",
    "processed_length": "{len(styled_speech.split())} tokens",
    "style_filter": "reality_tv_persona",
    "output_coherence": "optimized"
}}""")
        
        self._update_step_details(context)
        return context
    
    async def _apply_style_transfer(self, original_speech: str, psyche: Psyche, context: Dict[str, Any]) -> str:
        """Apply reality TV style transfer to the original speech"""
        if not original_speech:
            return original_speech
        
        # Generate style transfer prompt
        style_prompt = PromptFormatter.style_transfer_prompt(original_speech, psyche)
        
        # Add agent-specific context to track in LLM interactions
        agent_context = {
            "agent_name": psyche.name,
            "component": f"{self.name}_style_transfer"
        }
        
        try:
            # Start time tracking for style transfer
            start_time = time.time()
            
            raw_style_response = self.llm.generate(style_prompt, agent_context)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Add style transfer LLM call info to context
            context["style_transfer_llm"] = {
                "prompt": style_prompt,
                "response": raw_style_response,
                "elapsed_time": f"{elapsed_time:.2f}"
            }
            
            # Use robust JSON extraction
            style_data = process_llm_response_for_json(raw_style_response)
            styled_speech = style_data.get("styled_speech", original_speech)
            return styled_speech
        except Exception as e:
            logger.error(f"Error in style transfer: {e}")
            return original_speech

class TriggerComponent(PipelineComponent):
    """Classifies input text to detect stressful content using fastText"""
    
    step_title = "Trigger Analysis"
    
    def __init__(self, name: str, model_path: Optional[str] = None, default_stressors: Optional[List[str]] = None, llm: OllamaLLM = None):
        """
        Initialize the trigger component
        
        Args:
            name: Component name
            model_path: Path to pretrained fastText model (if None, will create a simple model)
            default_stressors: List of default stressful phrases to seed the model
            llm: LLM instance for generating system summaries
        """
        super().__init__(name)
        self.llm = llm if llm else OllamaLLM()
        self.model_path = model_path
        self.default_stressors = default_stressors or [
            "deadline", "urgent", "hurry", "problem", "mistake", "failure", 
            "conflict", "argument", "angry", "disappointed", "stressed",
            "critical", "emergency", "crisis", "pressure", "worried"
        ]
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.model = None
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Process input to classify for stress and update psyche's tension level"""
        observation = context.get("observation", "")
        
        # Ensure personalized stressors exist in psyche
        if not hasattr(psyche, "stressful_phrases"):
            # Initialize stressful phrases if not present
            psyche.stressful_phrases = self.default_stressors.copy()
            psyche.save()
            
        # Get or create agent-specific model
        model = self._get_or_create_model(psyche)
        
        # Classify the text
        prediction = self._classify_text(model, observation)
        is_stressful = prediction[0] == 'stress'
        logger.info(f"is_stressful={is_stressful} (label={prediction[0]}, prob={prediction[1]:.3f}) for observation: '{observation}'")
        
        # Update psyche tension level based on classification
        original_tension = psyche.tension_level
        llm_tension_delta = None
        tension_bonus = 0
        try:
            raw_tension_response = self.llm.generate(tension_prompt, agent_context)
            tension_data = process_llm_response_for_json(raw_tension_response)
            system_summary = tension_data.get("system_summary", "")
            # Try to extract tension_delta from system_summary
            import re
            match = re.search(r'"tension_delta"\s*:\s*"([+-]?\d+)', system_summary)
            if match:
                llm_tension_delta = int(match.group(1))
        except Exception as e:
            logger.error(f"Error generating tension analysis summary: {e}")
            system_summary = ""
        # New logic for tension update:
        tension_reason = ""
        if llm_tension_delta is not None:
            if is_stressful:
                # If both LLM and classifier say stressful, amplify
                psyche.tension_level = max(0, min(100, original_tension + llm_tension_delta + 20))
                tension_reason = f"LLM delta ({llm_tension_delta}) + stress bonus (+20)"
            else:
                psyche.tension_level = max(0, min(100, original_tension + llm_tension_delta))
                tension_reason = f"LLM delta ({llm_tension_delta})"
        elif is_stressful:
            psyche.tension_level = min(psyche.tension_level + 20, 100)
            tension_reason = "Stress classifier bonus (+20)"
        else:
            # Small random change to keep tension dynamic
            random_delta = random.randint(-5, 5)
            psyche.tension_level = max(0, min(100, psyche.tension_level + random_delta))
            tension_reason = f"Random delta ({random_delta}) for non-stressful"
        logger.info(f"Tension updated: {original_tension} -> {psyche.tension_level} ({tension_reason})")
        # Clear tension interpretation if tension changed
        if psyche.tension_level != original_tension:
            psyche.tension_interpretation = None
        context["tension_analysis"] = {
            "is_stressful": is_stressful,
            "tension_before": original_tension,
            "tension_after": psyche.tension_level,
            "known_stressors": psyche.stressful_phrases[:5],
            "tension_reason": tension_reason
        }
        context["summary"] = system_summary or f"""TRIGGER_ANALYSIS :: COMPLETE\n{{\n    \"tension_delta\": \"{psyche.tension_level - original_tension:+d}\",\n    \"stress_patterns_detected\": {len([p for p in psyche.stressful_phrases[:5] if p in observation.lower()])},\n    \"neural_pathways_updated\": \"{len(psyche.stressful_phrases)} registered stressors\",\n    \"internal_state\": \"monitoring for threat markers\"\n}}"""
        
        # Generate emotion based on psyche and utterance
        available_emotions = psyche.get_available_emotions()
        emotion_prompt = PromptFormatter.emotion_generation_prompt(psyche, observation, available_emotions)
        
        # Add agent-specific context for emotion generation
        emotion_agent_context = {
            "agent_name": psyche.name,
            "component": f"{self.name}_emotion"
        }
        
        try:
            # Start time tracking for emotion generation
            emotion_start_time = time.time()
            raw_emotion_response = self.llm.generate(emotion_prompt, emotion_agent_context)
            # Calculate elapsed time
            emotion_elapsed_time = time.time() - emotion_start_time
            # Parse the emotion response
            emotion = "neutral"
            emotion_reasoning = "Default emotion due to parsing error"
            emotion_intensity = 5
            emotion_system_summary = ""
            if raw_emotion_response and isinstance(raw_emotion_response, str):
                emotion_data = process_llm_response_for_json(raw_emotion_response)
                emotion = emotion_data.get("emotion", "neutral")
                emotion_reasoning = emotion_data.get("reasoning", "")
                emotion_intensity = emotion_data.get("intensity", 5)
                emotion_system_summary = emotion_data.get("system_summary", "")
            # Update psyche with the new emotion
            psyche.update_emotion(emotion)
            # Add emotion data to context
            context["emotion_analysis"] = {
                "emotion": emotion,
                "reasoning": emotion_reasoning,
                "intensity": emotion_intensity,
                "available_emotions": available_emotions,
                "recent_emotions": psyche.recent_emotions[:3],
                "elapsed_time": f"{emotion_elapsed_time:.2f}"
            }
            # Add emotion LLM call info to context for pipeline tracking
            context["emotion_llm_call"] = {
                "prompt": emotion_prompt,
                "response": raw_emotion_response,
                "elapsed_time": f"{emotion_elapsed_time:.2f}"
            }
            logger.debug(f"Generated emotion for {psyche.name}: {emotion} (intensity: {emotion_intensity}) - {emotion_reasoning}")
        except Exception as e:
            logger.error(f"Error generating emotion for {psyche.name}: {e}")
            # Fallback to neutral emotion
            emotion = "neutral"
            psyche.update_emotion(emotion)
            context["emotion_analysis"] = {
                "emotion": emotion,
                "reasoning": "Fallback due to error",
                "intensity": 5,
                "available_emotions": available_emotions,
                "recent_emotions": psyche.recent_emotions[:3],
                "elapsed_time": "0.00"
            }
        
        # Save updated psyche
        psyche.save()
        
        # Add tension update to context for callback notifications
        context["tension_update"] = {
            "agent_id": getattr(psyche, 'agent_id', None),
            "tension_level": psyche.tension_level,
            "tension_before": original_tension,
            "tension_after": psyche.tension_level
        }
        
        self._update_step_details(context)
        return context
    
    def _get_or_create_model(self, psyche):
        """Get or create a fastText model for this agent"""
        model_file = self.models_dir / f"{psyche.name.lower()}_tension.bin"
        
        if model_file.exists():
            # Load existing model
            return fasttext.load_model(str(model_file))
        else:
            # Create a simple model based on personalized stressors
            return self._create_simple_model(psyche, model_file)
            
    def _create_simple_model(self, psyche, model_file):
        """Create a simple fastText model from stressful phrases"""
        # Create temporary training file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            temp_path = f.name
            
            # Write training examples
            # Format: __label__stress stressful phrase
            # Format: __label__normal neutral phrase
            
            # Write stressful examples
            for phrase in psyche.stressful_phrases:
                f.write(f"__label__stress {phrase}\n")
                
                # Generate some variations
                words = phrase.split()
                if len(words) > 1:
                    for i in range(min(3, len(words))):
                        f.write(f"__label__stress {' '.join(random.sample(words, len(words)))}\n")
            
            # Generate some non-stressful examples
            neutral_phrases = [
                "hello there", "good morning", "how are you", "nice day", 
                "thank you", "appreciate it", "sounds good", "that's interesting",
                "welcome", "have a nice day", "pleased to meet you", "that's helpful",
                "I understand", "makes sense", "I see", "good point"
            ]
            
            for phrase in neutral_phrases:
                f.write(f"__label__normal {phrase}\n")
        
        try:
            # Train the model
            model = fasttext.train_supervised(temp_path, epoch=20, lr=1.0)
            # Save the model
            model.save_model(str(model_file))
            return model
        finally:
            # Clean up temp file
            os.unlink(temp_path)
    
    def _classify_text(self, model, text):
        """Classify text using the fastText model"""
        # Ensure text is a string and preprocess it
        text = str(text).strip()
        if not text:
            return ('normal', 0.0)  # Return no stress for empty text
        try:
            # Return tuple (label, probability)
            prediction = model.predict(text)
            label = prediction[0][0].replace('__label__', '')
            probability = prediction[1][0]
            logger.info(f"fastText classification: label={label}, probability={probability:.3f}, text='{text}'")
            # Lower threshold for stress
            if label == 'stress' and probability >= 0.2:
                return ('stress', probability)
            else:
                return ('normal', probability)
        except ValueError as ve:
            logger.warning(f"NumPy array handling issue in text classification: {ve}")
            return ('normal', 0.0)
        except Exception as e:
            logger.error(f"Unexpected error in text classification for text '{text[:100]}...': {e}")
            return ('normal', 0.0)  # Return no stress on error
    
    def _learn_new_stressors(self, observation, psyche):
        """Learn new stressful phrases from observation"""
        # Simple approach: occasionally sample words from stressful observations
        if random.random() < 0.3:  # 30% chance to learn
            words = observation.split()
            if len(words) > 3:
                # Sample a few words to create a new stressful phrase
                sample_size = min(3, len(words))
                new_stressor = ' '.join(random.sample(words, sample_size))
                
                # Don't add duplicates
                if new_stressor not in psyche.stressful_phrases:
                    psyche.stressful_phrases.append(new_stressor)
                    # Keep list at reasonable size
                    if len(psyche.stressful_phrases) > 50:
                        psyche.stressful_phrases = psyche.stressful_phrases[-50:]

class ReflectComponent(PipelineComponent):
    """Updates the psyche based on plan, action, and observation"""
    
    step_title = "Reflection"
    
    def __init__(self, name: str, llm: OllamaLLM = None):
        super().__init__(name)
        self.llm = llm if llm else OllamaLLM()
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Update psyche based on the planning and action results"""
        # Extract data from context
        input_message = context.get("input", "")
        if not input_message:
            input_message = context.get("observation", "")
        action = context.get("action", {})
        speech = action.get("speech", "")
        
        # Add to memories
        psyche.memories.append(f"{input_message} -> Me: {speech}")
        
        # If action contains a conversation_summary, update the psyche's conversation_memory
        conversation_summary = None
        if action.get("conversation_summary"):
            psyche.update_conversation_memory(action.get("conversation_summary"))
            conversation_summary = action.get("conversation_summary")
        
        # Generate tension interpretation using LLM
        tension_interpretation = await self._interpret_tension(psyche)
        
        # Save the tension interpretation to psyche
        psyche.update_tension_interpretation(tension_interpretation)
        
        # Learn new stressful phrases from input if they seem stressful
        new_stressors_added = await self._learn_stressful_phrases(input_message, psyche)
        
        # Generate reflection prompt
        reflection_prompt = PromptFormatter.reflection_prompt(
            psyche, input_message, action, tension_interpretation, conversation_summary
        )
        
        # Notify before LLM call
        context.update({
            "llm_call_start": True,
            "prompt": reflection_prompt
        })
        
        # Generate reflection summary
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add agent-specific context to track in LLM interactions
        agent_context = {
            "agent_name": psyche.name,
            "component": self.name
        }
        
        # Start time tracking
        start_time = time.time()
        
        raw_reflection_response = self.llm.generate(reflection_prompt, agent_context)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Notify after LLM call with prompt and response
        context.update({
            "llm_call": True,
            "prompt": reflection_prompt,
            "response": raw_reflection_response,
            "timestamp": timestamp,
            "elapsed_time": f"{elapsed_time:.2f}"
        })
        
        # Process reflection response
        try:
            reflection_data = process_llm_response_for_json(raw_reflection_response)
            principles_insight = reflection_data.get("principles_insight", "")
            reflection_summary = principles_insight if principles_insight else "Applied principles to guide response."
            system_summary = reflection_data.get("system_summary", "")
        except Exception as e:
            logger.error(f"Error processing reflection response: {e}")
            reflection_summary = "Applied principles to guide response."
            system_summary = ""
        
        # Add information about new stressors to reflection summary
        if new_stressors_added:
            reflection_summary += f" Added new stressful phrases: {', '.join(new_stressors_added[:5])}"
        
        # Update context with reflection results
        context["reflection"] = {
            "tension_level": tension_interpretation,
            "memory_added": f"{input_message} -> Me: {speech}",
            "conversation_memory": psyche.conversation_memory,
            "new_stressors_added": new_stressors_added
        }

        # Calculate self_model_coherence based on tension level for fallback
        if psyche.tension_level <= 20:
            coherence_state = "optimal"
        elif psyche.tension_level <= 40:
            coherence_state = "stable"
        elif psyche.tension_level <= 60:
            coherence_state = "degrading"
        elif psyche.tension_level <= 80:
            coherence_state = "fragmented"
        else:
            coherence_state = "critical"

        # Use LLM-generated system summary or fallback
        context["summary"] = system_summary or f"""REFLECTION_CYCLE :: COMPLETE
{{
    "memory_buffer_updated": "+1 entry",
    "tension_interpretation": "{tension_interpretation[:30]}{'...' if len(tension_interpretation) > 30 else ''}",
    "stressor_learning": "{len(new_stressors_added)} new patterns",
    "self_model_coherence": "{coherence_state}",
    "tension_level": "{psyche.tension_level}/100"
}}"""
        psyche.save()

        # Make sure step title and summary are updated in context
        self._update_step_details(context)
        
        return context

    async def _learn_stressful_phrases(self, input_message: str, psyche: Psyche) -> List[str]:
        """Learn new stressful phrases from input message using LLM analysis"""
        if not input_message:
            return []
        
        # Ensure stressful_phrases exists
        if not hasattr(psyche, "stressful_phrases"):
            psyche.stressful_phrases = []
        
        # Generate prompt to identify stressful phrases
        stress_analysis_prompt = PromptFormatter.stress_phrase_extraction_prompt(
            input_message, psyche.stressful_phrases[:10]  # Show recent stressors for context
        )
        
        # Add agent-specific context
        agent_context = {
            "agent_name": psyche.name,
            "component": f"{self.name}_stress_analysis"
        }
        
        try:
            # Get LLM response for stress phrase extraction
            raw_response = self.llm.generate(stress_analysis_prompt, agent_context)
            
            # Parse the response
            stress_data = process_llm_response_for_json(raw_response)
            new_phrases = stress_data.get("new_stressful_phrases", [])
            
            # Filter out duplicates and add to psyche (newest first)
            added_phrases = []
            for phrase in new_phrases:
                if phrase and phrase not in psyche.stressful_phrases:
                    # Add to beginning of list (newest first)
                    psyche.stressful_phrases.insert(0, phrase)
                    added_phrases.append(phrase)
            
            # Keep list at reasonable size, removing oldest
            if len(psyche.stressful_phrases) > 50:
                psyche.stressful_phrases = psyche.stressful_phrases[:50]
            
            return added_phrases
        except Exception as e:
            logger.error(f"Error in stress phrase extraction: {e}")
            return []

    async def _interpret_tension(self, psyche: Psyche) -> str:
        """Use LLM to interpret tension level based on agent's interior state"""
        # Get interior state
        interior_summary = psyche.get_interior_summary()
        interior_principles = psyche.get_interior_principles()
        
        # Build interior context
        interior_context = ""
        if interior_summary:
            interior_context += f"Personal narrative: {interior_summary}\n"
        if interior_principles:
            interior_context += f"Guiding principles: {interior_principles}\n"
        
        tension_prompt = f"""You are {psyche.name} with a {psyche.personality} personality.
{interior_context}
Your current tension level is {psyche.tension_level}/100.

Based on your personality, personal narrative, and guiding principles, how would you describe your current emotional/mental state in a few words? Be specific to your character and situation.

Respond with just a brief phrase describing your current state (e.g., "anxiously focused", "calmly determined", "overwhelmed but pushing through", etc.)"""

        # Add agent-specific context
        agent_context = {
            "agent_name": psyche.name,
            "component": f"{self.name}_tension_interpretation"
        }
        
        try:
            tension_interpretation = self.llm.generate(tension_prompt, agent_context)
            # Clean up the response (remove quotes, newlines, etc.)
            return tension_interpretation.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"Error interpreting tension for {psyche.name}: {e}")
            # Fallback to simple description
            if psyche.tension_level <= 20:
                return "calm and composed"
            elif psyche.tension_level <= 60:
                return "moderately tense"
            else:
                return "highly stressed"

class IntentClassifierComponent(PipelineComponent):
    """Classifies user intent from input text"""

    step_title = "Intent Classification"
    
    def __init__(self, name: str, llm: OllamaLLM = None):
        super().__init__(name)
        self.llm = llm if llm else OllamaLLM()
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Classify intent of the input and add to context"""
        last_message = context.get("input", "")
        
        conversation_history = psyche.memories[-10:] if psyche.memories else []

        # Generate intent classification prompt
        prompt = PromptFormatter.intent_classification_prompt(last_message, conversation_history)
        
        # Notify before LLM call
        context.update({
            "llm_call_start": True,
            "prompt": prompt
        })
        
        # Add agent-specific context to track in LLM interactions
        agent_context = {
            "agent_name": psyche.name,
            "component": self.name
        }
        
        # Generate classification response
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Start time tracking
        start_time = time.time()
        
        raw_response = self.llm.generate(prompt, agent_context)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Notify after LLM call with prompt and response
        context.update({
            "llm_call": True,
            "prompt": prompt,
            "response": raw_response,
            "timestamp": timestamp,
            "elapsed_time": f"{elapsed_time:.2f}"
        })
        
        try:
            # Extract JSON or create default
            parsed_data = process_llm_response_for_json(raw_response)
            # Validate that required keys exist and capture additional keys
            intent_data = {
                "intent": parsed_data.get("intent", "other"),
                "confidence": parsed_data.get("confidence", 50),
                "summary": parsed_data.get("summary", "No summary provided"),
                "emotional_tone": parsed_data.get("emotional_tone", "neutral"),
                "urgency": parsed_data.get("urgency", "low"),
                "category": parsed_data.get("category", "general")
            }
            system_summary = parsed_data.get("system_summary", "")
        except Exception as e:
            logger.error(f"Error processing intent classification: {e}")
            intent_data = {
                "intent": "other", 
                "confidence": 50,
                "summary": "No summary provided",
                "emotional_tone": "neutral",
                "urgency": "low",
                "category": "general"
            }
            system_summary = ""
            
        # Add to context
        context["intent"] = intent_data
        context["summary"] = system_summary or f"""INTENT_PARSER :: ANALYZED
{{
    "classification": "{intent_data['intent']}",
    "confidence_score": "{intent_data['confidence']}%",
    "emotional_vector": "{intent_data['emotional_tone']}",
    "urgency_level": "{intent_data['urgency']}",
    "processing_context": "{intent_data['category']}_domain"
}}"""

        self._update_step_details(context)
        return context 