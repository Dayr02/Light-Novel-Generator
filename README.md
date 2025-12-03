📚 Light Novel Story Generator
A comprehensive desktop application for creating and managing light novel stories with AI-powered chapter generation, inspired by the writing styles of ReZero and Fate series.

Run it by applying the following:
python main.py 
in the terminal from system root directory. 

✨ Features
Story Management

Multiple Stories: Create and manage multiple light novel projects
Story Overview: Title, synopsis, genre, themes, tone, writing style

Character System

Role Types: Protagonist, Deuteragonist, Major, Supporting, Minor, Antagonist, Love Interest, Mentor, Rival
Detailed Profiles: Appearance, personality, background, abilities, motivations
Combat & Equipment: Combat style, weapons, important items
Character Arcs: Track development and growth
Voice Style: Speech patterns and quirks
AI Expansion: Use AI to expand character details

World Building

Location Types: Continents, Nations, Cities, Towns, Villages, Regions, Landmarks, Buildings, Dungeons
Detailed Information: Geography, climate, population, government, economy, culture, history
AI Generation: Generate detailed locations with AI

Bestiary

Creature Types: Beast, Monster, Demon, Dragon, Undead, Spirit, Elemental, Construct, Mythical
Threat Levels: Harmless to Catastrophic
Detailed Entries: Description, habitat, behavior, abilities, weaknesses, lore

Power Systems

Complete Systems: Name, description, rules, limitations
Acquisition Methods: How characters gain powers
Power Levels: Progression systems
Examples: Sample abilities

Lore & History

Categories: History, Culture, Religion, Technology, Magic, Events, Legends, Prophecies
Timeline: Track when events occurred
Connections: Link to characters and locations

Organizations

Types: Guild, Kingdom, Empire, Church, Military, Academy, etc.
Structure: Goals, hierarchy, members, resources, relationships

Story Progression

Arc Tracking: Current arc name and number
Plot Points: Current and completed plot points
Character Development: Track growth across chapters
Foreshadowing: Keep track of hints and setup
Unresolved Threads: Track open storylines

Chapter Generation

AI-Powered: Generate complete chapters using Ollama + Llama 3.1
Context-Aware: Uses all your story data for consistency
Customizable: Temperature, word count, POV character
Plot Directives: Guide each chapter's content
Previous Chapter Summary: Maintain continuity

Chapter Management

View All Chapters: List with word counts, status, dates
Edit Chapters: Full editing capability
Status Tracking: Draft, Complete, Revised
Export: Individual or all chapters to text files

User Interface

Light/Dark Themes: Toggle between visual modes
Tabbed Interface: Easy navigation between features
Sidebar: Quick story selection
Status Bar: Current status and AI connection indicator

📁 Project Structure
LightNovelGenerator/  
├── main.py                    # Application entry point  
├── setup.py                   # Setup helper script  
├── test_complete.py           # System tests  
├── config.json                # Configuration (auto-created)  
│  
├── database/  
│   ├── __init__.py  
│   └── db_manager.py          # Database operations  
│  
├── ai/  
│   ├── __init__.py  
│   ├── ollama_client.py       # Ollama AI client  
│   ├── prompt_templates.py    # Generation prompts  
│   └── world_generator.py     # World building AI  
│  
├── ui/  
│   ├── __init__.py  
│   ├── main_window.py         # Main application window  
│   └── theme_manager.py       # Light/Dark themes  
│  
├── utils/  
│   ├── __init__.py  
│   └── config.py              # Configuration management  
│  
├── models/  
│   └── __init__.py            # (For future expansion)  
│  
└── data/  
    └── lightnovel.db          # SQLite database (auto-created)  
  
🚀 Installation
Prerequisites

Python 3.9+ - Download from python.org
Ollama - Download from ollama.ai

Setup Steps
bash# 1. Create project folder
mkdir LightNovelGenerator
cd LightNovelGenerator

# 2. Create virtual environment (recommended)
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 3. Install required packages
pip install requests pillow

