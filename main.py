# context management
# prompt formatter
# decision pipeline
# tensionmeter
# .say() .do() .go()
# plan act reflect
# available actions
# relationships
# complexes/personal narrative
# goals/motivations->tactics

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

app = FastAPI()

# === Context Management ===
class Context(BaseModel):
    """Maintains agent's current state and history"""
    memories: List[str] = []
    relationships: Dict[str, Dict] = {}  # Entity -> relationship metadata
    current_goal: Optional[str] = None
    pending_actions: List[str] = []
    tension_level: int = 0  # 0-100 stress meter

# === Prompt Formatter ===
class PromptFormatter:
    @staticmethod
    def plan_prompt(context: Context) -> str:
        """Format context into planning prompt"""
        return f"""
        Current state: {context.tension_level}/100 tension
        Recent history: {context.memories[-3:]}
        Relationships: {list(context.relationships.keys())}
        Goals: {context.current_goal or 'None'}
        
        What should I do next? Respond in JSON format with 'goal' and 'tactic' keys.
        """
    
    @staticmethod
    def act_prompt(context: Context, observation: str) -> str:
        """Format context into action prompt"""
        return f"""
        {observation}
        Current goal: {context.current_goal}
        Available actions: {context.pending_actions}
        
        How should I respond? Respond in JSON format with 'action' and 'speech' keys.
        """

# === Decision Pipeline ===
class DecisionPipeline:
    def __init__(self):
        self.llm = DummyLLM()  # Replace with actual LLM integration
    
    async def react_cycle(self, observation: str, context: Context) -> dict:
        """ReAct-style loop: Plan -> Act -> Reflect"""
        # Plan phase
        plan = json.loads(self.llm.generate(PromptFormatter.plan_prompt(context)))
        context.current_goal = plan['goal']
        
        # Act phase
        action_response = json.loads(self.llm.generate(
            PromptFormatter.act_prompt(context, observation)
        ))
        
        # Reflect phase
        self._update_tension(context, action_response.get('action'))
        context.memories.append(observation)
        
        return action_response
    
    def _update_tension(self, context: Context, action: str):
        """Update tension meter based on action"""
        if "confront" in action:
            context.tension_level = min(context.tension_level + 20, 100)
        elif "cooperate" in action:
            context.tension_level = max(context.tension_level - 10, 0)

# === API Endpoints ===
class AgentRequest(BaseModel):
    message: str
    current_context: Optional[Context] = None

@app.post("/message")
async def handle_message(request: AgentRequest):
    """Main endpoint for agent interaction"""
    context = request.current_context or Context()
    pipeline = DecisionPipeline()
    
    response = await pipeline.react_cycle(request.message, context)
    
    return {
        "response": response['speech'],
        "action": response['action'],
        "updated_context": context
    }

# === Mock LLM ===
class DummyLLM:
    """Replace with actual LLM calls"""
    def generate(self, prompt: str) -> str:
        if "What should I do next?" in prompt:
            return json.dumps({
                "goal": "reduce tension",
                "tactic": "diplomatic dialogue"
            })
        return json.dumps({
            "action": "say",
            "speech": "Let's discuss this calmly."
        })

# === Tension Meter Helpers ===
@app.post("/action")
async def log_action(action: str):
    """Track actions affecting tension"""
    # Implement tension update logic here
    return {"status": "logged"}

@app.post("/go")
async def advance_state():
    """Progress agent's internal state"""
    # Implement time-based updates here
    return {"status": "advanced"}



