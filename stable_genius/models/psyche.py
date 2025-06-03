from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
from pathlib import Path
from stable_genius.utils.logger import logger

class Psyche(BaseModel):
    """Maintains agent's mental state and history"""
    memories: List[str] = []
    conversation_memory: str = ""  # Summary of how the conversation is going
    relationships: Dict[str, Dict] = {}  # Entity -> relationship metadata
    goal: Optional[str] = None
    plan: Optional[List[str]] = None  # Tactics list
    active_tactic: Optional[str] = None  # Currently active tactic
    rounds_since_tactic_change: int = 0  # Counter for tactic switching frequency
    tension_level: int = 0  # 0-100 stress meter
    tension_interpretation: Optional[str] = None  # LLM-generated description of tension
    personality: str = "neutral"  # Default personality
    name: str = "Agent"  # Agent name
    stressful_phrases: List[str] = []  # Personalized list of stressful phrases
    interior: Dict[str, Any] = {"summary": "", "principles": ""}  # New aspect for agent's interior
    recent_emotions: List[str] = []  # Track recent emotions to avoid repetition
    
    @classmethod
    def load(cls, agent_name: str):
        """Load psyche from JSON file"""
        # Create db directory if it doesn't exist
        db_dir = Path("db")
        db_dir.mkdir(exist_ok=True)
        
        # Define the filepath for this agent
        filepath = db_dir / f"{agent_name.lower()}.json"
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                # If plan is present but not active_tactic, set first tactic as active
                psyche = cls(**data)
                if psyche.plan and len(psyche.plan) > 0 and not psyche.active_tactic:
                    psyche.active_tactic = psyche.plan[0]

                return psyche
            except (json.JSONDecodeError, IOError) as e:
                logger.info(f"Error loading psyche for {agent_name}: {e}")
                # Fall back to a new instance with the provided name
                return cls(name=agent_name)
        else:
            # Create a new psyche if no file exists
            return cls(name=agent_name)
    
    def save(self):
        """Save psyche to JSON file"""
        # Create db directory if it doesn't exist
        db_dir = Path("db")
        db_dir.mkdir(exist_ok=True)
        
        # Define the filepath for this agent
        filepath = db_dir / f"{self.name.lower()}.json"
        
        try:
            with open(filepath, 'w') as f:
                f.write(self.model_dump_json(indent=2))
        except IOError as e:
            logger.info(f"Error saving psyche for {self.name}: {e}")
    
    def update_plan(self, goal: str, plan: List[str]):
        """Update plan and goal, setting first tactic as active if not already set"""
        self.goal = goal
        self.plan = plan
        
        # Set first tactic as active if not set and we have tactics
        if not self.active_tactic and plan and len(plan) > 0:
            self.active_tactic = plan[0]
            self.rounds_since_tactic_change = 0  # Reset counter for new plan
        
        return self
    
    def increment_tactic_counter(self):
        """Increment the rounds since last tactic change"""
        self.rounds_since_tactic_change += 1
        return self
    
    def update_active_tactic(self, new_tactic: str):
        """Update active tactic and reset the counter"""
        if self.active_tactic != new_tactic:
            self.active_tactic = new_tactic
            self.rounds_since_tactic_change = 0  # Reset counter when tactic changes
        return self
    
    def update_conversation_memory(self, summary: str):
        """Update conversation memory with a new summary"""
        self.conversation_memory = summary
        return self
    
    def update_interior_summary(self, summary: str):
        """Update the interior summary (personal narrative)"""
        if not hasattr(self, "interior") or not isinstance(self.interior, dict):
            self.interior = {"summary": "", "principles": ""}
        self.interior["summary"] = summary
        return self
    
    def update_interior_principles(self, principles: str):
        """Update the interior principles"""
        if not hasattr(self, "interior") or not isinstance(self.interior, dict):
            self.interior = {"summary": "", "principles": ""}
        self.interior["principles"] = principles
        return self
    
    def get_interior_summary(self) -> str:
        """Get the current interior summary"""
        if hasattr(self, "interior") and isinstance(self.interior, dict):
            return self.interior.get("summary", "")
        return ""
    
    def get_interior_principles(self) -> str:
        """Get the current interior principles"""
        if hasattr(self, "interior") and isinstance(self.interior, dict):
            return self.interior.get("principles", "")
        return ""
    
    def update_interior(self, summary: str = None, principles: str = None):
        """Update interior state with summary and/or principles"""
        if not hasattr(self, "interior") or not isinstance(self.interior, dict):
            self.interior = {"summary": "", "principles": ""}
        
        if summary is not None:
            self.interior["summary"] = summary
        if principles is not None:
            self.interior["principles"] = principles
        
        return self
    
    def update_emotion(self, emotion: str):
        """Update recent emotions, ensuring we don't repeat the same 3 too often"""
        # Ensure recent_emotions exists
        if not hasattr(self, "recent_emotions"):
            self.recent_emotions = []
        
        # Add new emotion to the front
        self.recent_emotions.insert(0, emotion)
        
        # Keep only the last 5 emotions for tracking
        if len(self.recent_emotions) > 5:
            self.recent_emotions = self.recent_emotions[:5]
        
        return self
    
    def get_available_emotions(self) -> List[str]:
        """Get list of emotions that haven't been used in the last 3 interactions"""
        all_emotions = ["angry", "confused", "happy", "intense", "nervous", "neutral", "playful", "scared", "smug"]
        
        # Ensure recent_emotions exists
        if not hasattr(self, "recent_emotions"):
            self.recent_emotions = []
        
        # Get emotions used in last 3 interactions
        recent_3 = self.recent_emotions[:3] if len(self.recent_emotions) >= 3 else []
        
        # If we have used 3 emotions recently, exclude them, otherwise return all
        if len(recent_3) == 3:
            available = [e for e in all_emotions if e not in recent_3]
            # If all emotions are excluded (shouldn't happen), return all emotions
            return available if available else all_emotions
        else:
            return all_emotions
    
    def clear_memories(self):
        """Clear all memories from this psyche"""
        self.memories = []
        self.conversation_memory = ""
        return self
    
    @classmethod
    def clear_all_memories(cls, agent_name: str):
        """Load psyche, clear memories, and save it back"""
        psyche = cls.load(agent_name)
        psyche.memories = []
        psyche.conversation_memory = ""
        psyche.save()
        return psyche
    
    def update_tension_interpretation(self, interpretation: str):
        """Update the tension interpretation"""
        self.tension_interpretation = interpretation
        return self 