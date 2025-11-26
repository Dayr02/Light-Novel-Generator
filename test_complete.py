#!/usr/bin/env python3
"""
Complete System Test for Light Novel Story Generator
Run this to verify all components are working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from database.db_manager import DatabaseManager
        print("  ✓ DatabaseManager imported")
    except ImportError as e:
        print(f"  ✗ DatabaseManager import failed: {e}")
        return False
    
    try:
        from ai.ollama_client import OllamaClient
        print("  ✓ OllamaClient imported")
    except ImportError as e:
        print(f"  ✗ OllamaClient import failed: {e}")
        return False
    
    try:
        from ai.prompt_templates import PromptTemplates
        print("  ✓ PromptTemplates imported")
    except ImportError as e:
        print(f"  ✗ PromptTemplates import failed: {e}")
        return False
    
    try:
        from ai.world_generator import WorldGenerator
        print("  ✓ WorldGenerator imported")
    except ImportError as e:
        print(f"  ✗ WorldGenerator import failed: {e}")
        return False
    
    try:
        from ui.theme_manager import ThemeManager
        print("  ✓ ThemeManager imported")
    except ImportError as e:
        print(f"  ✗ ThemeManager import failed: {e}")
        return False
    
    try:
        from utils.config import Config, get_config
        print("  ✓ Config imported")
    except ImportError as e:
        print(f"  ✗ Config import failed: {e}")
        return False
    
    print("  All imports successful!\n")
    return True


def test_database():
    """Test database operations"""
    print("Testing database...")
    
    from database.db_manager import DatabaseManager
    
    # Use test database
    db = DatabaseManager("data/test_lightnovel.db")
    
    # Test story creation
    story_id = db.create_story(
        title="Test Light Novel",
        synopsis="A young hero discovers mysterious powers and must save the world.",
        genre="Fantasy Light Novel",
        themes="Adventure, Mystery, Coming of Age",
        tone="Dark but hopeful",
        writing_style="ReZero/Fate-inspired"
    )
    print(f"  ✓ Created test story (ID: {story_id})")
    
    # Test character creation
    char_id = db.add_character(
        story_id=story_id,
        name="Akira Tanaka",
        role="Protagonist",
        age=17,
        gender="Male",
        personality="Determined but inexperienced, kind-hearted",
        abilities="Unknown latent powers awakening",
        background="Ordinary high school student transported to another world",
        motivations="Find a way home, protect those he cares about"
    )
    print(f"  ✓ Created test character (ID: {char_id})")
    
    # Test location creation
    loc_id = db.add_world_location(
        story_id=story_id,
        name="Luminara Kingdom",
        location_type="Nation",
        description="A medieval fantasy kingdom with ancient magic",
        culture="Honor-based warrior society with deep magical traditions",
        government="Constitutional monarchy with council of mages"
    )
    print(f"  ✓ Created test location (ID: {loc_id})")
    
    # Test power system
    power_id = db.add_power_system(
        story_id=story_id,
        name="Soul Resonance",
        description="Magic system based on harmonizing one's soul with elemental forces",
        rules="Users must meditate to attune to elements; stronger emotions = stronger magic",
        limitations="Overuse causes soul fatigue; cannot use opposing elements"
    )
    print(f"  ✓ Created test power system (ID: {power_id})")
    
    # Test lore
    lore_id = db.add_lore(
        story_id=story_id,
        category="History",
        title="The Great Sundering",
        content="500 years ago, a catastrophic magical event split the world into realms",
        timeline_position="500 years before present",
        importance=5
    )
    print(f"  ✓ Created test lore entry (ID: {lore_id})")
    
    # Test retrieval
    story = db.get_story(story_id)
    characters = db.get_characters(story_id)
    locations = db.get_world_locations(story_id)
    powers = db.get_power_systems(story_id)
    lore = db.get_lore(story_id)
    
    print(f"  ✓ Retrieved story: {story['title']}")
    print(f"  ✓ Retrieved {len(characters)} character(s)")
    print(f"  ✓ Retrieved {len(locations)} location(s)")
    print(f"  ✓ Retrieved {len(powers)} power system(s)")
    print(f"  ✓ Retrieved {len(lore)} lore entry(ies)")
    
    # Cleanup test data
    db.delete_story(story_id)
    print("  ✓ Cleaned up test data")
    
    db.close()
    print("  Database tests passed!\n")
    return True


def test_ai_connection():
    """Test AI connection"""
    print("Testing AI connection...")
    
    from ai.ollama_client import OllamaClient
    
    ai = OllamaClient()
    
    if not ai.test_connection():
        print("  ⚠ Cannot connect to Ollama")
        print("    Make sure Ollama is running: ollama serve")
        print("    AI features will not work without Ollama\n")
        return False
    
    print("  ✓ Connected to Ollama successfully")
    print(f"  ✓ Model: {ai.model}")
    
    # Test simple generation
    print("  Testing generation (this may take 30-60 seconds)...")
    
    result = ai.generate(
        prompt="Write one sentence introducing a hero named Akira.",
        temperature=0.8,
        max_tokens=100
    )
    
    if "Error" in result:
        print(f"  ✗ Generation failed: {result}")
        return False
    
    print(f"  ✓ Generation successful: {result[:80]}...")
    print("  AI tests passed!\n")
    return True


def test_prompt_templates():
    """Test prompt template generation"""
    print("Testing prompt templates...")
    
    from ai.prompt_templates import PromptTemplates
    
    templates = PromptTemplates()
    
    # Test chapter generation prompt
    test_story = {
        'title': 'Test Story',
        'genre': 'Fantasy',
        'themes': 'Adventure',
        'tone': 'Epic',
        'writing_style': 'ReZero-inspired'
    }
    
    test_characters = [{
        'name': 'Hero',
        'role': 'Protagonist',
        'age': 17,
        'gender': 'Male',
        'appearance': 'Dark hair, determined eyes',
        'personality': 'Brave but reckless',
        'abilities': 'Unknown powers',
        'background': 'Ordinary student',
        'motivations': 'Protect friends',
        'voice_style': 'Casual, determined',
        'character_arc': 'Zero to hero',
        'importance': 5,
        'relationships': 'Close with companions'
    }]
    
    prompt = templates.chapter_generation_prompt(
        story_info=test_story,
        characters=test_characters,
        world_info=[],
        power_systems=[],
        lore=[],
        progression={},
        chapter_number=1,
        plot_directive="Introduce the protagonist in an exciting opening scene.",
        previous_chapter_summary=""
    )
    
    if len(prompt) > 500:
        print(f"  ✓ Chapter prompt generated ({len(prompt)} characters)")
    else:
        print("  ✗ Chapter prompt too short")
        return False
    
    # Test world generation prompt
    world_prompt = templates.world_generation_prompt(
        story_info=test_story,
        existing_world=[],
        generation_focus="Location",
        specific_request="Create a magical academy"
    )
    
    if len(world_prompt) > 200:
        print(f"  ✓ World prompt generated ({len(world_prompt)} characters)")
    else:
        print("  ✗ World prompt too short")
        return False
    
    print("  Prompt template tests passed!\n")
    return True


def test_theme_manager():
    """Test theme manager"""
    print("Testing theme manager...")
    
    from ui.theme_manager import ThemeManager
    
    tm = ThemeManager()
    
    # Test light theme
    light = tm.get_theme('light')
    if 'bg' in light and 'fg' in light:
        print("  ✓ Light theme loaded")
    else:
        print("  ✗ Light theme missing keys")
        return False
    
    # Test dark theme
    dark = tm.get_theme('dark')
    if 'bg' in dark and 'fg' in dark:
        print("  ✓ Dark theme loaded")
    else:
        print("  ✗ Dark theme missing keys")
        return False
    
    # Test theme toggle
    initial = tm.current_theme
    tm.toggle_theme()
    if tm.current_theme != initial:
        print("  ✓ Theme toggle works")
    else:
        print("  ✗ Theme toggle failed")
        return False
    
    print("  Theme manager tests passed!\n")
    return True


def test_config():
    """Test configuration manager"""
    print("Testing config manager...")
    
    from utils.config import Config
    
    config = Config("test_config.json")
    
    # Test default values
    if config.ai_model:
        print(f"  ✓ AI model: {config.ai_model}")
    else:
        print("  ✗ AI model not found")
        return False
    
    # Test get/set
    config.set('test', 'key', value='test_value')
    if config.get('test', 'key') == 'test_value':
        print("  ✓ Config get/set works")
    else:
        print("  ✗ Config get/set failed")
        return False
    
    # Test style presets
    presets = config.get_all_style_presets()
    if len(presets) > 0:
        print(f"  ✓ Found {len(presets)} style presets")
    else:
        print("  ✗ No style presets found")
        return False
    
    # Cleanup
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("  Config manager tests passed!\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Light Novel Story Generator - System Test")
    print("=" * 60)
    print()
    
    results = {
        'imports': test_imports(),
        'database': test_database(),
        'templates': test_prompt_templates(),
        'themes': test_theme_manager(),
        'config': test_config(),
        'ai': test_ai_connection()
    }
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name.capitalize():15} {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ All tests passed!")
        print()
        print("You can now run the application with:")
        print("  python main.py")
    else:
        print("⚠ Some tests failed!")
        print()
        if not results['ai']:
            print("AI connection failed - make sure Ollama is running:")
            print("  1. Open terminal")
            print("  2. Run: ollama serve")
            print("  3. Verify model: ollama list")
            print()
        print("Fix the issues above and run tests again.")
    
    print()
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)