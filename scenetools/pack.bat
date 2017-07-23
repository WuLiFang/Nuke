CD /D "%~dp0"

CALL :dirname %CD%
pyinstaller.exe --hidden-import shutil --add-data "%_%py\\;py\\" -F "%~dp0scenetools.py" --distpath .
START "" scenetools.exe

GOTO :EOF

:dirname
SET "_=%~dp1"