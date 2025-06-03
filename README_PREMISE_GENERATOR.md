# Premise Generator - Dynamic Workplace Reality TV Scenarios

The premise generator creates dynamic workplace reality TV scenarios with characters that have hidden psychological flaws and hero/villain perspectives, replacing the static `agents_config.json` approach.

## Features

### 🎭 **Character Generation**
- **Dynamic Personalities**: 20 different surface personality types (ambitious, analytical, charismatic, etc.)
- **Hidden Flaws**: Each character gets 2 subconscious flaws that influence their behavior without them being aware
- **Hero/Villain Tropes**: Each character sees themselves as a hero archetype and views others as villain types
- **Reality TV Names**: Diverse pool of names perfect for reality TV drama
- **Premise Interpretation**: Each character views the scenario through their own warped perspective

### 🦸 **Hero Tropes (Self-Identity)**
Each agent sees themselves as one of these hero archetypes:
- **Classic Heroes**: The Hero, Anti-Hero, The Chosen One
- **Support Heroes**: Mentor, Sidekick, Team Player, Protector
- **Flawed Heroes**: Reluctant Hero, Heart of Gold, Underdog
- **Principled Heroes**: Hunter of Truth, Polite Hero, Idealist

### 😈 **Villain Tropes (How They View Others)**
Each agent views other characters as villain types:
- **Sympathetic Villains**: Anti-Villain, Likable Villain
- **Classic Antagonists**: Big Bad, Arch-Enemy, The Bully
- **Scheming Types**: Manipulative, The Dragon, Chronic Backstager
- **Personality Villains**: Drama Queen, Narcissist, The Jerk
- **Unreliable Types**: Sore Loser, Backstabber, Hired Gun

### 🏢 **Workplace Scenarios** 
- **Corporate Takeover Challenge**: Acquire companies under pressure
- **Product Launch Showdown**: Develop and pitch revolutionary products
- **Crisis Management Simulation**: Handle PR disasters in real-time
- **Sales Territory War**: Fight for high-value clients
- **Executive Retreat Elimination**: Leadership challenges with alliance building
- **Hostile Merger Simulation**: Navigate company mergers and layoffs
- **Startup Incubator Competition**: Pitch for venture capital funding
- **Corporate Restructuring Challenge**: Redesign operations under pressure

### 😈 **Hidden Character Flaws**
Characters have 2 hidden flaws that subconsciously influence their behavior:

**Power & Control Flaws**:
- Arrogant, Bossy, Narcissist, Manipulative

**Loyalty & Trust Flaws**:
- Backstabbing, Blatant Liar, Chronic Backstager

**Emotional Flaws**:
- Hot-Blooded, Crybaby, Drama Queen, Needy

**Reliability Flaws**:
- Flaky, Lazy, Cowardly, Poor Communication Kills

**Competitive Flaws**:
- Sore Loser, Stubborn, Greedy, Vain, Conflict Ball

## Quick Start

### Generate a New Premise
```bash
python generate_premise.py [num_agents] [turns]
```

**Examples**:
```bash
# 2 agents, 5 turns (default)
python generate_premise.py

# 3 agents, 8 turns
python generate_premise.py 3 8

# 4 agents, 10 turns  
python generate_premise.py 4 10
```

### Use in Code
```python
from stable_genius.controllers.premise_generator import PremiseGenerator

# Generate new premise
config = PremiseGenerator.generate_premise(num_agents=3, turns=7)

# Load existing or generate new
config = PremiseGenerator.load_or_generate_config(
    num_agents=2, 
    turns=5, 
    force_regenerate=True
)

# Save config
PremiseGenerator.save_config(config)
```

## How It Works

### 1. **Dynamic Generation**
The conversation system now automatically generates premises instead of loading static configs:

```python
# In conversation.py
def load_config():
    # Falls back to dynamic generation if no static config exists
    config = PremiseGenerator.load_or_generate_config(num_agents=2, turns=5)
    return config
```

