from stable_genius.models.psyche import Psyche
from stable_genius.core.cognitive_pipeline import CognitivePipeline
from stable_genius.utils.llm import OllamaLLM

class Agent:
    def __init__(self, name, personality="neutral", llm=None, custom_pipeline=None):
        self.name = name
        self.personality = personality
        
        # Store shared LLM instance
        self.llm = llm if llm else OllamaLLM()
        
        # Create pipeline - optionally use custom components
        self.pipeline = CognitivePipeline(personality, llm=self.llm, components=custom_pipeline)
        
        # Load or initialize the psyche
        psyche = Psyche.load(name)
        
        # Update personality if different
        if psyche.personality != personality:
            psyche.personality = personality
            
        # Ensure actions are set
        if not psyche.pending_actions:
            psyche.pending_actions = ["say", "ask", "express", "confront", "cooperate"]
        
        # Initialize plan and active tactic if missing
        if not psyche.plan:
            if "friendly" in personality:
                psyche.plan = ["friendly conversation", "show empathy"]
            elif "analytical" in personality:
                psyche.plan = ["ask targeted questions", "analyze responses"]
            else:
                psyche.plan = ["balanced dialogue"]
                
            # Set first tactic as active
            if psyche.plan and not psyche.active_tactic:
                psyche.active_tactic = psyche.plan[0]
            
        # Save any changes
        psyche.save()
    
    def get_psyche(self):
        """Get the current psyche state"""
        return Psyche.load(self.name)
    
    def add_component(self, component, position=None):
        """Add a component to the pipeline"""
        self.pipeline.add_component(component, position)
    
    def update_active_tactic(self, new_tactic):
        """Update the active tactic for this agent"""
        psyche = Psyche.load(self.name)
        
        # Check if tactic is in plan
        if psyche.plan and new_tactic in psyche.plan:
            psyche.active_tactic = new_tactic
            psyche.save()
            return True
        
        # If tactic is not in plan, don't update
        return False
    
    async def receive_message(self, message: str, sender: str = None):
        """Process a message from another agent or the environment"""
        # Load current psyche state
        psyche = Psyche.load(self.name)
        
        # Add the sender to relationships if not already present
        if sender and sender not in psyche.relationships:
            psyche.relationships[sender] = {"familiarity": 0}
            
        observation = f"{sender + ': ' if sender else ''}{message}"
        
        # Process through cognitive pipeline
        response = await self.pipeline.process(observation, psyche)
        
        # Increase familiarity with sender
        if sender in psyche.relationships:
            psyche.relationships[sender]["familiarity"] += 1
            
        # Save updated psyche
        psyche.save()
            
        return response 