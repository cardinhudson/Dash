#!/usr/bin/env python3
"""
Wrapper para executar Extração.py com Python específico
"""

import os
import sys
import subprocess
from pathlib import Path

def executar_extracao():
    """Executa Extração.py com Python do sistema"""
    
    print("🚀 EXECUTANDO EXTRAÇÃO COM PYTHON DO SISTEMA")
    print("=" * 60)
    
    # Limpar variáveis de ambiente virtual
    vars_para_limpar = [
        'VIRTUAL_ENV', 'PYTHONHOME', 'CONDA_DEFAULT_ENV', 
        'PIPENV_ACTIVE', 'POETRY_ACTIVE', 'PYTHONPATH',
        'PYENV_VERSION', 'CONDA_PYTHON_EXE', 'CONDA_EXE'
    ]
    
    for var in vars_para_limpar:
        if var in os.environ:
            del os.environ[var]
            print(f"✅ Removida variável: {var}")
    
    # Python específico
    python_exe = r"C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe"
    extracao_file = Path("Extração.py")
    
    print(f"\n🐍 PYTHON: {python_exe}")
    print(f"📄 ARQUIVO: {extracao_file}")
    print(f"📁 DIRETÓRIO: {os.getcwd()}")
    
    # Verificar se os arquivos existem
    if not Path(python_exe).exists():
        print(f"❌ ERRO: Python não encontrado em {python_exe}")
        return False
        
    if not extracao_file.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {extracao_file}")
        return False
    
    # Executar a extração
    print(f"\n🔄 EXECUTANDO...")
    print("-" * 60)
    
    try:
        # Usar subprocess para executar com Python específico
        result = subprocess.run([
            python_exe, 
            str(extracao_file)
        ], cwd=os.getcwd(), check=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        else:
            print(f"\n❌ ERRO: Código de saída {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ ERRO NA EXECUÇÃO: {e}")
        return False

if __name__ == "__main__":
    sucesso = executar_extracao()
    if not sucesso:
        print("\n⚠️  EXECUÇÃO FALHOU!")
        sys.exit(1)
