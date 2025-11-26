import requests # type: ignore
import json
from typing import Optional, Dict, Any

class OllamaClient:
    """Client for interacting with Ollama local AI"""
    
    def __init__(self, base_url="http://localhost:11434", model="llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.api_endpoint = f"{base_url}/api/generate"
        # Conservative per-model token cap. Adjust if you know the model limits.
        # If you run models with larger contexts (e.g. 32k), set this accordingly.
        self.model_max_tokens = 32768
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def estimate_tokens_for_words(self, words: int, factor: float = 1.33, buffer: int = 128) -> int:
        """
        Roughly estimate a token budget for a target word count.

        - `factor` converts words -> tokens (default 1.33 tokens per word).
        - `buffer` adds extra tokens for prompt/context overhead.
        The result is clamped to `self.model_max_tokens - 512` to reserve some context.
        """
        if words <= 0:
            return 0
        tokens = int(words * factor) + int(buffer)
        safe_limit = max(1024, self.model_max_tokens - 512)
        if tokens > safe_limit:
            tokens = safe_limit
        return tokens


    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.8, max_tokens: int = 4000,
                 top_p: float = 0.9, stream: bool = False,
                 max_words: Optional[int] = None) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: The main generation prompt
            system_prompt: Optional system instructions
            temperature: Controls randomness (0.0-1.0, higher = more creative)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
        
        Returns:
            Generated text
        """
        
        # Construct full prompt with system instructions
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Determine token budget. If caller provided `max_words`, prefer that
        # and estimate token count. Otherwise use explicit `max_tokens`.
        if max_words is not None:
            tokens_to_use = self.estimate_tokens_for_words(max_words)
        else:
            tokens_to_use = int(max_tokens)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": tokens_to_use,
                "top_p": top_p,
                "stop": ["</chapter>", "[END]"]
            }
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=300  # 5 minute timeout for long generations
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f"Error: API returned status code {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The generation may be too long."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure it's running."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_chapter(self, prompt: str, temperature: float = 0.85,
                        max_tokens: int = 4500, max_words: Optional[int] = None) -> str:
        """
        Generate a light novel chapter
        Optimized settings for creative fiction
        """
        system_prompt = """You are a talented light novel author specializing in the style of ReZero and Fate series. 
Your writing features:
- Deep internal monologues and character psychology
- Detailed sensory descriptions
- Natural, character-driven dialogue
- Strategic pacing with tension and release
- Vivid action sequences when needed
- Emotional depth and complexity
- Proper light novel formatting with scene breaks

Write engaging, immersive prose that captures the essence of Japanese light novels."""

        # If caller provided `max_words`, forward it to `generate` so callers
        # can request output by word-count instead of raw tokens.
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            max_words=max_words,
            top_p=0.9
        )
    
    def generate_world_details(self, prompt: str, temperature: float = 0.7,
                               max_tokens: int = 2000) -> str:
        """
        Generate world-building details
        Lower temperature for more consistent world-building
        """
        system_prompt = """You are a world-building expert for light novel settings.
Generate detailed, internally consistent world elements that feel authentic and immersive.
Focus on practicality, cultural depth, and how elements interconnect.
Avoid generic fantasy tropes unless specifically requested.
Format your response clearly with headers and organized sections."""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.85
        )
    
    def expand_character(self, prompt: str, temperature: float = 0.75) -> str:
        """
        Generate detailed character information
        """
        system_prompt = """You are a character development specialist for light novels.
Create deep, multi-dimensional characters with realistic motivations, flaws, and growth potential.
Consider their role in the story, relationships, and how they'll evolve.
Write in a detailed but organized format."""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=2000
        )