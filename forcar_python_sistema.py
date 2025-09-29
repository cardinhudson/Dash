#!/usr/bin/env python3
"""
Script para forçar VS Code a usar Python do sistema
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def forcar_python_sistema():
    """Força VS Code a usar Python do sistema"""
    
    print("🔧 FORÇANDO VS CODE A USAR PYTHON DO SISTEMA")
    print("=" * 60)
    
    # Encontrar Python do sistema
    python_exe = sys.executable
    print(f"🐍 Python encontrado: {python_exe}")
    
    # Criar configuração workspace específica
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # Settings.json com configuração forçada
    settings = {
        "python.defaultInterpreterPath": python_exe.replace("\\", "/"),
        "python.pythonPath": python_exe.replace("\\", "/"),
        "python.terminal.activateEnvironment": False,
        "python.terminal.activateEnvInCurrentTerminal": False,
        "python.envFile": "",
        "python.venvPath": "",
        "python.condaPath": "",
        "python.pipenvPath": "",
        "python.poetryPath": "",
        "terminal.integrated.env.windows": {
            "PYTHONPATH": "",
            "VIRTUAL_ENV": "",
            "PYTHONHOME": "",
            "CONDA_DEFAULT_ENV": ""
        },
        "files.exclude": {
            "**/.venv": True,
            "**/venv": True,
            "**/env": True
        }
    }
    
    settings_file = vscode_dir / "settings.json"
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
    print(f"✅ Criado: {settings_file}")
    
    # Launch.json com configuração específica
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Extração - Python Sistema FORÇADO",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/Extração.py",
                "console": "integratedTerminal",
                "python": python_exe.replace("\\", "/"),
                "cwd": "${workspaceFolder}",
                "env": {
                    "PYTHONPATH": "",
                    "VIRTUAL_ENV": "",
                    "PYTHONHOME": "",
                    "CONDA_DEFAULT_ENV": ""
                }
            }
        ]
    }
    
    launch_file = vscode_dir / "launch.json"
    with open(launch_file, 'w', encoding='utf-8') as f:
        json.dump(launch_config, f, indent=4)
    print(f"✅ Criado: {launch_file}")
    
    # Tentar executar comando VS Code para resetar
    try:
        print("\n🔄 Tentando resetar cache do VS Code...")
        subprocess.run([
            "code", 
            "--command", 
            "python.clearCache"
        ], cwd=os.getcwd(), timeout=10)
        print("✅ Cache limpo")
    except Exception as e:
        print(f"⚠️  Não foi possível limpar cache automaticamente: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO FORÇADA APLICADA!")
    print("\nPRÓXIMOS PASSOS:")
    print("1. Feche COMPLETAMENTE o VS Code")
    print("2. Reabra o VS Code")
    print("3. F5 → 'Extração - Python Sistema FORÇADO'")
    print("4. OU use terminal: python Extração.py")
    print("=" * 60)

if __name__ == "__main__":
    forcar_python_sistema()
