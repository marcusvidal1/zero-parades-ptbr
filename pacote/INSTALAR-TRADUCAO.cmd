@echo off
title ZERO PARADES - Instalar traducao PT-BR
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\instalar.ps1" -Interativo
exit /b %ERRORLEVEL%
