import asyncio
import argparse
import sys
import signal
import json
from pathlib import Path
from stable_genius.agents.personalities import create_agent
from stable_genius.utils.logger import logger


def signal_handler(sig, frame):
    """Handle keyboard interrupt gracefully"""
    logger.info("\n\nKeyboard interrupt detected. Shutting down gracefully...\n\n")
    logger.info("Thank you for using the application! ₍ᐢ._.ᐢ₎♡")
    sys.exit(0)

# Config directory and file
config_dir = Path(__file__).parent / "config"
config_dir.mkdir(exist_ok=True)
CONFIG_FILE = config_dir / "agents_config.json"

# Load config from file
def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}. Please create this file before running.")
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {e}")

async def simulate_conversation():
    """Run a simulated conversation between two agents"""
    try:
        # Load config
        config = load_config()
        turns = config.get("turns", 5)
        
        # Get agent configs
        agents_config = config["agents"]
        if len(agents_config) < 2:
            logger.error("Need at least 2 agents in config file")
            return 1
        
        # Create agents
        agent1 = create_agent(agents_config[0]["name"], agents_config[0]["personality"])
        agent2 = create_agent(agents_config[1]["name"], agents_config[1]["personality"])
        
        logger.info(f"\n\n========== Starting Conversation between {agent1.name} and {agent2.name} ==========\n")
        logger.info(f"Conversation turns: {turns}\n")
        
        # Start with a greeting
        message = "Hello there!"
        
        for i in range(turns):
            logger.info(f"\n\n---------- Turn {i+1} ----------\n")
            try:
                response1 = await agent1.receive_message(message, agent2.name)
                message1 = response1['speech']
                # Get current psyche state
                agent1_psyche = agent1.get_psyche()
                logger.info(f"{agent1.name} ({agent1_psyche.tension_level}/100 tension):")
                logger.info(f"  \"{message1}\"\n")
                
                response2 = await agent2.receive_message(message1, agent1.name)
                message = response2['speech']
                # Get current psyche state
                agent2_psyche = agent2.get_psyche()
                logger.info(f"{agent2.name} ({agent2_psyche.tension_level}/100 tension):")
                logger.info(f"  \"{message}\"\n")
            except Exception as e:
                logger.error(f"Error during conversation turn {i+1}: {str(e)}")
                message = "I'm not sure I understood that. Can you try again?"
        
        logger.info("\n\n========== Conversation Ended ==========\n")
        agent1_psyche = agent1.get_psyche()
        agent2_psyche = agent2.get_psyche()
        logger.info(f"{agent1.name}'s final state: {agent1_psyche.tension_level}/100 tension")
        logger.info(f"{agent2.name}'s final state: {agent2_psyche.tension_level}/100 tension")
        logger.info(f"\n{agent1.name}'s memories:")
        for memory in agent1_psyche.memories:
            logger.info(f"  - {memory}")
        logger.info(f"\n{agent2.name}'s memories:")
        for memory in agent2_psyche.memories:
            logger.info(f"  - {memory}")
        logger.info("")
        
    except KeyboardInterrupt:
        logger.info("\n\nConversation interrupted by user. Exiting gracefully...")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    # Register signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Run the conversation
        exit_code = asyncio.run(simulate_conversation())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        # This is a fallback in case the signal handler doesn't catch it
        logger.info("\n\nKeyboard interrupt detected. Shutting down...")
        sys.exit(0) 