import json
import requests
import sys
import time
from stable_genius.utils.logger import logger

class OllamaLLM:
    """Interface to the Ollama API for LLM generation"""
    
    def __init__(self, personality="neutral", model="llama3.3:latest", max_retries=5, retry_delay=2):
        self.base_url = "http://localhost:11434"
        self.model = model
        self.personality = personality
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        # Verify connection on initialization - exit if Ollama is not available
        if not self._verify_connection():
            logger.info("ERROR: Cannot continue without Ollama connection. Please start Ollama and try again.")
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
                    logger.info("Warning: No models found in Ollama. Please install a model with 'ollama pull <model-name>'")
                    return False
                elif self.model not in available_models:
                    logger.info(f"Warning: Model '{self.model}' not found. Available models: {', '.join(available_models)}")
                    if available_models:
                        self.model = available_models[0]
                        logger.info(f"Falling back to '{self.model}'")
                
                # Connection verified and model available
                return True
            else:
                logger.info(f"Error: Could not check Ollama models. Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.info("Error: Could not connect to Ollama server. Is it running?")
            logger.info("Try starting Ollama with 'ollama serve'")
            return False
        except Exception as e:
            logger.info(f"Error: Could not connect to Ollama server: {str(e)}")
            return False
    
    def generate(self, prompt: str) -> str:
        """Generate text using Ollama API with retry mechanism for timeouts and 404 errors"""
        retries = 0
        backoff = self.retry_delay
        
        # Log the request with a truncated prompt (for privacy/readability)
        truncated_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
        logger.debug(f"Sending request to Ollama model: {self.model}")
        logger.debug(f"Prompt: {truncated_prompt}")
        
        start_time = time.time()
        
        while retries <= self.max_retries:
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
                
                elapsed_time = time.time() - start_time
                logger.debug(f"Request completed in {elapsed_time:.2f} seconds")
                
                # Retry specifically on 404 errors
                if response.status_code == 404:
                    retries += 1
                    if retries <= self.max_retries:
                        error_msg = f"Error: 404 Not Found for URL: {self.base_url}/api/generate"
                        logger.debug(f"{error_msg}. Retrying ({retries}/{self.max_retries}) after {backoff} seconds...")
                        time.sleep(backoff)
                        # Implement exponential backoff
                        backoff *= 1.5
                        continue
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    error_msg = f"Error connecting to Ollama service: {response.status_code} {response.reason}"
                    logger.info(error_msg)
                    
                    # Return a JSON formatted error that can be processed by the system
                    if "JSON" in prompt.upper():
                        return json.dumps({
                            "error": f"Error: {response.status_code} {response.reason}"
                        })
                    return f"Error: {response.status_code} {response.reason}"
                    
            except requests.exceptions.Timeout:
                retries += 1
                if retries <= self.max_retries:
                    logger.debug(f"Request timed out. Retrying ({retries}/{self.max_retries}) after {backoff} seconds...")
                    time.sleep(backoff)
                    # Implement exponential backoff
                    backoff *= 1.5
                else:
                    error_msg = "Error: Maximum retries reached for request timeout"
                    logger.debug(error_msg)
                    elapsed_time = time.time() - start_time
                    logger.indebugfo(f"Request failed after {elapsed_time:.2f} seconds and {retries} retries")
                    
                    # Return a JSON formatted error that can be processed by the system
                    if "JSON" in prompt.upper():
                        return json.dumps({
                            "error": error_msg
                        })
                    return error_msg
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Error connecting to Ollama service: {str(e)}"
                logger.debug(error_msg)
                elapsed_time = time.time() - start_time
                logger.debug(f"Request failed after {elapsed_time:.2f} seconds")
                
                # Return a JSON formatted error that can be processed by the system
                if "JSON" in prompt.upper():
                    return json.dumps({
                        "error": f"Error: {str(e)}"
                    })
                return f"Error: {str(e)}"

        # Return an error if we've exhausted all retries
        error_msg = "Error: Maximum retries reached"
        logger.debug(error_msg)
        elapsed_time = time.time() - start_time
        logger.debug(f"Request failed after {elapsed_time:.2f} seconds and {retries} retries")
        
        # Return a JSON formatted error that can be processed by the system
        if "JSON" in prompt.upper():
            return json.dumps({
                "error": error_msg
            })
        return error_msg

