@echo off
REM Change to project directory (script location)
cd /d "%~dp0"

REM Optional: activate virtualenv (uncomment & update path if used)
REM call venv\Scripts\activate

echo Running setup...
python setup.py

echo Running tests...
python test_complete.py

echo Starting application...
python main.py

REM Keep console open after the app exits
pause