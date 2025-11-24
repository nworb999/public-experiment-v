#!/usr/bin/env python3
"""
Batch conversation generator for creating multiple agent conversations in parallel.
Each conversation uses a completely fresh premise and agent states.
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from stable_genius.agents.personalities import create_agent
from stable_genius.controllers.premise_generator import PremiseGenerator
from stable_genius.utils.llm import OllamaLLM
from stable_genius.utils.logger import logger
from stable_genius.models.psyche import Psyche


class ConversationCapture:
    """Captures conversation data for output formatting"""

    def __init__(self, conversation_id: int, premise: Dict[str, Any], agents_config: List[Dict[str, Any]]):
        self.conversation_id = conversation_id
        self.premise = premise
        self.agents_config = agents_config
        self.messages = []
        self.agent_states = {}

        # Create display name mapping (remove conversation ID suffix for cleaner output)
        self.display_names = {}
        for agent in agents_config:
            # Map "Alice_C001" -> "Alice", "Morgan_C001" -> "Morgan"
            if "_C" in agent["name"]:
                display_name = agent["name"].split("_C")[0]
            else:
                display_name = agent["name"]
            self.display_names[agent["name"]] = display_name

    def add_message(self, agent_name: str, message: str, tension_level: int):
        """Add a message to the conversation log"""
        display_name = self.display_names.get(agent_name, agent_name)
        self.messages.append({
            'agent': display_name,
            'message': message,
            'tension': tension_level,
            'timestamp': datetime.now().isoformat()
        })

    def set_final_agent_states(self, agent1_psyche: Psyche, agent2_psyche: Psyche):
        """Store final agent states for summary"""
        display_name1 = self.display_names.get(agent1_psyche.name, agent1_psyche.name)
        display_name2 = self.display_names.get(agent2_psyche.name, agent2_psyche.name)

        self.agent_states = {
            display_name1: {
                'tension': agent1_psyche.tension_level,
                'memories': agent1_psyche.memories,
                'conversation_memory': agent1_psyche.conversation_memory
            },
            display_name2: {
                'tension': agent2_psyche.tension_level,
                'memories': agent2_psyche.memories,
                'conversation_memory': agent2_psyche.conversation_memory
            }
        }


def write_conversation_file(capture: ConversationCapture, output_file: Path):
    """Write conversation to file (can be called incrementally during conversation)"""
    markdown_content = format_conversation_markdown(capture)
    output_file.write_text(markdown_content, encoding='utf-8')


def format_conversation_markdown(capture: ConversationCapture) -> str:
    """Format a conversation capture as markdown for review"""

    md_lines = []

    # Header
    md_lines.append(f"# Conversation {capture.conversation_id:03d}: {capture.premise['title']}")
    md_lines.append("")
    md_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md_lines.append("")

    # Premise details
    md_lines.append("## Premise")
    md_lines.append("")
    md_lines.append(f"**Scenario**: {capture.premise['scenario']}")
    md_lines.append("")
    md_lines.append(f"**Stakes**: {capture.premise['stakes']}")
    md_lines.append("")
    md_lines.append(f"**Tension Points**: {', '.join(capture.premise['tension_points'])}")
    md_lines.append("")

    # Agent details
    md_lines.append("## Characters")
    md_lines.append("")

    for agent_config in capture.agents_config:
        # Use display name (without conversation ID)
        display_name = capture.display_names.get(agent_config['name'], agent_config['name'])
        md_lines.append(f"### {display_name}")
        md_lines.append("")
        md_lines.append(f"**Personality**: {agent_config['personality']}")
        md_lines.append("")
        md_lines.append(f"**Hero Identity**: {agent_config['hero_trope']} - *{agent_config['hero_description']}*")
        md_lines.append("")
        md_lines.append(f"**Hidden Flaws**: {', '.join(agent_config['hidden_flaws'])}")
        md_lines.append("")

        # Show how they view themselves
        md_lines.append(f"**Self-Perception**: {agent_config['premise_interpretation']}")
        md_lines.append("")

        # Show how they view other agents
        if agent_config.get('other_agent_perspectives'):
            md_lines.append("**Views on Others**:")
            md_lines.append("")
            for other_name, perspective in agent_config['other_agent_perspectives'].items():
                # Also convert other names to display names
                other_display = capture.display_names.get(other_name, other_name)
                md_lines.append(f"- *{other_display}*: {perspective['villain_trope']} - {perspective['perspective']}")
            md_lines.append("")

    # Conversation transcript
    md_lines.append("## Conversation Transcript")
    md_lines.append("")

    for msg in capture.messages:
        md_lines.append(f"**{msg['agent']}** (Tension: {msg['tension']}/100)")
        md_lines.append(f"> {msg['message']}")
        md_lines.append("")

    # Final states
    md_lines.append("## Final Agent States")
    md_lines.append("")

    for agent_name, state in capture.agent_states.items():
        md_lines.append(f"### {agent_name}")
        md_lines.append("")
        md_lines.append(f"**Final Tension**: {state['tension']}/100")
        md_lines.append("")
        md_lines.append(f"**Reflection**: {state['conversation_memory']}")
        md_lines.append("")

    return "\n".join(md_lines)


async def run_single_conversation(
    conversation_id: int,
    turns: int,
    llm_service: OllamaLLM,
    output_file: Path = None
) -> ConversationCapture:
    """Run a single conversation with fresh premise and agents"""

    # Generate fresh premise and agents
    config = PremiseGenerator.generate_premise(num_agents=2, turns=turns)

    premise = config['premise']
    agents_config = config['agents']

    # Make agent names unique per conversation to avoid file conflicts when running in parallel
    agents_config[0]["name"] = f"Alice_C{conversation_id:03d}"
    agents_config[1]["name"] = f"Morgan_C{conversation_id:03d}"

    # Create conversation capture (with display names for output)
    capture = ConversationCapture(conversation_id, premise, agents_config)

    logger.info(f"[Conv {conversation_id:03d}] Starting: {premise['title']}")

    # Clear and set up agent psyche states
    logger.info(f"[Conv {conversation_id:03d}] Setting up agent psyches...")
    for agent_config in agents_config:
        agent_name = agent_config["name"]

        psyche = Psyche.load(agent_name)
        psyche.memories = []
        psyche.conversation_memory = ""
        psyche.plan = None
        psyche.active_tactic = None
        psyche.goal = None
        psyche.tension_level = 0  # Reset tension to 0 for fresh start

        # Update with new premise data
        if "personality" in agent_config:
            psyche.personality = agent_config["personality"]

        if "premise_interpretation" in agent_config:
            psyche.premise_interpretation = agent_config["premise_interpretation"]

        if "hidden_flaws" in agent_config:
            psyche.hidden_flaws = agent_config["hidden_flaws"]

        if "flaw_descriptions" in agent_config:
            psyche.flaw_descriptions = agent_config["flaw_descriptions"]

        if "hero_trope" in agent_config:
            psyche.hero_trope = agent_config["hero_trope"]

        if "hero_description" in agent_config:
            psyche.hero_description = agent_config["hero_description"]

        if "other_agent_perspectives" in agent_config:
            psyche.other_agent_perspectives = agent_config["other_agent_perspectives"]

        psyche.save()

    # Create agents
    logger.info(f"[Conv {conversation_id:03d}] Creating agent objects...")
    agent1 = create_agent(agents_config[0]["name"], agents_config[0]["personality"], llm_service)
    agent2 = create_agent(agents_config[1]["name"], agents_config[1]["personality"], llm_service)
    logger.info(f"[Conv {conversation_id:03d}] Agents created: {agent1.name} and {agent2.name}")

    # Write initial file with premise and character info (before conversation starts)
    if output_file:
        write_conversation_file(capture, output_file)
        logger.info(f"[Conv {conversation_id:03d}] Initial file written: {output_file.name}")

    # Run conversation
    message = "Hello there!"
    logger.info(f"[Conv {conversation_id:03d}] Starting {turns}-turn conversation...")

    for i in range(turns):
        # Agent 1's turn
        response1 = await agent1.receive_message(message, agent2.name)
        message1 = response1['speech']
        agent1_psyche = agent1.get_psyche()

        capture.add_message(agent1.name, message1, agent1_psyche.tension_level)
        logger.info(f"[Conv {conversation_id:03d}] Turn {i+1}/{turns} - {agent1.name}: {message1[:50]}...")

        # Write file after agent 1's message
        if output_file:
            write_conversation_file(capture, output_file)

        # Agent 2's turn
        response2 = await agent2.receive_message(message1, agent1.name)
        message2 = response2['speech']
        agent2_psyche = agent2.get_psyche()

        capture.add_message(agent2.name, message2, agent2_psyche.tension_level)
        logger.info(f"[Conv {conversation_id:03d}] Turn {i+1}/{turns} - {agent2.name}: {message2[:50]}...")

        # Write file after agent 2's message (completing the turn)
        if output_file:
            write_conversation_file(capture, output_file)

        message = message2

    # Capture final states
    capture.set_final_agent_states(agent1.get_psyche(), agent2.get_psyche())

    # Write final file with agent states
    if output_file:
        write_conversation_file(capture, output_file)
        logger.info(f"[Conv {conversation_id:03d}] Final file written")

    logger.info(f"[Conv {conversation_id:03d}] Completed!")

    return capture


async def run_batch_generation(count: int, turns: int, output_dir: Path):
    """Run multiple conversations sequentially"""

    # Load environment variables
    load_dotenv()

    # Verify API key (check both possible names)
    api_key = os.getenv('ANTHROPIC_KEY') or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("ANTHROPIC_KEY environment variable not found in .env file")
        sys.exit(1)

    # Create LLM service
    llm_service = OllamaLLM(model="claude-sonnet-4-5-20250929", use_local=False)

    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_dir = output_dir / f"batch_{timestamp}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting batch generation of {count} conversations IN PARALLEL")
    logger.info(f"Output directory: {batch_dir}")
    logger.info(f"Each conversation uses unique agent names to avoid conflicts")
    logger.info(f"Files will be written incrementally as conversations progress")

    # Create output file paths upfront
    output_files = [
        batch_dir / f"conversation_{i + 1:03d}.md"
        for i in range(count)
    ]

    # Run all conversations in parallel using asyncio.gather
    tasks = [
        run_single_conversation(i + 1, turns, llm_service, output_files[i])
        for i in range(count)
    ]

    logger.info(f"Launching {count} parallel conversation tasks...")
    captures = await asyncio.gather(*tasks)
    logger.info(f"All {count} conversations completed!")

    # Write index file
    index_lines = [
        f"# Batch Generation - {timestamp}",
        "",
        f"Generated {count} conversations with {turns} turns each",
        "",
        "## Conversations",
        ""
    ]

    for capture in captures:
        filename = f"conversation_{capture.conversation_id:03d}.md"
        # Add to index
        index_lines.append(f"- [{capture.premise['title']}]({filename})")

    # Write index file
    index_path = batch_dir / "index.md"
    index_path.write_text("\n".join(index_lines), encoding='utf-8')

    logger.info(f"\n✅ Batch generation complete!")
    logger.info(f"📁 Output directory: {batch_dir}")
    logger.info(f"📄 Generated {count} conversation scripts")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate multiple agent conversations in parallel for script review"
    )
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of conversations to generate (default: 3)'
    )
    parser.add_argument(
        '--turns',
        type=int,
        default=5,
        help='Number of turns per conversation (default: 5)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='scripts-output',
        help='Output directory for generated scripts (default: scripts-output)'
    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    # Run batch generation
    asyncio.run(run_batch_generation(args.count, args.turns, output_dir))


if __name__ == "__main__":
    main()
