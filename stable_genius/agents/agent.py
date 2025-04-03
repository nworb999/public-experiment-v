from stable_genius.models.psyche import Psyche
from stable_genius.core.decision import DecisionPipeline
from stable_genius.core.components import IntentClassifierComponent, TensionClassifierComponent
from stable_genius.utils.llm import OllamaLLM

class Agent:
    def __init__(self, name, personality="neutral", llm=None, custom_pipeline=None):
        self.name = name
        self.personality = personality
        
        # Store shared LLM instance
        self.llm = llm if llm else OllamaLLM()
        
        # Create pipeline - optionally use custom components
        self.pipeline = DecisionPipeline(personality, llm=self.llm, components=custom_pipeline)
        
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
    
    @classmethod
    def create_with_tension_classifier(cls, name, personality="neutral", llm=None, initial_stressors=None):
        """Factory method to create an agent with tension classification"""
        agent = cls(name, personality, llm)
        # Add tension classifier after observation but before planning
        agent.add_component(TensionClassifierComponent("tension_classifier", 
                                                     default_stressors=initial_stressors), 
                          position=1)
        return agent
    
    @classmethod
    def create_full_pipeline(cls, name, personality="neutral", llm=None, initial_stressors=None):
        """Factory method to create an agent with tension classifier"""
        agent = cls(name, personality, llm)
        # Add tension classifier
        agent.add_component(TensionClassifierComponent("tension_classifier", 
                                                     default_stressors=initial_stressors), 
                          position=1)
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