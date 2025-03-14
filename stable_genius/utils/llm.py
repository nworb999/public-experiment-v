import json
import requests
import sys
from typing import Dict, Any, Optional, List

class OllamaLLM:
    """Interface to the Ollama API for LLM generation"""
    
    def __init__(self, personality="neutral", model="mistral"):
        self.base_url = "http://localhost:11434"
        self.model = model
        self.personality = personality
        # Verify connection on initialization - exit if Ollama is not available
        if not self._verify_connection():
            print("ERROR: Cannot continue without Ollama connection. Please start Ollama and try again.")
            sys.exit(1)
    
    def _verify_connection(self):
        """Verify Ollama is running and has the required model"""
        try:
            # Check available models
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [m['name'] for m in models]
                
                if not models:
                    print("Warning: No models found in Ollama. Please install a model with 'ollama pull mistral'")
                    return False
                elif self.model not in available_models:
                    print(f"Warning: Model '{self.model}' not found. Available models: {', '.join(available_models)}")
                    if available_models:
                        self.model = available_models[0]
                        print(f"Falling back to '{self.model}'")
                
                # Connection verified and model available
                return True
            else:
                print(f"Error: Could not check Ollama models. Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Ollama server. Is it running?")
            print("Try starting Ollama with 'ollama serve'")
            return False
        except Exception as e:
            print(f"Error: Could not connect to Ollama server: {str(e)}")
            return False
    
    def generate(self, prompt: str) -> str:
        """Generate text using Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30  # Add a timeout to prevent hanging
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                error_msg = f"Error connecting to Ollama service: {response.status_code} {response.reason}"
                print(error_msg)
                
                # Return a JSON formatted error that can be processed by the system
                if "JSON" in prompt.upper():
                    return json.dumps({
                        "error": f"Error: {response.status_code} {response.reason}"
                    })
                return f"Error: {response.status_code} {response.reason}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Ollama service: {str(e)}"
            print(error_msg)
            
            # Return a JSON formatted error that can be processed by the system
            if "JSON" in prompt.upper():
                return json.dumps({
                    "error": f"Error: {str(e)}"
                })
            return f"Error: {str(e)}"

