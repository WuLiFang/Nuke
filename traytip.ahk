#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#SingleInstance force
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

_title := " "
_text := " "
_seconds := 3
_options := 1
Loop, %0%
{
    if (A_Index == 1)
        _title := %A_Index%
    if (A_Index == 2)
        _text := %A_Index%
    if (A_Index == 3)
        _seconds := %A_Index%
    if (A_Index == 4)
        _options := %A_Index%
}
TrayTip, %_title%, %_text%, %_seconds%, %_options%
Sleep, % _seconds * 1000 + 8000