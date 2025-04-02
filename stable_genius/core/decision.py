import json
import logging
from typing import List, Dict, Any, Callable, Optional
from stable_genius.models.psyche import Psyche
from stable_genius.core.components import PipelineComponent
from stable_genius.utils.logger import logger

class DecisionPipeline:
    """Manages the agent's decision-making process using composable components"""
    
    def __init__(self, personality: str = "neutral", components: Optional[List[PipelineComponent]] = None):
        """
        Initialize the decision pipeline
        
        Args:
            personality: The agent's personality trait
            components: List of pipeline components in processing order (if None, default pipeline is created)
        """
        self.personality = personality
        self.callbacks = []
        self.components = components or self._create_default_pipeline()
        
    def _create_default_pipeline(self) -> List[PipelineComponent]:
        """Create the default pipeline components when none are provided"""
        from stable_genius.core.components import ObserveComponent, PlanComponent, ActionComponent, ReflectComponent
        
        return [
            ObserveComponent("observe"),
            PlanComponent("plan", self.personality),
            ActionComponent("action"),
            ReflectComponent("reflect")
        ]
    
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
        
        # Process through each component
        for component in self.components:
            try:
                # Notify start of component processing
                self.notify_callbacks(f"{component.name}_start", context)
                
                # Process through component
                context = await component.process(context, psyche)
                
                # Notify completion of component processing
                self.notify_callbacks(component.name, context)
                
            except Exception as e:
                logger.error(f"Error in pipeline component {component.name}: {e}")
                context[f"{component.name}_error"] = str(e)
        
        # Notify complete cycle
        self.notify_callbacks("complete", {"result": context})
        
        return context
    
    async def react_cycle(self, observation: str, psyche: Psyche) -> Dict[str, Any]:
        """
        Legacy method for compatibility with existing code
        
        Args:
            observation: Initial observation input
            psyche: The agent's psyche state
            
        Returns:
            Dictionary with legacy format results
        """
        result = await self.process(observation, psyche)
        
        # Format for backwards compatibility
        return {
            "speech": result.get("speech", "I don't know what to say."),
            "plan": result.get("plan", {}),
            "action": result.get("action", {"action": "say", "speech": "No action determined."})
        } 