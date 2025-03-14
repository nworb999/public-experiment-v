from stable_genius.agents.agent import Agent
from stable_genius.models.psyche import Psyche

class Personality:
    """Base class for all personality types"""
    def configure_psyche(self, psyche):
        """Apply personality-specific configurations to a psyche"""
        pass
    
    def get_type(self):
        """Return the personality type name"""
        return self.type

class FriendlyPersonality(Personality):
    def __init__(self):
        self.type = "friendly"
        
    def configure_psyche(self, psyche):
        psyche.tension_level = 20  # Starts relaxed
        # You could add more friendly-specific configurations here

class AnalyticalPersonality(Personality):
    def __init__(self):
        self.type = "analytical"
        
    def configure_psyche(self, psyche):
        psyche.tension_level = 40  # Starts slightly tense
        # You could add more analytical-specific configurations here

# Factory function to create agents with specific personalities
def create_agent(name, personality_type):
    """Create an agent with a specific personality type"""
    # Create the base agent
    agent = Agent(name, personality=personality_type)
    
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

# Usage examples:
# friendly_agent = create_agent("Bob", "friendly")
# analytical_agent = create_agent("Alice", "analytical")
