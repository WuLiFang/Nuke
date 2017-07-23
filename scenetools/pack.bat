CD /D "%~dp0%"

pyinstaller.exe --hidden-import shutil -F "%~dp0scenetools.py" --distpath .
START "" scenetools.exe