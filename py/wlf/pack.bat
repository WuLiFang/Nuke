CD /D "%UserProfile%"
MKDIR SceneTools
CD SceneTools

pyinstaller.exe -F "%~dp0SceneTools.py"

CD dist
COPY "%~dp0csheet.py"
XCOPY /Y "%~dp0Backdrops" "Backdrops\"
DEL "..\场集工具_v.zip"
"C:\Program Files\7-Zip\7z.exe" a -r0 "..\场集工具_v.zip" "*"
CD ..
EXPLORER %CD%