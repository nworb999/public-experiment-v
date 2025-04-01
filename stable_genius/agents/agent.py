from stable_genius.models.psyche import Psyche
from stable_genius.core.decision import DecisionPipeline
from stable_genius.core.components_impl import IntentClassifierComponent

class Agent:
    def __init__(self, name, personality="neutral", custom_pipeline=None):
        self.name = name
        self.personality = personality
        
        # Create pipeline - optionally use custom components
        self.pipeline = DecisionPipeline(personality, components=custom_pipeline)
        
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
    
    def add_component(self, component, position=None):
        """Add a component to the pipeline"""
        self.pipeline.add_component(component, position)
    
    def create_with_intent_classifier(cls, name, personality="neutral"):
        """Factory method to create an agent with intent classification"""
        agent = cls(name, personality)
        # Add intent classifier after observation but before planning
        agent.add_component(IntentClassifierComponent("intent_classifier"), position=1)
        return agent
    
    async def receive_message(self, message: str, sender: str = None):
        """Process a message from another agent or the environment"""
        # Load current psyche state
        psyche = Psyche.load(self.name)
        
        # Add the sender to relationships if not already present
        if sender and sender not in psyche.relationships:
            psyche.relationships[sender] = {"familiarity": 0}
            
        # TODO this is where the environment events are processed
        observation = f"{sender + ': ' if sender else ''}{message}"
        
        # Process through decision pipeline
        response = await self.pipeline.process(observation, psyche)
        
        # Increase familiarity with sender
        if sender in psyche.relationships:
            psyche.relationships[sender]["familiarity"] += 1
            
        # Save updated psyche
        psyche.save()
            
        return response 