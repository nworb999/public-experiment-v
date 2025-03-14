from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

class Psyche(BaseModel):
    """Maintains agent's mental state and history"""
    memories: List[str] = []
    relationships: Dict[str, Dict] = {}  # Entity -> relationship metadata
    current_goal: Optional[str] = None
    pending_actions: List[str] = []
    tension_level: int = 0  # 0-100 stress meter
    personality: str = "neutral"  # Default personality
    name: str = "Agent"  # Agent name
    
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
                return cls(**data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading psyche for {agent_name}: {e}")
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
            print(f"Error saving psyche for {self.name}: {e}") 