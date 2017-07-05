REM CD /D "%UserProfile%"
CD /D "%~dp0%"
REM MKDIR SceneTools
REM CD SceneTools

pyinstaller.exe -F "%~dp0scenetools.py" --distpath .

REM CD dist
REM COPY "%~dp0csheet.py"
REM XCOPY /Y "%~dp0Backdrops" "Backdrops\"
REM DEL "..\场集工具_v.zip"
REM "C:\Program Files\7-Zip\7z.exe" a -r0 "..\场集工具_v.zip" "*"
REM CD ..
REM EXPLORER %CD%