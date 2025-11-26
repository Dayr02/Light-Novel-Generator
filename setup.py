#!/usr/bin/env python3
"""
Setup Script for Light Novel Story Generator
Run this script to verify and set up your environment.
"""

import subprocess
import sys
import os

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} - Need 3.9+")
        return False

def check_tkinter():
    """Check if tkinter is available"""
    print("Checking tkinter...")
    try:
        import tkinter
        print("  ✓ tkinter available")
        return True
    except ImportError:
        print("  ✗ tkinter not found")
        print("    Install with: sudo apt-get install python3-tk (Linux)")
        return False

def install_packages():
    """Install required packages"""
    print("\nInstalling required packages...")
    
    packages = ['requests', 'pillow']
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package} already installed")
        except ImportError:
            print(f"  Installing {package}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package, '-q'
            ])
            print(f"  ✓ {package} installed")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        'database',
        'models', 
        'ai',
        'ui',
        'utils',
        'data'
    ]
    
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        
        # Create __init__.py if needed
        init_file = os.path.join(dir_name, '__init__.py')
        if not os.path.exists(init_file) and dir_name != 'data':
            with open(init_file, 'w') as f:
                f.write(f'"""\n{dir_name.capitalize()} package\n"""\n')
        
        print(f"  ✓ {dir_name}/")
    
    return True

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\nChecking Ollama...")
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("  ✓ Ollama is running")
            
            # Check for models
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print("  Available models:")
                for model in models:
                    print(f"    • {model.get('name', 'unknown')}")
                
                # Check for llama3.1
                llama_found = any('llama3' in m.get('name', '').lower() for m in models)
                if llama_found:
                    print("  ✓ Llama 3 model found")
                else:
                    print("  ⚠ Llama 3.1 not found")
                    print("    Download with: ollama pull llama3.1:8b")
            else:
                print("  ⚠ No models installed")
                print("    Download with: ollama pull llama3.1:8b")
            
            return True
        else:
            raise Exception("Bad response")
    except Exception:
        print("  ⚠ Ollama not running or not installed")
        print("    1. Install from: https://ollama.ai/download")
        print("    2. Run: ollama serve")
        print("    3. Download model: ollama pull llama3.1:8b")
        return False

def create_sample_init_files():
    """Create proper __init__.py files"""
    print("\nCreating package init files...")
    
    init_contents = {
        'database/__init__.py': '''"""
Database package
Database management and operations
"""

from .db_manager import DatabaseManager

__all__ = ['DatabaseManager']
''',
        'ai/__init__.py': '''"""
AI package
AI client and generation utilities
"""

from .ollama_client import OllamaClient
from .prompt_templates import PromptTemplates
from .world_generator import WorldGenerator

__all__ = ['OllamaClient', 'PromptTemplates', 'WorldGenerator']
''',
        'ui/__init__.py': '''"""
UI package
User interface components
"""

from .theme_manager import ThemeManager

__all__ = ['ThemeManager']
''',
        'utils/__init__.py': '''"""
Utils package
Utility functions and configuration
"""

from .config import Config, get_config

__all__ = ['Config', 'get_config']
''',
        'models/__init__.py': '''"""
Models package
Data models (for future expansion)
"""
'''
    }
    
    for filepath, content in init_contents.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {filepath}")
    
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("""
Next Steps:

1. Make sure Ollama is running:
   $ ollama serve

2. Download the AI model (if not done):
   $ ollama pull llama3.1:8b

3. Run the tests:
   $ python test_complete.py

4. Start the application:
   $ python main.py

5. Create your first story and start writing!

For help, see the Quick Start Guide in the Help menu.
""")

def main():
    """Main setup function"""
    print("=" * 60)
    print("Light Novel Story Generator - Setup")
    print("=" * 60)
    print()
    
    all_good = True
    
    if not check_python_version():
        all_good = False
    
    if not check_tkinter():
        all_good = False
    
    if not install_packages():
        all_good = False
    
    if not create_directories():
        all_good = False
    
    if not create_sample_init_files():
        all_good = False
    
    # Ollama is optional for setup
    check_ollama()
    
    if all_good:
        print_next_steps()
    else:
        print("\n⚠ Setup encountered issues. Please fix them and run again.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)