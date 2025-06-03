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
    pending_actions: List[str] = []
    tension_level: int = 0  # 0-100 stress meter
    personality: str = "neutral"  # Default personality
    name: str = "Agent"  # Agent name
    stressful_phrases: List[str] = []  # Personalized list of stressful phrases
    
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
                with open(filepath, 'r', encoding='utf-8') as f:
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
            with open(filepath, 'w', encoding='utf-8') as f:
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
        
        return self
    
    def update_conversation_memory(self, summary: str):
        """Update conversation memory with a new summary"""
        self.conversation_memory = summary
        return self
            
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