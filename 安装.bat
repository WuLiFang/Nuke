@ECHO off
SET "TEXT=nuke.pluginAddPath(r'%~dp0')"
SET "FILE=%UserProfile%\.nuke\init.py"

FIND /C /I "%TEXT%" "%FILE%" >nul 2>nul
IF %ERRORLEVEL% NEQ 0 ECHO.>>"%FILE%" && ECHO %TEXT%>>"%FILE%"

START "" notepad.exe  "%FILE%"

ECHO 如果弹出的记事本中有内容, 说明安装成功
ECHO 重启Nuke即可
ECHO.
PAUSE