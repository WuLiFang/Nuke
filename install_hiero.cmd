@ECHO off
CHCP 65001
SET "DEST=%UserProfile%\.nuke\Python\Startup"
IF NOT EXIST %DEST% MKDIR %DEST%
SET "FILE=%DEST%\com-wulifang-sudito-hiero-plugin-startup.py"
SET "DIRNAME=%~dp0"
SET "DIRNAME=%DIRNAME:\=/%"
SET "TEXT=hiero.core.addPluginPath('%DIRNAME%')"

ECHO # -*- coding=UTF-8 -*- > %FILE%
ECHO import hiero.core >> %FILE%
ECHO.>>"%FILE%"
ECHO %TEXT%>>"%FILE%"
ECHO 已添加 hiero 启动脚本： %FILE%
