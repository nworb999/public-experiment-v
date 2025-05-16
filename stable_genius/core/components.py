import fasttext
import time
import os
from pathlib import Path
import tempfile
import random

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from stable_genius.models.psyche import Psyche
from stable_genius.utils.prompt import PromptFormatter
from stable_genius.utils.llm import OllamaLLM
from stable_genius.core.plan_processor import PlanProcessor
from stable_genius.core.action_processor import ActionProcessor
from stable_genius.utils.logger import logger



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
        plan_result = self.processor.process(raw_plan_response, has_plan)
        
        if has_plan:
            # If plan exists, we're just updating the active tactic
            if "active_tactic" in plan_result:
                psyche.active_tactic = plan_result["active_tactic"]
                context.update({
                    "active_tactic": plan_result["active_tactic"],
                    "summary": plan_result.get("summary", "No summary provided for tactic selection")
                })
        else:
            # If no plan exists, update psyche with new goal and plan
            if "goal" in plan_result:
                psyche.goal = plan_result["goal"]
            
            if "plan" in plan_result:
                psyche.plan = plan_result["plan"]
                
            if "active_tactic" in plan_result:
                psyche.active_tactic = plan_result["active_tactic"]
            
            # Update context with full plan
            context.update({
                "plan": plan_result,
                "summary": plan_result.get("summary", "No summary provided for plan creation")
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
        
        # Update psyche with conversation summary if provided
        if 'conversation_summary' in action_response:
            psyche.update_conversation_memory(action_response['conversation_summary'])
        
        # Update context with action
        context.update({
            "action": action_response,
            "speech": action_response.get("speech")
        })
        
        self._update_step_details(context)
        return context

class ReflectComponent(PipelineComponent):
    """Updates the psyche based on plan, action, and observation"""
    
    def __init__(self, name: str):
        super().__init__(name)
        
    async def process(self, context: Dict[str, Any], psyche: Psyche) -> Dict[str, Any]:
        """Update psyche based on the planning and action results"""
        # Extract data from context
        input_message = context.get("input", "")
        if not input_message:
            input_message = context.get("observation", "")
        action = context.get("action", {})
        speech = action.get("speech", "")
        action_type = action.get("action", "say")
        
        # Add to memories
        psyche.memories.append(f"{input_message} -> {speech}")
        
        # If action contains a conversation_summary, update the psyche's conversation_memory
        if action.get("conversation_summary"):
            psyche.update_conversation_memory(action.get("conversation_summary"))
        
        # Update context with reflection results
        context["reflection"] = {
            "tension_level": psyche.tension_level,
            "memory_added": f"{input_message} -> {speech}",
            "conversation_memory": psyche.conversation_memory
        }

        # Add cognitive process summary
        context["summary"] = "Reflected on the conversation and updated memories and tension level."

        # Make sure step title and summary are updated in context
        self._update_step_details(context)
        
        return context
        

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
        context["summary"] = f"Classified intent as {intent_data['intent']} with confidence {intent_data['confidence']}%"

        self._update_step_details(context)
        return context

class TriggerComponent(PipelineComponent):
    """Classifies input text to detect stressful content using fastText"""
    
    step_title = "Trigger Analysis"
    
    def __init__(self, name: str, model_path: Optional[str] = None, default_stressors: Optional[List[str]] = None):
        """
        Initialize the trigger component
        
        Args:
            name: Component name
            model_path: Path to pretrained fastText model (if None, will create a simple model)
            default_stressors: List of default stressful phrases to seed the model
        """
        super().__init__(name)
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
        stress_score = prediction[1]  # Confidence score
        
        # Update psyche tension level based on stress score
        original_tension = psyche.tension_level
        if stress_score > 0.7:  # High confidence of stress
            # Increase tension more significantly
            psyche.tension_level = min(psyche.tension_level + int(stress_score * 20), 100)
            
            # Potentially learn new stressful phrases
            self._learn_new_stressors(observation, psyche)
            
        elif stress_score > 0.5:  # Medium confidence
            # Mild tension increase
            psyche.tension_level = min(psyche.tension_level + int(stress_score * 10), 100)
            
        # Add results to context
        context["tension_analysis"] = {
            "is_stressful": stress_score > 0.5,
            "stress_score": stress_score,
            "tension_before": original_tension,
            "tension_after": psyche.tension_level,
            "known_stressors": psyche.stressful_phrases[:5]  # Sample of known stressors
        }

        context["summary"] = f"Analyzed tension level based on stress score {stress_score}, known stressful phrases {psyche.stressful_phrases[:5]}"
        
        # Save updated psyche
        psyche.save()
        
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
            return ('stress', 0.0)  # Return no stress for empty text
            
        try:
            # Return tuple (label, probability)
            prediction = model.predict(text)
            label = prediction[0][0].replace('__label__', '')
            probability = prediction[1][0]
            
            # If normal, return inverted probability
            if label == 'normal':
                return ('stress', 1.0 - probability)
            return ('stress', probability)
        except ValueError as ve:
            # Handle numpy array copy issues
            logger.warning(f"NumPy array handling issue in text classification: {ve}")
            return ('stress', 0.0)
        except Exception as e:
            logger.error(f"Unexpected error in text classification for text '{text[:100]}...': {e}")
            return ('stress', 0.0)  # Return no stress on error
    
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