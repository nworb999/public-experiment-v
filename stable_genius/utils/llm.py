from dotenv import load_dotenv
import json
import requests
import sys
import time
from stable_genius.utils.logger import logger
import os
import anthropic

load_dotenv()

# MODEL_NAME = "llama3.3:70b-instruct-q2_K"
# MODEL_NAME = "llama3:8b"
MODEL_NAME = "claude-3-5-sonnet-20241022"
ANTHROPIC_KEY = os.getenv('ANTHROPIC_KEY')

class OllamaLLM:
    """Interface to the Ollama API for LLM generation"""
    
    def __init__(self, model=MODEL_NAME, max_retries=10, retry_delay=2, use_local=True):
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Determine if this is an Anthropic model
        self.is_anthropic_model = model.startswith('claude-')
        
        if self.is_anthropic_model:
            # Use Anthropic API directly
            if not ANTHROPIC_KEY:
                logger.info("ERROR: ANTHROPIC_KEY environment variable not set")
                sys.exit(1)
            self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            self.base_url = None
            self.anthropic_key = None
        else:
            # Use Ollama API
            self.base_url = "http://localhost:11434" if use_local else "https://api.ollama.com"
            self.anthropic_client = None
            self.anthropic_key = ANTHROPIC_KEY if not use_local else None
            # Verify connection on initialization - exit if Ollama is not available
            if use_local and not self._verify_connection():
                logger.info("ERROR: Cannot continue without Ollama connection. Please start Ollama and try again.")
                sys.exit(1)
        
        # Store LLM interactions
        self.interactions = []
    
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
    
    def generate(self, prompt: str, context: dict = None) -> str:
        """Generate text using either Anthropic API or Ollama API based on model type"""
        if self.is_anthropic_model:
            return self._generate_anthropic(prompt, context)
        else:
            return self._generate_ollama(prompt, context)
    
    def _generate_anthropic(self, prompt: str, context: dict = None) -> str:
        """Generate text using Anthropic API"""
        # Log the request with a truncated prompt (for privacy/readability)
        truncated_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
        logger.info(f"🔄 LLM REQUEST STARTED: Model={self.model}")
        logger.debug(f"Prompt: {truncated_prompt}")
        
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            elapsed_time = time.time() - start_time
            response_text = response.content[0].text
            
            # Record interaction with context if provided
            self._record_interaction(prompt, response_text, timestamp, elapsed_time, context)
            logger.info(f"✅ LLM RESPONSE RECEIVED: Time={elapsed_time:.2f}s")
            return response_text
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = f"Error calling Anthropic API: {str(e)}"
            logger.info(f"❌ LLM REQUEST FAILED: {str(e)}, Time={elapsed_time:.2f}s")
            logger.debug(error_msg)
            
            # Return the failed prompt with the error message
            if "JSON" in prompt.upper():
                error_response = json.dumps({"error": f"Error: {str(e)}", "prompt": prompt})
            else:
                error_response = f"Error: {str(e)}\nFailed prompt: {prompt}"
            
            # Record the error interaction
            self._record_interaction(prompt, error_response, timestamp, elapsed_time, context)
            return error_response
    
    def _generate_ollama(self, prompt: str, context: dict = None) -> str:
        """Generate text using Ollama API with retry mechanism for timeouts and 404 errors"""
        retries = 0
        backoff = self.retry_delay
        
        # Log the request with a truncated prompt (for privacy/readability)
        truncated_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
        logger.info(f"🔄 LLM REQUEST STARTED: Model={self.model}")
        logger.debug(f"Prompt: {truncated_prompt}")
        
        start_time = time.time()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        while retries <= self.max_retries:
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "anthropic_key": self.anthropic_key
                    },
                    timeout=30  # Add a timeout to prevent hanging
                )
                
                elapsed_time = time.time() - start_time
                
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
                    response_text = response.json().get("response", "")
                    # Record interaction with context if provided
                    self._record_interaction(prompt, response_text, timestamp, elapsed_time, context)
                    logger.info(f"✅ LLM RESPONSE RECEIVED: Time={elapsed_time:.2f}s")
                    return response_text
                else:
                    error_msg = f"Error connecting to Ollama service: {response.status_code} {response.reason}"
                    logger.info(f"❌ LLM REQUEST FAILED: Status={response.status_code}, Time={elapsed_time:.2f}s")
                    logger.info(error_msg)
                    
                    # Return the failed prompt with the error message
                    error_response = f"Error: {response.status_code} {response.reason}"
                    if "JSON" in prompt.upper():
                        error_response = json.dumps({"error": error_response, "prompt": prompt})
                    else:
                        error_response = f"{error_response}\nFailed prompt: {prompt}"
                    
                    # Record the error interaction
                    self._record_interaction(prompt, error_response, timestamp, elapsed_time, context)
                    return error_response
                    
            except requests.exceptions.Timeout:
                retries += 1
                if retries <= self.max_retries:
                    logger.debug(f"Request timed out. Retrying ({retries}/{self.max_retries}) after {backoff} seconds...")
                    time.sleep(backoff)
                    # Implement exponential backoff
                    backoff *= 1.5
                else:
                    error_msg = "Error: Maximum retries reached for request timeout"
                    elapsed_time = time.time() - start_time
                    logger.info(f"❌ LLM REQUEST FAILED: Maximum retries reached, Time={elapsed_time:.2f}s")
                    logger.debug(error_msg)
                    
                    # Return the failed prompt with the error message
                    if "JSON" in prompt.upper():
                        error_response = json.dumps({"error": error_msg, "prompt": prompt})
                    else:
                        error_response = f"{error_msg}\nFailed prompt: {prompt}"
                    
                    # Record the error interaction
                    self._record_interaction(prompt, error_response, timestamp, elapsed_time, context)
                    return error_response
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Error connecting to Ollama service: {str(e)}"
                elapsed_time = time.time() - start_time
                logger.info(f"❌ LLM REQUEST FAILED: {str(e)}, Time={elapsed_time:.2f}s")
                logger.debug(error_msg)
                
                # Return the failed prompt with the error message
                if "JSON" in prompt.upper():
                    error_response = json.dumps({"error": f"Error: {str(e)}", "prompt": prompt})
                else:
                    error_response = f"Error: {str(e)}\nFailed prompt: {prompt}"
                
                # Record the error interaction
                self._record_interaction(prompt, error_response, timestamp, elapsed_time, context)
                return error_response

        # Return an error if we've exhausted all retries
        error_msg = "Error: Maximum retries reached"
        elapsed_time = time.time() - start_time
        logger.info(f"❌ LLM REQUEST FAILED: Maximum retries reached, Time={elapsed_time:.2f}s")
        logger.debug(error_msg)
        
        # Return the failed prompt with the error message
        if "JSON" in prompt.upper():
            error_response = json.dumps({"error": error_msg, "prompt": prompt})
        else:
            error_response = f"{error_msg}\nFailed prompt: {prompt}"
        
        # Record the error interaction
        self._record_interaction(prompt, error_response, timestamp, elapsed_time, context)
        return error_response
        
    def _record_interaction(self, prompt, response, timestamp, elapsed_time, context=None):
        """Record an LLM interaction with optional context information"""
        interaction = {
            'prompt': prompt,
            'response': response,
            'timestamp': timestamp,
            'elapsed_time': f"{elapsed_time:.2f}s",
            'model': self.model
        }
        
        # Add any additional context if provided
        if context:
            interaction.update(context)
            
        self.interactions.append(interaction)
        
    def get_interactions(self):
        """Return all recorded interactions"""
        return self.interactions
        
    def clear_interactions(self):
        """Clear all recorded interactions"""
        self.interactions = []
