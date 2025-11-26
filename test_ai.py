from ai.ollama_client import OllamaClient

def test_ollama():
    print("Testing Ollama connection...")
    
    ai = OllamaClient()
    
    # Test connection
    if not ai.test_connection():
        print("❌ Cannot connect to Ollama!")
        print("Make sure Ollama is running.")
        print("Try running: ollama serve")
        return
    
    print("✓ Connected to Ollama successfully!")
    
    # Test simple generation
    print("\nTesting text generation...")
    result = ai.generate(
        prompt="Write a single paragraph introducing a protagonist named Akira in a light novel style.",
        temperature=0.8,
        max_tokens=200
    )
    
    print("\nGenerated text:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    if "Error" not in result:
        print("\n✅ AI generation test successful!")
    else:
        print("\n❌ AI generation failed!")
        print(result)

if __name__ == "__main__":
    test_ollama()