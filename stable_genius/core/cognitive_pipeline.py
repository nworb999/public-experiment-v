import json
import logging
from typing import List, Dict, Any, Callable, Optional
from stable_genius.models.psyche import Psyche
from stable_genius.core.components import (
    PipelineComponent,
    TriggerComponent,
    IntentClassifierComponent, 
    PlanComponent, 
    ActionComponent, 
    ReflectComponent
)
from stable_genius.utils.llm import OllamaLLM
from stable_genius.utils.logger import logger

class CognitivePipeline:
    """Manages the agent's cognitive-making process using composable components"""
    
    def __init__(self, personality: str = "neutral", llm=None, components: Optional[List[PipelineComponent]] = None):
        """
        Initialize the cognitive pipeline
        
        Args:
            personality: The agent's personality trait
            llm: Shared LLM instance to use for all components
            components: List of pipeline components in processing order (if None, default pipeline is created)
        """
        self.personality = personality
        self.llm = llm if llm else OllamaLLM()
        self.callbacks = []
        
        if components is None:
            logger.info("Creating default pipeline components")
            components = [
                TriggerComponent("trigger"),
                IntentClassifierComponent("classify-intent"),
                PlanComponent("plan", self.personality, self.llm),
                ActionComponent("action", self.llm),
                ReflectComponent("reflect")
            ]
            for component in components:
                logger.info(f"Added component: {component.name}")
                
        self.components = components
    
    def add_component(self, component: PipelineComponent, position: Optional[int] = None) -> None:
        """
        Add a component to the pipeline
        
        Args:
            component: The component to add
            position: Position to insert (None to append)
        """
        if position is None:
            self.components.append(component)
        else:
            self.components.insert(position, component)
    
    def register_callback(self, callback: Callable):
        """Register a callback function to receive pipeline updates
        
        The callback should accept (stage_name, data) parameters
        """
        self.callbacks.append(callback)
    
    def notify_callbacks(self, stage: str, data: Dict[str, Any]) -> None:
        """Notify all registered callbacks with pipeline stage updates"""
        logger.info(f"Pipeline stage: {stage}")
        for callback in self.callbacks:
            try:
                callback(stage, data)
            except Exception as e:
                logger.error(f"Error in pipeline callback: {e}")
    
    async def process(self, observation: str, psyche: Psyche) -> Dict[str, Any]:
        """
        Process through all pipeline components
        
        Args:
            observation: Initial observation input
            psyche: The agent's psyche state
            
        Returns:
            Final pipeline context containing results
        """
        # Initialize context with observation
        context = {"input": observation, "personality": self.personality}
        logger.info(f"Starting pipeline processing for {psyche.name}")
        
        # Process through each component
        for component in self.components:
            try:
                # Notify start of component processing
                self.notify_callbacks(f"{component.name}_start", context)
                
                # Process through component
                context = await component.process(context, psyche)
                
                # Check if an LLM call was made during component processing
                if context.get("llm_call"):
                    # Notify about LLM call
                    llm_data = {
                        "prompt": context.get("prompt", ""),
                        "response": context.get("response", ""),
                        "timestamp": context.get("timestamp", ""),
                        "component": component.name,
                        "elapsed_time": context.get("elapsed_time", ""),
                        "step_title": context.get("step_title", "")
                    }
                    # Pass the data to callbacks for further processing
                    self.notify_callbacks("llm_call", llm_data)
                    
                    # Clear LLM call flags to prevent duplicate notifications
                    context.pop("llm_call", None)
                    context.pop("llm_call_start", None)
                
                # Notify completion of component processing
                self.notify_callbacks(component.name, context)
                
            except Exception as e:
                logger.error(f"Error in pipeline component {component.name}: {e}")
                context[f"{component.name}_error"] = str(e)
        
        # Notify complete cycle
        logger.info(f"Pipeline processing complete for {psyche.name}")
        self.notify_callbacks("complete", {"result": context})
        
        return context
    