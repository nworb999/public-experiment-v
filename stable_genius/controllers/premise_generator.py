import random
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

class PremiseGenerator:
    """Generates dynamic workplace reality TV premises with flawed characters"""
    
    # Hidden character flaws (subconscious)
    HIDDEN_FLAWS = [
        "Arrogant", "Backstabbing", "Blatant Liar", "Bossy", "Chronic Backstager",
        "Conflict Ball", "Cowardly", "Crybaby", "Drama Queen", "Flaky", "Greedy",
        "Hot-Blooded", "Lazy", "Manipulative", "Narcissist", "Needy",
        "Poor Communication Kills", "Sore Loser", "Stubborn", "Vain"
    ]
    
    # Hero tropes (how agents see themselves)
    HERO_TROPES = {
        "Anti-Hero": "morally questionable but ultimately good intentions",
        "The Hero": "classic protagonist who fights for what's right",
        "The Chosen One": "destined to succeed through fate and natural talent",
        "Mentor": "wise advisor who guides others to success",
        "Sidekick": "reliable support who helps others achieve greatness",
        "Heart of Gold": "acts tough but is actually kind and caring inside",
        "Polite Hero": "respectful and courteous even under pressure",
        "Reluctant Hero": "doesn't seek glory but steps up when needed",
        "Hunter of Truth": "fights against deception and seeks justice",
        "Protector": "shields others from harm and stands up for the weak",
        "Underdog": "proves that determination can overcome any obstacle",
        "Team Player": "puts group success above personal gain",
        "Idealist": "believes in doing the right thing no matter the cost"
    }
    
    # Villain tropes (how agents see others)
    VILLAIN_TROPES = {
        "Anti-Villain": "has some good qualities but plays dirty when it matters",
        "Likable Villain": "charming and charismatic but ultimately selfish",
        "The Dragon": "enforcer who does the dirty work for their own agenda",
        "The Bully": "torments and intimidates weaker people",
        "Big Bad": "master manipulator who orchestrates schemes",
        "Arch-Enemy": "personal rival who seems to oppose everything you stand for",
        "Drama Queen": "overreacts to everything and creates unnecessary chaos",
        "Manipulative": "schemes behind the scenes and uses people",
        "Sore Loser": "throws tantrums and lashes out when things don't go their way",
        "Hired Gun": "mercenary who will betray anyone for personal gain",
        "The Jerk": "just an unlikeable, rude person who brings negativity",
        "Narcissist": "self-obsessed and dismissive of others' feelings",
        "Rule Breaker": "cheats and exploits loopholes to get ahead",
        "Backstabber": "pretends to be friendly but betrays trust",
        "Glory Hound": "steals credit and puts themselves above the team"
    }
    
    # Workplace reality TV premises
    WORKPLACE_PREMISES = [
        {
            "title": "Corporate Takeover Challenge",
            "scenario": "Two teams compete to acquire the most valuable fictional companies within 48 hours, negotiating deals and managing budgets.",
            "stakes": "The losing team faces elimination, and the winner gets to choose the next challenge.",
            "tension_points": ["budget constraints", "time pressure", "negotiation conflicts", "strategic betrayals"]
        },
        {
            "title": "Product Launch Showdown", 
            "scenario": "Teams must develop and pitch a revolutionary product to a panel of investors, handling everything from R&D to marketing.",
            "stakes": "Bottom performer gets fired, winning team gets a luxury retreat.",
            "tension_points": ["creative differences", "leadership disputes", "presentation anxiety", "resource competition"]
        },
        {
            "title": "Crisis Management Simulation",
            "scenario": "A major PR crisis hits the company and teams must navigate media, stakeholders, and damage control within 24 hours.",
            "stakes": "Poor performance results in public humiliation and elimination.",
            "tension_points": ["media pressure", "conflicting priorities", "blame games", "reputation management"]
        },
        {
            "title": "Sales Territory War",
            "scenario": "Competing teams fight for the same high-value clients in overlapping sales territories, using any means necessary.",
            "stakes": "Lowest sales numbers face elimination review.",
            "tension_points": ["client poaching", "territory disputes", "commission conflicts", "ethical boundaries"]
        },
        {
            "title": "Executive Retreat Elimination",
            "scenario": "During a weekend executive retreat, participants face leadership challenges while forming and breaking alliances.",
            "stakes": "Multiple eliminations based on peer review and performance.",
            "tension_points": ["alliance building", "leadership tests", "peer evaluations", "social dynamics"]
        },
        {
            "title": "Hostile Merger Simulation",
            "scenario": "Two companies are forced to merge, and teams must navigate the politics, layoffs, and cultural integration.",
            "stakes": "Redundant positions will be eliminated, winner becomes new department head.",
            "tension_points": ["job security fears", "cultural clashes", "power struggles", "loyalty tests"]
        },
        {
            "title": "Startup Incubator Competition",
            "scenario": "Teams pitch startup ideas to venture capitalists, competing for limited funding and mentorship opportunities.",
            "stakes": "Unfunded teams are eliminated, winner gets real investment money.",
            "tension_points": ["idea theft", "funding competition", "mentor favoritism", "intellectual property disputes"]
        },
        {
            "title": "Corporate Restructuring Challenge",
            "scenario": "Teams must redesign company operations while managing existing employees and implementing new systems.",
            "stakes": "Ineffective restructuring leads to team elimination.",
            "tension_points": ["employee resistance", "system failures", "budget overruns", "implementation delays"]
        }
    ]
    
    @classmethod
    def generate_premise(cls, num_agents: int = 2, turns: int = 5) -> Dict[str, Any]:
        """Generate a complete workplace reality TV premise with characters"""
        if num_agents != 2:
            raise ValueError("Only supports exactly 2 agents: Alice and Morgan")
        
        # Select random premise
        premise = random.choice(cls.WORKPLACE_PREMISES)
        
        # Generate characters
        agents = []
        
        for i in range(num_agents):
            agent = cls._generate_character()
            
            # Assign fixed names
            if i == 0:
                agent["name"] = "Alice"
            elif i == 1:
                agent["name"] = "Morgan"
            
            agents.append(agent)
        
        # Assign tropes and perspectives
        cls._assign_tropes_and_perspectives(agents, premise)
        
        return {
            "premise": premise,
            "agents": agents,
            "turns": turns,
            "generated": True
        }
    
    @classmethod
    def _generate_character(cls) -> Dict[str, Any]:
        """Generate a single character with personality and hidden flaws"""
        # Choose 2 hidden flaws first
        hidden_flaws = random.sample(cls.HIDDEN_FLAWS, 2)
        
        # Choose a hero trope
        hero_trope = random.choice(list(cls.HERO_TROPES.keys()))
        hero_description = cls.HERO_TROPES[hero_trope]
        
        # Create a combined personality that subtly reflects both hero identity and flaws
        personality = cls._create_combined_personality(hero_trope, hidden_flaws)
        
        return {
            "name": None,  # Will be set by generate_premise
            "personality": personality,
            "hidden_flaws": hidden_flaws,
            "flaw_descriptions": cls._get_flaw_descriptions(hidden_flaws),
            "hero_trope": hero_trope,
            "hero_description": hero_description
        }
    
    @classmethod
    def _create_combined_personality(cls, hero_trope: str, hidden_flaws: List[str]) -> str:
        """Create a short, legible, dramatic, combative, well-meaning sentence fragment (max 6 words)."""
        hero_phrases = {
            "Anti-Hero": ["Chaotic but means well"],
            "The Hero": ["Fiery, never backs down"],
            "The Chosen One": ["Destined, bulldozes for good"],
            "Mentor": ["Dramatic sage, thrives on conflict"],
            "Sidekick": ["Explosively loyal, stirs drama"],
            "Heart of Gold": ["Tough, causes scenes for good"],
            "Polite Hero": ["Explosively polite, calls out"],
            "Reluctant Hero": ["Erupts for good when pushed"],
            "Hunter of Truth": ["Relentless, confronts for justice"],
            "Protector": ["Combative, shields with drama"],
            "Underdog": ["Fiery underdog, never backs down"],
            "Team Player": ["Drama for the team, explosive"],
            "Idealist": ["Firebrand, stirs trouble for good"],
        }
        flaw_phrases = {
            "Arrogant": ["Explosively self-assured, argues hard"],
            "Backstabbing": ["Turns fast, always strategic"],
            "Blatant Liar": ["Twists truth with flair"],
            "Bossy": ["Commands with drama, expects chaos"],
            "Chronic Backstager": ["Schemes, stirs chaos backstage"],
            "Conflict Ball": ["Lives for drama, confronts all"],
            "Cowardly": ["Panics big, makes spectacle"],
            "Crybaby": ["Weaponizes emotion, dramatic setbacks"],
            "Drama Queen": ["Thrives on chaos, battles all"],
            "Flaky": ["Unpredictable, disappears in drama"],
            "Greedy": ["Fights for theirs, starts drama"],
            "Hot-Blooded": ["Erupts fast, drama follows"],
            "Lazy": ["Fights to avoid work, drama"],
            "Manipulative": ["Pulls strings, stirs the pot"],
            "Narcissist": ["All about me, dramatic"],
            "Needy": ["Craves attention, starts drama"],
            "Poor Communication Kills": ["Explodes from misunderstandings"],
            "Sore Loser": ["Tantrums, fireworks, can't lose"],
            "Stubborn": ["Never backs down, dramatic"],
            "Vain": ["Fights for spotlight, obsessed image"],
        }
        hero = random.choice(hero_phrases.get(hero_trope, ["Volatile, dramatic hero"]))
        flaw1 = random.choice(flaw_phrases.get(hidden_flaws[0], ["Combative, dramatic"]))
        flaw2 = random.choice(flaw_phrases.get(hidden_flaws[1], ["Explosive, unpredictable"]))
        # Randomly choose a template
        templates = [
            f"{hero}. {flaw1}.",
            f"{hero}. {flaw2}.",
            f"{hero}, but {flaw1.lower()}.",
            f"{hero}, but also {flaw2.lower()}.",
            f"{hero}—{flaw1.lower()}."
        ]
        summary = random.choice(templates)
        # Limit to 6 words max, but keep as a legible phrase
        words = summary.split()
        if len(words) > 6:
            summary = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        return summary.strip()
    
    @classmethod
    def _assign_tropes_and_perspectives(cls, agents: List[Dict[str, Any]], premise: Dict[str, Any]) -> None:
        """Assign villain tropes and create character perspectives on each other (hero tropes already assigned)"""
        for i, agent in enumerate(agents):
            # Hero trope and description already set in _generate_character
            
            # Create premise interpretation incorporating their hero identity
            agent["premise_interpretation"] = cls._warp_premise_by_character(premise, agent)
            
            # Create perspectives on other agents
            agent["other_agent_perspectives"] = {}
            for j, other_agent in enumerate(agents):
                if i != j:
                    # This agent sees the other as a villain
                    villain_trope = random.choice(list(cls.VILLAIN_TROPES.keys()))
                    agent["other_agent_perspectives"][other_agent["name"]] = {
                        "villain_trope": villain_trope,
                        "villain_description": cls.VILLAIN_TROPES[villain_trope],
                        "perspective": cls._create_villain_perspective(other_agent, villain_trope, cls.VILLAIN_TROPES[villain_trope])
                    }
    
    @classmethod
    def _create_villain_perspective(cls, target_agent: Dict[str, Any], villain_trope: str, villain_description: str) -> str:
        """Create how one agent views another as a villain, always volatile, dramatic, and combative."""
        name = target_agent["name"]
        personality = target_agent["personality"]
        perspective_templates = [
            f"{name} acts like they're all {personality}, but honestly? They're the kind of person who would {villain_description.lower()} and then start a fight about it.",
            f"Every time I see {name}, I just know drama is about to go down. {personality} types like them always {villain_description.lower()} and make everything a battle.",
            f"{name}'s so-called '{personality}' vibe is just a cover. Underneath, they're itching for a showdown and will {villain_description.lower()} at the drop of a hat."
        ]
        return random.choice(perspective_templates)
    
    @classmethod
    def _get_flaw_descriptions(cls, flaws: List[str]) -> Dict[str, str]:
        """Get detailed descriptions of character flaws"""
        descriptions = {
            "Arrogant": "Overconfident and dismissive of others, leading to conflicts",
            "Backstabbing": "Will betray allies for personal gain (great for alliances and eliminations)",
            "Blatant Liar": "Constantly dishonest, creating mistrust",
            "Bossy": "Takes charge in an overbearing way, annoying teammates",
            "Chronic Backstager": "Always scheming behind the scenes",
            "Conflict Ball": "Picks fights for no good reason",
            "Cowardly": "Avoids challenges or confrontation, making them unreliable",
            "Crybaby": "Overly emotional and prone to breakdowns",
            "Drama Queen": "Exaggerates every little issue for attention",
            "Flaky": "Unreliable and inconsistent, frustrating teammates",
            "Greedy": "Puts personal gain above teamwork",
            "Hot-Blooded": "Quick to anger, leading to explosive confrontations",
            "Lazy": "Avoids work, making others pick up the slack",
            "Manipulative": "Uses people like pawns for their own ends",
            "Narcissist": "Self-obsessed and dismissive of others' feelings",
            "Needy": "Constantly seeks validation, draining others",
            "Poor Communication Kills": "Misunderstands or fails to explain things, causing drama",
            "Sore Loser": "Throws tantrums when they don't win",
            "Stubborn": "Refuses to compromise, even when wrong",
            "Vain": "Obsessed with looks/status, leading to shallow conflicts"
        }
        
        return {flaw: descriptions[flaw] for flaw in flaws}
    
    @classmethod
    def _warp_premise_by_character(cls, premise: Dict[str, Any], character: Dict[str, Any]) -> str:
        """Warp the premise through the character's personality, flaws, and hero identity, always volatile, dramatic, and combative but well-meaning."""
        personality = character["personality"]
        hidden_flaws = character["hidden_flaws"]
        hero_description = character.get("hero_description", "someone who tries to do the right thing")
        warping_templates = [
            f"As a {personality} person, this {premise['title'].lower()} is my battleground. I'm here to prove I'm {hero_description}, and if I have to cause chaos or pick a fight, so be it—it's for the greater good. I know I tend to {cls._flaw_to_behavior(hidden_flaws[0]).lower()}, but that's just how you win.",
            f"This {premise['title'].lower()} is my chance to show everyone that being {hero_description} means never backing down, even if it gets messy. Sure, I sometimes {cls._flaw_to_behavior(hidden_flaws[1]).lower()}, but that's what it takes to come out on top (for the right reasons).",
            f"Given my {personality} nature, this {premise['title'].lower()} is going to be explosive. I'm not here to play nice—I'm here to fight for what's right, even if it means I {cls._flaw_to_behavior(hidden_flaws[0]).lower()} along the way."
        ]
        return random.choice(warping_templates)
    
    @classmethod
    def _flaw_to_behavior(cls, flaw: str) -> str:
        """Convert a flaw into a behavioral tendency description"""
        behaviors = {
            "Arrogant": "dismiss others' ideas too quickly",
            "Backstabbing": "look out for myself first",
            "Blatant Liar": "stretch the truth when it benefits me",
            "Bossy": "take control even when it's not my place",
            "Chronic Backstager": "work behind the scenes to influence outcomes",
            "Conflict Ball": "find myself in unnecessary arguments",
            "Cowardly": "avoid difficult confrontations",
            "Crybaby": "get overwhelmed by emotional situations",
            "Drama Queen": "make things more dramatic than they need to be",
            "Flaky": "struggle with consistency in my commitments",
            "Greedy": "prioritize my own gains",
            "Hot-Blooded": "react too quickly when frustrated",
            "Lazy": "look for the easiest path forward",
            "Manipulative": "find ways to influence people for my advantage",
            "Narcissist": "focus on how things affect me personally",
            "Needy": "require constant reassurance from others",
            "Poor Communication Kills": "misunderstand what others are really saying",
            "Sore Loser": "take losses harder than I should",
            "Stubborn": "stick to my position even when I might be wrong",
            "Vain": "worry about how I look to others"
        }
        
        return behaviors.get(flaw, "act in ways that create complications")
    
    @classmethod
    def load_or_generate_config(cls, num_agents: int = 2, turns: int = 5, force_regenerate: bool = False) -> Dict[str, Any]:
        """Always generate a new config, never load from file or save to disk."""
        return cls.generate_premise(num_agents, turns)

# Simple test function
if __name__ == "__main__":
    generator = PremiseGenerator()
    config = generator.generate_premise(3, 7)
    
    print("Generated Premise:")
    print(f"Title: {config['premise']['title']}")
    print(f"Scenario: {config['premise']['scenario']}")
    print(f"Stakes: {config['premise']['stakes']}")
    print()
    
    print("Generated Characters:")
    for agent in config['agents']:
        print(f"Name: {agent['name']}")
        print(f"Personality: {agent['personality']}")
        print(f"Hidden Flaws: {agent['hidden_flaws']}")
        print(f"Premise Interpretation: {agent['premise_interpretation']}")
        print() 