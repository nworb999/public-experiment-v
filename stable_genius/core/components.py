from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from stable_genius.models.psyche import Psyche
from stable_genius.utils.logger import logger

class PipelineComponent(ABC):
    """Base class for all pipeline components"""
    
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