#!/usr/bin/env python3
"""
Simple script to test the connection to Ollama server
"""
import requests
import json
import sys
from stable_genius.utils.logger import logger

def test_ollama_connection():
    """Test if Ollama is running and responding"""
    logger.info("Testing connection to Ollama server...")
    
    base_url = "http://localhost:11434"
    
    try:
        # Test basic connection
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            logger.info(f"✅ Successfully connected to Ollama server")
            
            if models:
                logger.info(f"Available models: {', '.join([m['name'] for m in models])}")
            else:
                logger.info("No models found. You may need to pull a model first.")
            
            # Test basic generation if models exist
            if models:
                test_model = models[0]['name']
                logger.info(f"\nTesting generation with {test_model}...")
                
                prompt_response = requests.post(
                    f"{base_url}/api/generate",
                    json={
                        "model": test_model,
                        "prompt": "Say hello in one short sentence.",
                        "stream": False
                    }
                )
                
                if prompt_response.status_code == 200:
                    result = prompt_response.json()
                    logger.info(f"✅ Model response: {result.get('response', '(no response)')}")
                else:
                    logger.info(f"❌ Failed to generate response: {prompt_response.status_code}")
                    logger.info(prompt_response.text)
            
            return True
        else:
            logger.info(f"❌ Connection failed with status code: {response.status_code}")
            logger.info(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        logger.info("❌ Failed to connect to Ollama server at localhost:11434")
        logger.info("Make sure Ollama is running. You can start it with:")
        logger.info("  ollama serve")
        return False
    except Exception as e:
        logger.info(f"❌ Error testing Ollama connection: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    if not success:
        sys.exit(1) 