### 2. **Character Psychology**
Each character's psyche stores:
- `premise_interpretation`: Their personal view of the scenario
- `hidden_flaws`: Subconscious behavioral tendencies  
- `flaw_descriptions`: Detailed flaw explanations
- `hero_trope`: How they see themselves (hero archetype)
- `other_agent_perspectives`: How they view others as villains

### 3. **Subconscious Influence**
The prompt system subtly incorporates all elements without explicit references:

**Hidden Flaws**: "Backstabbing" → **Tendency**: "awareness of strategic opportunities"  
**Hero Identity**: "Protector" → **Core belief**: "shields others from harm and stands up for the weak"  
**Villain View**: "The Dragon" → **Perspective**: "enforcer who does the dirty work for their own agenda"

## Character Dynamics Example

```
🎭 CHARACTER DYNAMICS:
Grace (Heart of Gold Hero) sees Ryan as: The Dragon
Ryan (Protector Hero) sees Grace as: Backstabber
🔥 Conflict: Heart of Gold vs The Dragon / Protector vs Backstabber
```

This creates rich psychological conflict where:
- **Grace** thinks she's the caring one but sees Ryan as a scheming enforcer
- **Ryan** thinks he's protecting people but sees Grace as a traitor
- **Neither realizes their own hidden flaws** (Grace: Greedy + Hot-Blooded, Ryan: Backstager + Poor Communication)

## Configuration Structure

```json
{
  "premise": {
    "title": "Crisis Management Simulation",
    "scenario": "A major PR crisis hits...",
    "stakes": "Poor performance results in elimination...",
    "tension_points": ["media pressure", "blame games", ...]
  },
  "agents": [
    {
      "name": "Grace",
      "personality": "diplomatic", 
      "hidden_flaws": ["Greedy", "Hot-Blooded"],
      "hero_trope": "Heart of Gold",
      "hero_description": "acts tough but is actually kind and caring inside",
      "other_agent_perspectives": {
        "Ryan": {
          "villain_trope": "The Dragon",
          "villain_description": "enforcer who does the dirty work",
          "perspective": "Ryan's innovative personality doesn't fool me..."
        }
      },
      "premise_interpretation": "This crisis is my chance to prove I'm..."
    }
  ],
  "turns": 5,
  "generated": true
}
```

## Backwards Compatibility

The system maintains backwards compatibility with static `agents_config.json` files. If a static config exists, it will be used. To force dynamic generation, delete the static config file or use `force_regenerate=True`.

## Character Development

The trope system creates multi-layered characters with rich internal conflicts:

### Example: Grace vs Ryan
- **Grace's Reality**: "I'm a Heart of Gold hero trying to help, but Ryan is a scheming Dragon"
- **Ryan's Reality**: "I'm a Protector hero defending people, but Grace is a Backstabber"
- **Hidden Truth**: Grace is actually greedy and hot-blooded, Ryan actually schemes behind scenes and miscommunicates

### Result: Authentic Drama
- Grace gets angry (hot-blooded) when Ryan questions her motives (greed)
- Ryan misunderstands (poor communication) and plots behind scenes (backstager)
- Each thinks they're the hero and the other is the villain
- **Perfect reality TV conflict!** 🔥

## Example Output

```
============================================================
PREMISE: Crisis Management Simulation
============================================================
Scenario: Major PR crisis hits, teams navigate media and damage control...
Stakes: Poor performance results in public humiliation and elimination.

CHARACTERS & DYNAMICS:
----------------------------------------
1. Grace (diplomatic)
   Hero Identity: Heart of Gold - acts tough but caring inside
   Hidden Flaws: Greedy, Hot-Blooded
   Views on Others:
     → Ryan as 'The Dragon': Enforcer who does dirty work for their agenda

2. Ryan (innovative)  
   Hero Identity: Protector - shields others from harm
   Hidden Flaws: Chronic Backstager, Poor Communication Kills
   Views on Others:
     → Grace as 'Backstabber': Pretends to be friendly but betrays trust

🔥 Conflict potential: Heart of Gold vs The Dragon / Protector vs Backstabber
```

This creates psychologically complex characters with authentic motivations, misunderstandings, and conflicts - perfect for reality TV drama! 🎬📺 