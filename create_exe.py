"""
Script to create standalone executable
"""

import PyInstaller.__main__
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Icon file path (you'll create this)
icon_path = os.path.join(script_dir, 'icon.ico')

# PyInstaller arguments
args = [
    'main.py',                              # Your main script
    '--name=LightNovelGenerator',           # Application name
    '--onefile',                            # Single executable
    '--windowed',                           # No console window
    f'--icon={icon_path}' if os.path.exists(icon_path) else '',  # Application icon
    '--add-data=database;database',         # Include database module
    '--add-data=models;models',             # Include models module
    '--add-data=ai;ai',                     # Include AI module
    '--add-data=ui;ui',                     # Include UI module
    '--add-data=utils;utils',               # Include utils module
    '--hidden-import=tkinter',              # Ensure tkinter is included
    '--hidden-import=sqlite3',              # Ensure sqlite3 is included
    '--hidden-import=requests',             # Ensure requests is included
    '--clean',                              # Clean build cache
    '--noconfirm',                          # Overwrite without asking
]

# Remove empty strings
args = [arg for arg in args if arg]

print("Building executable...")
print(f"Icon: {'Found' if os.path.exists(icon_path) else 'Not found (using default)'}")
print()

PyInstaller.__main__.run(args)

print("\n✅ Build complete!")
print(f"Executable location: {os.path.join(script_dir, 'dist', 'LightNovelGenerator.exe')}")