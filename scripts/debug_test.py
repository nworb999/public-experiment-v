#!/usr/bin/env python3
"""Minimal test to find where it hangs"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("1. Importing dotenv...")
from dotenv import load_dotenv

print("2. Loading .env...")
load_dotenv()

print("3. Importing os...")
import os

print("4. Checking ANTHROPIC_KEY...")
key = os.getenv('ANTHROPIC_KEY')
print(f"   Key exists: {bool(key)}")

print("5. Importing logger...")
from stable_genius.utils.logger import logger

print("6. Importing LLM...")
from stable_genius.utils.llm import OllamaLLM

print("7. Creating LLM service...")
llm = OllamaLLM(model="claude-sonnet-4-5-20250929", use_local=False)
print("   LLM created successfully!")

print("8. Importing PremiseGenerator...")
from stable_genius.controllers.premise_generator import PremiseGenerator

print("9. Generating premise...")
config = PremiseGenerator.generate_premise(num_agents=2, turns=2)
print(f"   Premise: {config['premise']['title']}")

print("\n✅ All tests passed!")
