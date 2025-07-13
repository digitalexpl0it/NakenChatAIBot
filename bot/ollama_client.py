import aiohttp
import asyncio
from typing import Optional, Dict, Any
import json

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, config: Dict[str, Any], logger, bot_name: str = "AI Assistant"):
        self.config = config['ollama']
        self.logger = logger
        self.bot_name = bot_name
        self.base_url = f"{self.config['host']}:{self.config['port']}"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config['timeout'])
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def generate_response(self, prompt: str, context: str = "", model: Optional[str] = None) -> Optional[str]:
        """Generate response from Ollama API"""
        if not self.session:
            self.logger.error("Ollama client not initialized. Use async context manager.")
            return None
        
        model = model or self.config['model']
        
        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)
        
        # Prepare request payload
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "num_predict": self.config['max_tokens'],
                "temperature": self.config['temperature']
            }
        }
        
        try:
            self.logger.debug(f"Generating response with model: {model}")
            self.logger.debug(f"Prompt: {full_prompt[:100]}...")
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Ollama API error {response.status}: {error_text}")
                    return None
                
                data = await response.json()
                
                if 'response' not in data:
                    self.logger.error(f"Unexpected Ollama response format: {data}")
                    return None
                
                response_text = data['response'].strip()
                self.logger.debug(f"Generated response: {response_text[:100]}...")
                
                return response_text
                
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error connecting to Ollama: {e}")
            return None
        except asyncio.TimeoutError:
            self.logger.error("Timeout while generating response from Ollama")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error generating response: {e}")
            return None
    
    def _build_prompt(self, prompt: str, context: str = "") -> str:
        """Build the full prompt with system message and context"""
        system_prompt = self.config['system_prompt']
        
        # Replace {bot_name} placeholder with actual bot name
        system_prompt = system_prompt.replace('{bot_name}', self.bot_name)
        
        if context:
            full_prompt = f"{system_prompt}\n\nRecent conversation:\n{context}\n\nUser: {prompt}\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        return full_prompt
    
    async def list_models(self) -> Optional[list]:
        """List available models from Ollama"""
        if not self.session:
            self.logger.error("Ollama client not initialized")
            return None
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    self.logger.error(f"Failed to list models: {response.status}")
                    return None
                
                data = await response.json()
                models = [model['name'] for model in data.get('models', [])]
                self.logger.info(f"Available models: {models}")
                return models
                
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return None
    
    async def check_model_exists(self, model: str) -> bool:
        """Check if a specific model exists"""
        models = await self.list_models()
        if models is None:
            return False
        
        return model in models
    
    async def test_connection(self) -> bool:
        """Test connection to Ollama API"""
        try:
            models = await self.list_models()
            return models is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False 