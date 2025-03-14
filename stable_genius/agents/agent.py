from stable_genius.models.psyche import Psyche
from stable_genius.core.decision import DecisionPipeline

class Agent:
    def __init__(self, name, personality="neutral"):
        self.name = name
        self.personality = personality
        self.pipeline = DecisionPipeline(personality)
        
        # Load or initialize the psyche
        psyche = Psyche.load(name)
        
        # Update personality if different
        if psyche.personality != personality:
            psyche.personality = personality
            
        # Ensure actions are set
        if not psyche.pending_actions:
            psyche.pending_actions = ["say", "ask", "express", "confront", "cooperate"]
            
        # Save any changes
        psyche.save()
    
    def get_psyche(self):
        """Get the current psyche state"""
        return Psyche.load(self.name)
    
    async def receive_message(self, message: str, sender: str = None):
        """Process a message from another agent or the environment"""
        # Load current psyche state
        psyche = Psyche.load(self.name)
        
        # Add the sender to relationships if not already present
        if sender and sender not in psyche.relationships:
            psyche.relationships[sender] = {"familiarity": 0}
            
        observation = f"{sender + ': ' if sender else ''}{message}"
        
        # Process through decision pipeline
        response = await self.pipeline.react_cycle(observation, psyche)
        
        # Increase familiarity with sender
        if sender in psyche.relationships:
            psyche.relationships[sender]["familiarity"] += 1
            
        # Save updated psyche
        psyche.save()
            
        return response 