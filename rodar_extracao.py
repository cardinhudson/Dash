#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar Extração.py de forma robusta
Resolve o problema "No pyvenv.cfg file"
"""

import subprocess
import sys
import os
from datetime import datetime

def main():
    print("🚀 Executando Extração KE5Z...")
    print(f"⏰ Início: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Caminho do Python que funciona
    python_path = r"C:\Users\u235107\AppData\Local\Programs\Python\Python311\python.exe"
    
    # Verificar se existe
    if not os.path.exists(python_path):
        print("❌ Python não encontrado no caminho esperado!")
        print("Tentando com python padrão...")
        python_path = "python"
    
    # Verificar se Extração.py existe
    if not os.path.exists("Extração.py"):
        print("❌ Arquivo Extração.py não encontrado!")
        return False
    
    try:
        print("🔄 Executando extração...")
        # Executar sem capturar output para ver logs em tempo real
        resultado = subprocess.run([python_path, "Extração.py"])
        
        if resultado.returncode == 0:
            print("=" * 50)
            print("✅ Extração concluída com sucesso!")
            print(f"⏰ Fim: {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Erro: Falha com código {resultado.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    if not sucesso:
        input("\nPressione Enter para sair...")
    else:
        print("\n🎉 Processo finalizado!")
