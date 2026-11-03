@echo off
title ZERO PARADES - Remover traducao PT-BR
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\remover.ps1" -Interativo
exit /b %ERRORLEVEL%
