from stable_genius.agents.agent import Agent
from stable_genius.models.psyche import Psyche

class Personality:
    """Base class for all personality types"""
    def __init__(self):
        self.stressful_phrases = [
            "deadline", "urgent", "hurry", "problem", "mistake", "failure",
            "conflict", "argument", "angry", "disappointed"
        ]
        
    def configure_psyche(self, psyche):
        """Apply personality-specific configurations to a psyche"""
        psyche.stressful_phrases = self.stressful_phrases
    
    def get_type(self):
        """Return the personality type name"""
        return self.type

class FriendlyPersonality(Personality):
    def __init__(self):
        super().__init__()
        self.type = "friendly"
        
        # Friendly personality stressors - focused on social tension and conflict
        self.stressful_phrases = [
            "conflict", "argument", "disagree", "angry", "disappointed", 
            "rejected", "criticized", "ignored", "disrespected", "rude",
            "unfriendly", "hostile", "mean", "upset", "hurt feelings",
            "misunderstood", "alone", "isolated", "abandoned", "betrayed"
        ]
        
    def configure_psyche(self, psyche):
        super().configure_psyche(psyche)
        # Don't hardcode tension level - let it evolve naturally

class AnalyticalPersonality(Personality):
    def __init__(self):
        super().__init__()
        self.type = "analytical"
        
        # Analytical personality stressors - focused on uncertainty and errors
        self.stressful_phrases = [
            "uncertain", "unclear", "ambiguous", "imprecise", "approximate", 
            "error", "mistake", "incorrect", "flawed", "bug", "problem",
            "lacking data", "insufficient", "unverified", "unreliable",
            "inconsistent", "illogical", "irrational", "failure", "deadline",
            "incomplete", "inefficient", "complex", "chaotic", "unpredictable"
        ]
        
    def configure_psyche(self, psyche):
        super().configure_psyche(psyche)
        # Don't hardcode tension level - let it evolve naturally

# Factory function to create agents with specific personalities
def create_agent(name, personality_type, llm=None):
    """Create an agent with a specific personality type"""
    # Create the base agent
    agent = Agent(name, personality=personality_type, llm=llm)
    
    # Create and apply the appropriate personality
    personality = None
    if personality_type == "friendly":
        personality = FriendlyPersonality()
    elif personality_type == "analytical":
        personality = AnalyticalPersonality()
    
    # Load and configure the psyche if we have a valid personality
    if personality:
        psyche = Psyche.load(name)
        personality.configure_psyche(psyche)
        psyche.save()
    
    return agent

