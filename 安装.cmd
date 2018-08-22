@ECHO off
CHCP 65001
setlocal ENABLEDELAYEDEXPANSION
SET "DIRNAME=%~dp0"
SET "DIRNAME=%DIRNAME:\=/%"
SET "TEXT=nuke.pluginAddPath('%DIRNAME%')"
SET "FILE=%UserProfile%\.nuke\init.py"

IF NOT EXIST %FILE% (ECHO import nuke > %FILE%)

FIND /C /I "%TEXT%" "%FILE%" >nul 2>nul
IF %ERRORLEVEL% EQU 0 (GOTO Success)

ECHO.>>"%FILE%" && ECHO %TEXT%>>"%FILE%"

FIND /C /I "%TEXT%" "%FILE%" >nul 2>nul
IF %ERRORLEVEL% EQU 0 (GOTO Success) ELSE (GOTO Fail)

:Success
ECHO -----当前init.py内容------
TYPE "%FILE%"
ECHO -------------------------
ECHO 安装成功
ECHO 重启Nuke即可
ECHO.
PAUSE
GOTO :EOF

:Fail
ECHO 插件安装失败, 请确认能够手动编辑 %FILE% 后重试
ECHO.
PAUSE
GOTO :EOF
