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
    # Create the base agent with the exact personality type passed in
    agent = Agent(name, personality=personality_type, llm=llm)
    
    # Load psyche to get premise data that might already be stored
    psyche = Psyche.load(name)
    
    # Configure stress phrases based on hero tropes and hidden flaws from premise data
    stress_phrases = []
    
    # Use hero trope to determine base stress patterns
    hero_trope = getattr(psyche, 'hero_trope', None)
    if hero_trope:
        hero_stress_patterns = {
            "Anti-Hero": ["moral dilemma", "compromise", "judgement", "expectations"],
            "The Hero": ["innocent harm", "failure", "corruption", "betrayal of trust"],
            "The Chosen One": ["inadequacy", "destiny", "burden", "isolation"],
            "Mentor": ["student failure", "responsibility", "legacy", "wisdom questioned"],
            "Sidekick": ["abandonment", "uselessness", "ignored", "overshadowed"],
            "Heart of Gold": ["vulnerability", "exposed", "taken advantage", "soft"],
            "Polite Hero": ["rudeness", "conflict", "confrontation", "discourtesy"],
            "Reluctant Hero": ["spotlight", "attention", "responsibility", "expectations"],
            "Hunter of Truth": ["deception", "lies", "cover-up", "misinformation"],
            "Protector": ["harm to others", "failure to protect", "vulnerability"],
            "Underdog": ["dismissal", "underestimation", "impossible odds"],
            "Team Player": ["team conflict", "division", "selfishness", "betrayal"],
            "Idealist": ["corruption", "compromise", "pragmatism", "cynicism"]
        }
        stress_phrases.extend(hero_stress_patterns.get(hero_trope, []))
    
    # Use hidden flaws to add specific stress triggers
    hidden_flaws = getattr(psyche, 'hidden_flaws', [])
    if hidden_flaws:
        flaw_stress_patterns = {
            "Arrogant": ["humiliation", "proven wrong", "outsmarted", "belittled"],
            "Backstabbing": ["loyalty", "trust", "alliance", "exposure"],
            "Blatant Liar": ["fact checking", "verification", "truth", "exposed"],
            "Bossy": ["insubordination", "ignored", "challenged", "disobeyed"],
            "Chronic Backstager": ["transparency", "openness", "direct confrontation"],
            "Conflict Ball": ["peace", "harmony", "agreement", "calm"],
            "Cowardly": ["danger", "confrontation", "courage", "bravery"],
            "Crybaby": ["criticism", "harsh words", "rejection", "coldness"],
            "Drama Queen": ["ignored", "mundane", "ordinary", "overlooked"],
            "Flaky": ["commitment", "reliability", "consistency", "dependability"],
            "Greedy": ["sharing", "generosity", "loss", "giving up"],
            "Hot-Blooded": ["patience", "calm", "restraint", "control"],
            "Lazy": ["work", "effort", "energy", "productivity"],
            "Manipulative": ["honest", "direct", "transparent", "genuine"],
            "Narcissist": ["criticism", "ignored", "irrelevant", "unimportant"],
            "Needy": ["independence", "alone", "self-reliance", "rejection"],
            "Poor Communication Kills": ["clarity", "understanding", "precision"],
            "Sore Loser": ["losing", "defeat", "failure", "second place"],
            "Stubborn": ["flexibility", "compromise", "change", "adaptation"],
            "Vain": ["ugliness", "appearance", "image", "unflattering"]
        }
        
        for flaw in hidden_flaws:
            stress_phrases.extend(flaw_stress_patterns.get(flaw, []))
    
    # Add general stress phrases if no premise data available
    if not stress_phrases:
        stress_phrases = [
            "deadline", "urgent", "hurry", "problem", "mistake", "failure",
            "conflict", "argument", "angry", "disappointed"
        ]
    
    # Remove duplicates and apply to psyche
    psyche.stressful_phrases = list(set(stress_phrases))
    psyche.save()
    
    return agent

