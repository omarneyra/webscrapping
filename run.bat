@echo off
REM ==============================================================================
REM Cyber Protein Tracker - Script de ejecucion para Windows
REM ==============================================================================

cd /d "%~dp0"
echo === Cyber Protein Tracker (Windows) ===
echo Ejecutando pipeline de extraccion y analisis inteligente...

python main.py %*
if %ERRORLEVEL% NEQ 0 (
    echo Error al ejecutar el script en Python.
    pause
    exit /b %ERRORLEVEL%
)
