#!/usr/bin/env python3
"""
Script para limpar completamente o ambiente e forçar o VS Code a usar Python do sistema
"""

import os
import sys
import json
import shutil
from pathlib import Path

def limpar_ambiente():
    """Limpa todas as configurações de ambiente virtual"""
    
    print("🧹 LIMPANDO AMBIENTE PYTHON...")
    print("=" * 50)
    
    # Limpar variáveis de ambiente
    vars_para_limpar = [
        'VIRTUAL_ENV', 'PYTHONHOME', 'CONDA_DEFAULT_ENV', 
        'PIPENV_ACTIVE', 'POETRY_ACTIVE', 'PYTHONPATH'
    ]
    
    for var in vars_para_limpar:
        if var in os.environ:
            del os.environ[var]
            print(f"✅ Removida variável: {var}")
    
    # Verificar Python atual
    print(f"\n🐍 PYTHON ATIVO:")
    print(f"   Versão: {sys.version}")
    print(f"   Executável: {sys.executable}")
    print(f"   Diretório: {os.getcwd()}")
    
    # Verificar se há ambientes virtuais
    pastas_venv = ['.venv', 'venv', 'venv_novo', 'env', '.env']
    for pasta in pastas_venv:
        if os.path.exists(pasta):
            print(f"⚠️  ENCONTRADO: {pasta}")
        else:
            print(f"✅ LIMPO: {pasta}")
    
    # Criar arquivo pyvenv.cfg se necessário
    pyvenv_path = Path("pyvenv.cfg")
    if not pyvenv_path.exists():
        python_exe = sys.executable
        python_home = str(Path(python_exe).parent)
        
        config_content = f"""home = {python_home}
executable = {python_exe}
command = {python_exe} -m venv {os.getcwd()}
include-system-site-packages = true
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
prompt = Dash
"""
        with open(pyvenv_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ Criado: {pyvenv_path}")
    
    print("\n🎯 TESTANDO IMPORTAÇÕES:")
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 LIMPEZA CONCLUÍDA!")
    print("💡 Agora execute: python Extração.py")
    print("=" * 50)

if __name__ == "__main__":
    limpar_ambiente()
