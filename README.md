# Conflictors: Agent-Driven Narrative Generation


[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg

A cognitive architecture experiment for generating believable agent-driven drama using large language models (LLMs). This project explores computational narrative through autonomous agents engaged in simulated reality TV-style conversations.

## Abstract

Large language models (LLMs) have revolutionized digital content production, automating text generation at unprecedented scale and fundamentally restructuring media markets. This project applies language agents to narrative planning for synthetic entertainment. The output is a simulated conversation between two agents who are powered by LLMs. It builds upon foundational work in computational narratology, computer planning, and agent-based AI. 

It addresses key challenges in narrative AI: maintaining long-term narrative structure, demonstrating agency, and generating contextually appropriate story progressions that adhere to causal logic. It seeks to do so by generating an agent-based drama with natural, believable agents who have interiors and actions consistent with their principles and psyche.

The project focuses on reality TV as a test environment, where mundane, natural dialogue and evolving relationships take precedent over overarching narrative and coherent plot. The novelty of this research is synthesizing state-of-the-art language agent architectures with existing agent-driven storytelling techniques.

## Implementation Details

### Architecture Overview

The system implements a **cognitive architecture** where agents operate through five sequential processing stages during each conversational turn:

1. **Reactive Trigger**: Modulates affective valence based on matches against agent-specific stress word lists
2. **Intent Classifier**: Categorizes incoming utterances to understand opponent's goals
3. **Planning Module**: Selects conversational tactics, maintains strategy, or initiates termination upon goal satisfaction
4. **Action Generation**: Produces dialogue utterances based on current state and goals
5. **Reflection Module**: Consolidates dialogue history into individualized, potentially distorted agent perspectives

### Key Design Principles

- **TV Tropes as Moral Compass**: Each agent is initialized using TV Tropes archetypes (hero, villain, underdog, narcissist, etc.) as the foundation for their personality, perception of themselves, and perception of other agents
- **Conflicting Perceptions**: Agents view themselves as heroes and others as antagonists, creating organic tension
- **Hidden Flaws**: Agents have hidden personality flaws that influence behavior without their explicit awareness
- **Memory and Reflection**: Agents maintain warped personal narratives through abstracted memories that may differ from objective reality
- **Goal-Directed Behavior**: Each agent pursues individual objectives through planned conversational tactics

### Technical Components

- **LLM Backend**: Claude Sonnet 4 (Anthropic)
- **Text Classification**: FastText for trigger word detection
- **Turn-Based Framework**: Agents alternate speaking, similar to chess
- **Premise Generation**: System extrapolates mental states, tendencies, and workplace conflict scenarios from minimal trope inputs
- **Conversation Controller**: Manages turn-based flow and agent state synchronization
- **Psyche Processor**: Updates emotional state and cognitive variables each turn

### Conversation Flow
```
Initialization 
    ↓
Agent Generation from Tropes 
    ↓
Premise Generation
    ↓
┌─────────────────────────┐
│   Conversation Loop     │
│                         │
│  Agent A's Turn:        │
│   • Trigger Detection   │
│   • Intent Classification│
│   • Planning            │
│   • Action Generation   │
│   • Reflection          │
│                         │
│  Agent B's Turn         │
│   (same steps)          │
│                         │
│  (Loop repeats)         │
└─────────────────────────┘
```


## How to Run

### Prerequisites

- Python 3.8+
- Pipenv (for dependency management)
- Anthropic API key (for Claude access)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd public-experiment-v
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

3. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Running the Main Conversation

Run the main conversation simulation:
```bash
pipenv run python main.py
```

This will:
- Generate two agents with conflicting personalities based on TV Tropes
- Create a workplace premise for their interaction
- Run a turn-based conversation (default: 10 turns per agent)
- Save conversation history and agent states to `db/` directory

### Using the Visualizer

To view conversations with a web interface:

1. Start the visualization server:
```bash
pipenv run python visualizer/visualize.py
```

2. Open your browser to `http://localhost:5000`

The visualizer provides:
- Real-time conversation updates
- Agent emotional state visualization with avatar expressions
- Cognitive pipeline insights (trigger detection, intent classification, planning)
- Conversation history playback

### Premise Generator

To generate custom premises for agent conversations:
```bash
pipenv run python -m stable_genius.controllers.premise_generator
```

See `README_PREMISE_GENERATOR.md` for more details.

### Testing Components

Test the Ollama integration (if using local models):
```bash
pipenv run python scripts/test_ollama.py
```

## Project Structure
```
public-experiment-v/
├── stable_genius/          # Core agent framework
│   ├── agents/             # Agent definitions and personalities
│   ├── controllers/        # Conversation and premise management
│   ├── core/               # Cognitive pipeline components
│   ├── models/             # Agent psyche models
│   └── utils/              # LLM interface and utilities
├── visualizer/             # Web-based visualization
│   ├── server/             # Flask backend
│   └── templates/          # Frontend UI
├── db/                     # Agent state persistence
├── models/                 # Trained classification models (FastText)
├── config/                 # Agent configuration files
└── main.py                 # Main conversation runner
```


## Research Context

This project explores agent-driven narrative generation as an alternative to top-down plot planning. It examines whether conflicting agent-level role perceptions can generate organic narrative tension, similar to successful reality television formats.

### Related Work

The system draws on computational narrative research including:
- **TALE-SPIN** (Meehan): Goal-driven agents with conflicting objectives
- **Facade**: Beat-based interactive drama with emergent narrative
- **Generative Agents** (Park et al.): LLM-powered agents with observation, planning, and reflection
- **OPIATE** (Fairclough): Hybrid approach with story director and semi-autonomous characters
- **IDtension** (Szilas): Narrative physics tracking moral principles

### Key Findings

**Successes:**
- Goal pursuit and conflict generation emerged naturally from agent architecture
- Agents maintained character consistency throughout conversations
- TV Tropes provided effective semantic scaffolding for believable personalities

**Limitations:**
- Agents remained primarily reactive rather than proactive
- Plot drift and circular dialogue occurred frequently
- Overly simplistic memory architecture (single overwritten summary)
- Lack of natural dialogue patterns like interruptions
- Failed to achieve sophisticated obstruction and achievement dynamics

**Conclusion:**
The results support hybrid approaches for narrative planning with LLMs. Pure bottom-up, agent-driven approaches prove insufficient without complementary top-down narrative management. An ideal next iteration would implement a separate autonomous "plot orchestrator" to manage story arc progression while maintaining individual agent authenticity.

## Models and Data

- **Agent States**: Stored in `db/` as JSON (includes memories, goals, emotional state)
- **Tension Models**: FastText classifiers in `models/` for trigger word detection
- **Configuration**: Agent initialization parameters in `config/`

## License

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

This means you are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original
