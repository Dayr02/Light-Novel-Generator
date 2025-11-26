"""
Complete application build script for Light Novel Generator
Creates standalone executable with custom icon and installer
"""

import os
import sys
import shutil
import subprocess
import platform

def check_requirements():
    """Check if all requirements are installed"""
    print("Checking requirements...")
    
    required_packages = ['requests', 'Pillow', 'pyinstaller']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling missing packages...")
        for pkg in missing:
            subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=True)
        print("✓ All packages installed")
    
    return True

def create_default_icon():
    """Create a default icon if none exists"""
    if os.path.exists('icon.ico'):
        print("✓ Icon file found")
        return True
    
    print("Creating default icon...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 256x256 image with gradient background
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background (blue to purple)
        for y in range(size):
            r = int(74 + (y / size) * 50)
            g = int(158 - (y / size) * 80)
            b = int(255 - (y / size) * 50)
            draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
        # Draw book icon shape
        book_color = (255, 255, 255, 230)
        
        # Book cover
        draw.rounded_rectangle([40, 50, 216, 206], radius=10, fill=book_color)
        
        # Book spine
        draw.rectangle([40, 50, 60, 206], fill=(200, 200, 200, 255))
        
        # Book pages
        for i in range(3):
            offset = i * 3
            draw.line([(65 + offset, 60), (65 + offset, 196)], 
                     fill=(180, 180, 180, 255), width=1)
        
        # Text lines on book
        line_color = (100, 100, 100, 200)
        draw.rectangle([80, 80, 180, 90], fill=line_color)
        draw.rectangle([80, 100, 160, 108], fill=line_color)
        draw.rectangle([80, 118, 190, 126], fill=line_color)
        draw.rectangle([80, 136, 150, 144], fill=line_color)
        
        # Pen/quill
        pen_color = (255, 215, 0, 255)
        draw.polygon([(180, 160), (220, 200), (210, 210), (170, 170)], fill=pen_color)
        draw.polygon([(220, 200), (230, 220), (210, 210)], fill=(50, 50, 50, 255))
        
        # Save as ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save('icon.ico', format='ICO', sizes=sizes)
        
        print("✓ Default icon created")
        return True
        
    except Exception as e:
        print(f"⚠ Could not create icon: {e}")
        return False

def create_spec_file():
    """Create PyInstaller spec file for custom build"""
    
    icon_line = "icon='icon.ico'," if os.path.exists('icon.ico') else "icon=None,"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('models', 'models'),
        ('ai', 'ai'),
        ('ui', 'ui'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'sqlite3',
        'requests',
        'json',
        'datetime',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LightNovelGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)
'''
    
    with open('LightNovelGenerator.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Spec file created")

def build_executable():
    """Build the executable"""
    print("\n🔨 Building executable...")
    print("This may take 2-5 minutes...\n")
    
    cmd = ['pyinstaller', 'LightNovelGenerator.spec', '--clean', '--noconfirm']
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False

def create_shortcut_windows():
    """Create desktop shortcut on Windows"""
    if platform.system() != 'Windows':
        return
    
    print("\nCreating desktop shortcut...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Light Novel Generator.lnk")
        
        exe_path = os.path.abspath(os.path.join('dist', 'LightNovelGenerator.exe'))
        icon_path = os.path.abspath('icon.ico') if os.path.exists('icon.ico') else exe_path
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = icon_path
        shortcut.Description = "Light Novel Story Generator"
        shortcut.save()
        
        print(f"✓ Shortcut created: {path}")
        
    except ImportError:
        print("⚠ Install pywin32 and winshell for automatic shortcut:")
        print("  pip install pywin32 winshell")
        create_shortcut_script()

def create_shortcut_script():
    """Create a script to make shortcut manually"""
    
    script = '''@echo off
echo Creating desktop shortcut...

set SCRIPT="%TEMP%\\CreateShortcut.vbs"
set EXE_PATH="%~dp0dist\\LightNovelGenerator.exe"
set ICON_PATH="%~dp0icon.ico"
set SHORTCUT="%USERPROFILE%\\Desktop\\Light Novel Generator.lnk"

echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = %SHORTCUT% >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %EXE_PATH% >> %SCRIPT%
echo oLink.IconLocation = %ICON_PATH% >> %SCRIPT%
echo oLink.Description = "Light Novel Story Generator" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%

echo Done! Shortcut created on desktop.
pause
'''
    
    with open('create_shortcut.bat', 'w') as f:
        f.write(script)
    
    print("✓ Created create_shortcut.bat - Run it to create desktop shortcut")

def create_linux_desktop_entry():
    """Create .desktop file for Linux"""
    if platform.system() != 'Linux':
        return
    
    desktop_entry = '''[Desktop Entry]
Version=1.0
Type=Application
Name=Light Novel Generator
Comment=AI-powered light novel story generator
Exec={exe_path}
Icon={icon_path}
Terminal=false
Categories=Office;Writing;
'''
    
    exe_path = os.path.abspath(os.path.join('dist', 'LightNovelGenerator'))
    icon_path = os.path.abspath('icon.png') if os.path.exists('icon.png') else ''
    
    content = desktop_entry.format(exe_path=exe_path, icon_path=icon_path)
    
    desktop_file = os.path.expanduser('~/.local/share/applications/lightnovelgenerator.desktop')
    
    with open(desktop_file, 'w') as f:
        f.write(content)
    
    os.chmod(desktop_file, 0o755)
    print(f"✓ Desktop entry created: {desktop_file}")

def create_mac_app_bundle():
    """Instructions for macOS app bundle"""
    if platform.system() != 'Darwin':
        return
    
    print("\n📱 macOS App Bundle:")
    print("The executable is in dist/LightNovelGenerator")
    print("To create an app bundle, use py2app or create manually:")
    print("1. Create LightNovelGenerator.app/Contents/MacOS/")
    print("2. Copy executable there")
    print("3. Create Info.plist with app metadata")

def clean_build():
    """Clean build artifacts"""
    print("\nCleaning previous builds...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['LightNovelGenerator.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"  Removed {file_name}")

def print_final_instructions():
    """Print final instructions"""
    
    exe_name = 'LightNovelGenerator.exe' if platform.system() == 'Windows' else 'LightNovelGenerator'
    exe_path = os.path.abspath(os.path.join('dist', exe_name))
    
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETE!")
    print("=" * 60)
    print(f"""
Executable Location:
  {exe_path}

To run the application:
  1. Double-click the executable, OR
  2. Run from command line: {exe_path}

To create a desktop shortcut:
""")
    
    if platform.system() == 'Windows':
        print("  • Run create_shortcut.bat, OR")
        print("  • Right-click exe → Send to → Desktop (create shortcut)")
        print("  • To change icon: Right-click shortcut → Properties → Change Icon")
    elif platform.system() == 'Linux':
        print("  • Desktop entry created in ~/.local/share/applications/")
        print("  • Or create shortcut manually in your desktop environment")
    else:
        print("  • Drag the app to your Applications folder")
        print("  • Or create an alias on your desktop")
    
    print("""
IMPORTANT: 
  • Make sure Ollama is running before starting the app
  • The app will create a 'data' folder for the database
  • First run may take a moment to initialize

Enjoy writing your light novels! 📚
""")

def main():
    """Main build process"""
    print("=" * 60)
    print("🔨 Light Novel Generator - Build Tool")
    print("=" * 60)
    print()
    
    # Parse arguments
    if '--clean' in sys.argv:
        clean_build()
        if '--clean-only' in sys.argv:
            return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Create icon
    create_default_icon()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        print("\n❌ Build failed. Check errors above.")
        return
    
    # Create shortcuts based on platform
    if platform.system() == 'Windows':
        create_shortcut_windows()
    elif platform.system() == 'Linux':
        create_linux_desktop_entry()
    elif platform.system() == 'Darwin':
        create_mac_app_bundle()
    
    # Print final instructions
    print_final_instructions()

if __name__ == "__main__":
    main()