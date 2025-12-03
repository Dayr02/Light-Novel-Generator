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
        # llama3.1:8b has 8192 context window, use 4096 for safety
        self.model_max_tokens = 8192
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def estimate_tokens_for_words(self, words: int, factor: float = 1.5, buffer: int = 512) -> int:
        """
        Estimate token budget for target word count.

        - `factor`: tokens per word (1.5 is more accurate for narrative text)
        - `buffer`: safety margin for variation
        Returns tokens clamped to safe model limits.
        """
        if words <= 0:
            return 2048  # Minimum reasonable generation

        # More accurate token estimation for narrative prose
        tokens = int(words * factor) + buffer

        # Reserve more context for the prompt (4096 tokens)
        safe_limit = max(2048, self.model_max_tokens - 4096)

        if tokens > safe_limit:
            tokens = safe_limit

        return tokens


    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.8, max_tokens: int = 4000,
                 top_p: float = 0.9, stream: bool = False,
                 max_words: Optional[int] = None) -> str:
        """
        Generate text using Ollama with improved token handling

        Args:
            prompt: The main generation prompt
            system_prompt: Optional system instructions
            temperature: Controls randomness (0.0-1.0, higher = more creative)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            max_words: Target word count (preferred over max_tokens)

        Returns:
            Generated text
        """

        # Construct full prompt with system instructions
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        # Determine token budget
        if max_words is not None:
            tokens_to_use = self.estimate_tokens_for_words(max_words)
            print(f"[TARGET] {max_words} words -> {tokens_to_use} tokens")
        else:
            tokens_to_use = int(max_tokens)

        # Build options - don't include num_ctx if it exceeds safe limits
        options = {
            "temperature": temperature,
            "num_predict": tokens_to_use,
            "top_p": top_p,
            "stop": ["</chapter>", "[END]"],
        }
        
        # Only set num_ctx if it's reasonable for the model
        if self.model_max_tokens <= 8192:
            options["num_ctx"] = 8192

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": options
        }

        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=600  # 10 minute timeout for long generations
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')

                # Verify word count if target was specified
                if max_words and generated_text:
                    actual_words = len(generated_text.split())
                    print(f"[RESULT] Generated {actual_words} words (target: {max_words})")

                    # If significantly short, warn user
                    if actual_words < max_words * 0.7:
                        print(f"[WARNING] Generation fell short of target by {max_words - actual_words} words")

                return generated_text
            else:
                return f"Error: API returned status code {response.status_code}"

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try reducing the target word count."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure it's running."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_chapter(self, prompt: str, temperature: float = 0.85,
                        max_tokens: int = 4500, max_words: Optional[int] = None) -> str:
        """
        Generate a light novel chapter with optimized settings
        """
        system_prompt = """You are a talented light novel author specializing in ReZero and Fate series style.

        CRITICAL: Write a COMPLETE chapter with the target word count. Do not stop early.

        Your writing features:
        - Deep internal monologues and character psychology
        - Detailed sensory descriptions and atmosphere
        - Natural, character-driven dialogue with unique voices
        - Strategic pacing with tension and emotional beats
        - Vivid action sequences when appropriate
        - Emotional depth and character growth
        - Proper scene breaks (◇◇◇) between major transitions
        Write immersive prose that captures Japanese light novel essence. WRITE THE FULL CHAPTER LENGTH."""

        # Always prefer max_words over max_tokens for chapters
        if max_words is None and max_tokens:
            # Estimate words from tokens (rough conversion)
            max_words = int(max_tokens / 1.5)

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