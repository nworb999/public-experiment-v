"""
Configuration management for the visualization server
"""
import json
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "generated_agents_config.json"
TEMPLATE_DIR = PROJECT_ROOT / "visualizer" / "templates"
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_PORT = 5000
MAX_HISTORY_ITEMS = 3
MAX_AGENT_MESSAGES = 10
VALID_AGENT_IDS = [0, 1]

def load_config():
    """Load configuration from generated JSON file"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}. Please run the main app to generate this file before starting the visualizer.")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading config file: {e}") 