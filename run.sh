#!/usr/bin/env bash
# ==============================================================================
# Cyber Protein Tracker - Script de ejecución para Linux / macOS
# ==============================================================================

set -e

# Detectar ruta del script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=== Cyber Protein Tracker (Linux) ==="
echo "Ejecutando pipeline de extracción y análisis inteligente..."

if command -v python3 &>/dev/null; then
    python3 main.py "$@"
elif command -v python &>/dev/null; then
    python main.py "$@"
else
    echo "Error: Python no está instalado en este sistema."
    exit 1
fi
