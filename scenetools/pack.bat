CD /D "%~dp0%"

pyinstaller.exe -F "%~dp0scenetools.py" --distpath .
START "" scenetools.exe