@echo off
echo Creating desktop shortcut...

set SCRIPT="%TEMP%\CreateShortcut.vbs"
set EXE_PATH="%~dp0dist\LightNovelGenerator.exe"
set ICON_PATH="%~dp0icon.ico"
:: Use the public desktop so the shortcut is available to all users (requires admin)
set SHORTCUT="%PUBLIC%\Desktop\Light Novel Generator.lnk"

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
