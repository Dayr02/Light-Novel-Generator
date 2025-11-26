#!/usr/bin/env python3
"""
Light Novel Story Generator
Main application entry point

A comprehensive tool for creating and managing light novel stories
with AI-powered chapter generation using local Ollama models.

Features:
- Complete character management with detailed profiles
- World building tools (locations, regions, landmarks)
- Bestiary for creatures and monsters
- Lore and power system tracking
- Story progression tracking
- AI-powered chapter generation
- Light/Dark theme support
- Export functionality

Usage:
    python main.py

Requirements:
    - Python 3.9+
    - Ollama with llama3.1:8b model
    - Required packages: requests, pillow
"""

import sys
import os

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def check_requirements():
    """Check that all requirements are met before starting"""
    errors = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        errors.append(f"Python 3.9+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
    
    # Check tkinter
    try:
        import tkinter
    except ImportError:
        errors.append("tkinter not found - install python3-tk")
    
    # Check requests
    try:
        import requests
    except ImportError:
        errors.append("requests not found - run: pip install requests")
    
    # Check Ollama (warning only)
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=3)
        if response.status_code != 200:
            warnings.append("Ollama not responding properly")
    except:
        warnings.append("Ollama not running - AI features will not work")
    
    return errors, warnings

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           📚 Light Novel Story Generator 📚                 ║
║                                                              ║
║                Story/Chapter Generation                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main application entry point"""
    print_banner()
    
    print("Checking requirements...")
    errors, warnings = check_requirements()
    
    if errors:
        print("\n❌ Cannot start - missing requirements:")
        for error in errors:
            print(f"   • {error}")
        print("\nPlease fix these issues and try again.")
        print("Run 'python setup.py' for help with setup.")
        sys.exit(1)
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
        print()
    
    print("Starting application...")
    print()
    
    try:
        # Import and create application
        from ui.main_window import MainWindow
        
        # Create and run application
        app = MainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication closed by user.")
        sys.exit(0)
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nMake sure all files are in place:")
        print("   • database/db_manager.py")
        print("   • ai/ollama_client.py")
        print("   • ai/prompt_templates.py")
        print("   • ai/world_generator.py")
        print("   • ui/main_window.py")
        print("   • ui/theme_manager.py")
        print("   • utils/config.py")
        print("\nRun 'python setup.py' to create missing files.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        print("\nIf this persists, try:")
        print("   1. Run 'python test_complete.py' to check components")
        print("   2. Check that Ollama is running: 'ollama serve'")
        print("   3. Verify the database: check data/lightnovel.db")
        sys.exit(1)

if __name__ == "__main__":
    main()