# 4. Download Ollama and install the model
ollama pull llama3.1:8b

# 5. Start Ollama server (keep running in background)
ollama serve

# 6. Run setup script
python setup.py

# 7. Test the system
python test_complete.py

# 8. Start the application
python main.py
📖 Quick Start Guide
1. Create a Story

Click "📝 New Story" in the toolbar
Enter title and synopsis
Optionally let AI analyze your synopsis for suggestions

2. Build Your World

Characters Tab: Add protagonist and other characters
World Tab: Create locations and regions
Bestiary Tab: Add creatures and monsters
Lore & Powers Tab: Define magic systems and history

3. Track Progress

Use Progression Tab to track plot points
Note character development
Keep foreshadowing organized

4. Generate Chapters

Go to "Generate Chapter" tab
Enter chapter number and plot directive
Adjust temperature (0.7-0.9 for best results)
Click "Generate Chapter"
Wait 2-5 minutes for generation
Review and save

5. Export Your Work

Export individual chapters as .txt
Export all chapters at once
Chapters include metadata headers

⚙️ Configuration
Edit config.json to customize:
json{
  "ai": {
    "model": "llama3.1:8b",
    "default_temperature": 0.85
  },
  "generation": {
    "default_word_count": 3000
  },
  "ui": {
    "theme": "dark"
  }
}
💡 Tips for Best Results

Add Detailed Character Profiles - More detail = better consistency
Define Power System Rules - Limitations are crucial
Write Specific Plot Directives - "Hero confronts villain in temple" > "Hero fights"
Use Previous Chapter Summaries - Helps continuity
Adjust Temperature: 0.7-0.8 = focused, 0.85-0.95 = creative

🔧 Troubleshooting
Ollama Not Connecting
bash# Make sure Ollama is running
ollama serve

# Check if model is installed
ollama list

# Download if missing
ollama pull llama3.1:8b
Generation Too Slow

Normal: 2-5 minutes per chapter

**Build & Desktop Shortcut (Windows)**

Follow these steps to create a Windows executable and a desktop shortcut with the application icon.

- Install build dependencies (PyInstaller and optional shortcut helpers):

```powershell
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow pywin32 winshell
```

- Create or verify the application icon. The project includes a helper in `build_app.py` that will create a default `icon.ico` if none exists. You can run:

```powershell
python build_app.py
```

This will:
- Ensure required Python packages are installed
- Create `icon.ico` (if missing)
- Generate a PyInstaller spec file
- Build the standalone executable (in `dist\LightNovelGenerator.exe`)
- Attempt to create a desktop shortcut on Windows

- If you prefer to run PyInstaller manually, first ensure `icon.ico` is present then run:

```powershell
pyinstaller LightNovelGenerator.spec --clean --noconfirm
```

- If the automatic Windows shortcut step requires extra packages, run the bundled batch script instead which uses a VBScript approach and does not require extra Python packages:

```powershell
.\create_shortcut.bat
```

Notes:
- The shortcut script looks for `dist\LightNovelGenerator.exe` and `icon.ico` in the project root. If `icon.ico` is missing the exe icon will be used instead.
- To change the icon later: Right-click the desktop shortcut → Properties → Change Icon → Browse to `icon.ico`.

Troubleshooting:
- If PyInstaller fails because of missing hidden imports, rerun `pyinstaller` adding `--hidden-import` flags or run `python build_app.py` which attempts to install missing packages.
- If the shortcut isn't created automatically, run `create_shortcut.bat` manually. If VBScript is blocked by policy, create the shortcut by right-clicking the exe and choosing "Send to → Desktop (create shortcut)".

Enjoy — after building you can launch the app from the Start Menu or the Desktop shortcut.
Close other applications
Use smaller model: ollama pull llama3.1:8b

Database Errors

Check data/ folder exists
Backup and delete lightnovel.db to reset

📄 License
Personal use - Created for story writing and creative projects.
🎉 Enjoy Writing!
Happy creating! May your stories be epic and your chapters flow freely!
