from stable_genius.models.psyche import Psyche
from stable_genius.core.cognitive_pipeline import CognitivePipeline
from stable_genius.utils.llm import OllamaLLM

class Agent:
    def __init__(self, name, personality="neutral", llm=None, custom_pipeline=None):
        self.name = name
        self.personality = personality
        
        # Store shared LLM instance
        self.llm = llm if llm else OllamaLLM(use_local=False)
        
        # Create pipeline - optionally use custom components
        self.pipeline = CognitivePipeline(personality, llm=self.llm, components=custom_pipeline)
        
        # Load or initialize the psyche
        psyche = Psyche.load(name)
        
        # Initialize interior if not already set
        if not hasattr(psyche, "interior") or not isinstance(psyche.interior, dict):
            psyche.interior = {"summary": "", "principles": ""}
        
        # Generate interior based on new premise data if available
        if not psyche.interior.get("summary") or not psyche.interior.get("principles"):
            self._generate_interior_from_premise(psyche)
        
        # Update personality if different
        if psyche.personality != personality:
            psyche.personality = personality
        
        # Don't initialize hardcoded plans - let them be generated based on psyche
        # Plans should be dynamically generated based on interior state in the planning component
            
        # Save any changes
        psyche.save()
    
    def _generate_interior_from_premise(self, psyche):
        """Generate interior summary and principles from premise data"""
        # Check if we have premise data to work with
        hero_trope = getattr(psyche, 'hero_trope', None)
        hero_description = getattr(psyche, 'hero_description', None)
        hidden_flaws = getattr(psyche, 'hidden_flaws', [])
        premise_interpretation = getattr(psyche, 'premise_interpretation', None)
        
        if hero_trope and hero_description:
            # Generate principles based on hero trope
            psyche.interior["principles"] = f"I am {hero_trope.lower()} - {hero_description}"
            
            # Generate summary combining hero identity, hidden flaws, and premise interpretation
            summary_parts = [f"I see myself as {hero_trope.lower()} who {hero_description}"]
            
            if premise_interpretation:
                # Clean up the premise interpretation text
                clean_interpretation = premise_interpretation.strip()
                if clean_interpretation.endswith('.'):
                    clean_interpretation = clean_interpretation[:-1]
                summary_parts.append(f"In this situation, {clean_interpretation.lower()}")
            
            if hidden_flaws:
                # Convert flaws to more subtle interior narrative
                flaw_influences = []
                for flaw in hidden_flaws[:2]:  # Limit to first 2 flaws to keep it concise
                    if flaw == "Arrogant":
                        flaw_influences.append("I know I'm usually right about things")
                    elif flaw == "Backstabbing":
                        flaw_influences.append("I believe in strategic thinking")
                    elif flaw == "Blatant Liar":
                        flaw_influences.append("I shape truth to serve the greater good")
                    elif flaw == "Bossy":
                        flaw_influences.append("I naturally take charge when others hesitate")
                    elif flaw == "Conflict Ball":
                        flaw_influences.append("I'm passionate about my convictions")
                    elif flaw == "Cowardly":
                        flaw_influences.append("I prefer calculated approaches to risk")
                    elif flaw == "Drama Queen":
                        flaw_influences.append("I understand the importance of making moments significant")
                    elif flaw == "Flaky":
                        flaw_influences.append("I adapt flexibly to changing circumstances")
                    elif flaw == "Greedy":
                        flaw_influences.append("I believe in maximizing opportunities")
                    elif flaw == "Hot-Blooded":
                        flaw_influences.append("I act with passionate intensity")
                    elif flaw == "Lazy":
                        flaw_influences.append("I value efficiency and smart work")
                    elif flaw == "Manipulative":
                        flaw_influences.append("I understand how to influence situations")
                    elif flaw == "Narcissist":
                        flaw_influences.append("I recognize my own importance")
                    elif flaw == "Needy":
                        flaw_influences.append("I value connection and validation")
                    elif flaw == "Stubborn":
                        flaw_influences.append("I stand firm in my principles")
                    elif flaw == "Vain":
                        flaw_influences.append("I care about how I'm perceived")
                
                if flaw_influences:
                    if len(flaw_influences) == 1:
                        summary_parts.append(f"Deep down, {flaw_influences[0]}")
                    else:
                        summary_parts.append(f"Deep down, {flaw_influences[0]} and {flaw_influences[1]}")
            
            psyche.interior["summary"] = ". ".join(summary_parts) + "."
        else:
            # Fallback for agents without premise data
            psyche.interior["principles"] = f"A {self.personality} individual navigating complex situations"
            psyche.interior["summary"] = f"I approach life with a {self.personality} perspective, trying to do what seems right in each moment."
    
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