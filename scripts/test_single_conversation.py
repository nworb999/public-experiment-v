#!/usr/bin/env python3
"""Test a single conversation to debug hanging issues"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from stable_genius.agents.personalities import create_agent
from stable_genius.controllers.premise_generator import PremiseGenerator
from stable_genius.utils.llm import OllamaLLM
from stable_genius.utils.logger import logger
from stable_genius.models.psyche import Psyche

async def test_conversation():
    load_dotenv()

    logger.info("Step 1: Creating LLM service...")
    llm_service = OllamaLLM(model="claude-sonnet-4-5-20250929", use_local=False)

    logger.info("Step 2: Generating premise...")
    config = PremiseGenerator.generate_premise(num_agents=2, turns=2)
    premise = config['premise']
    agents_config = config['agents']
    logger.info(f"Premise: {premise['title']}")

    logger.info("Step 3: Setting up agent psyches...")
    for agent_config in agents_config:
        agent_name = agent_config["name"]
        logger.info(f"  Setting up {agent_name}")

        psyche = Psyche.load(agent_name)
        psyche.memories = []
        psyche.conversation_memory = ""
        psyche.plan = None
        psyche.active_tactic = None
        psyche.goal = None
        psyche.personality = agent_config["personality"]
        psyche.premise_interpretation = agent_config.get("premise_interpretation")
        psyche.hidden_flaws = agent_config.get("hidden_flaws", [])
        psyche.flaw_descriptions = agent_config.get("flaw_descriptions", {})
        psyche.hero_trope = agent_config.get("hero_trope")
        psyche.hero_description = agent_config.get("hero_description")
        psyche.other_agent_perspectives = agent_config.get("other_agent_perspectives", {})
        psyche.save()

    logger.info("Step 4: Creating agent objects...")
    agent1 = create_agent(agents_config[0]["name"], agents_config[0]["personality"], llm_service)
    agent2 = create_agent(agents_config[1]["name"], agents_config[1]["personality"], llm_service)
    logger.info(f"  Created {agent1.name} and {agent2.name}")

    logger.info("Step 5: Starting conversation (1 turn)...")
    message = "Hello there!"

    logger.info(f"  {agent1.name} receiving message...")
    response1 = await agent1.receive_message(message, agent2.name)
    message1 = response1['speech']
    logger.info(f"  {agent1.name}: {message1[:100]}...")

    logger.info(f"  {agent2.name} receiving message...")
    response2 = await agent2.receive_message(message1, agent1.name)
    message2 = response2['speech']
    logger.info(f"  {agent2.name}: {message2[:100]}...")

    logger.info("✅ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_conversation())
