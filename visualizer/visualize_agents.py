#!/usr/bin/env python3
"""
Visualization dashboard for agent conversations with real-time updates
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from visualizer.server import main

if __name__ == "__main__":
    sys.exit(main()) 