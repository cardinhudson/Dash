#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para usar configurações do VS Code e aplicar configurações de rede
Integra com .vscode/settings.json para evitar problemas de VPN
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def ler_config_vscode():
    """Lê as configurações do VS Code"""
    vscode_settings = Path('.vscode/settings.json')
    
    if not vscode_settings.exists():
        print("❌ Arquivo .vscode/settings.json não encontrado!")
        return None
    
    try:
        with open(vscode_settings, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Configurações do VS Code carregadas com sucesso!")
        return config
    except Exception as e:
        print(f"❌ Erro ao ler configurações: {e}")
        return None

def aplicar_config_rede():
    """Aplica configurações de rede baseadas no VS Code"""
    print("\n🔧 Aplicando configurações de rede...")
    
    # Configurações de rede otimizadas
    comandos_rede = [
        "netsh winsock reset",
        "netsh int ip reset",
        "ipconfig /flushdns",
        "ipconfig /release",
        "ipconfig /renew"
    ]
    
    for comando in comandos_rede:
        try:
            print(f"   Executando: {comando}")
            subprocess.run(comando, shell=True, capture_output=True, text=True)
        except Exception as e:
            print(f"   ⚠️ Erro em {comando}: {e}")
    
    print("✅ Configurações de rede aplicadas!")

def testar_python():
    """Testa se o Python está funcionando corretamente"""
    print("\n🐍 Testando Python...")
    
    try:
        # Testa comando python
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Python funcionando: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"❌ Erro com 'python': {e}")
    
    try:
        # Testa comando py
        result = subprocess.run(['py', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Py funcionando: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"❌ Erro com 'py': {e}")
    
    print("❌ Nenhum comando Python funcionando!")
    return False

def executar_extracao():
    """Executa o script de extração"""
    print("\n📊 Executando Extração.py...")
    
    try:
        # Tenta com python primeiro
        result = subprocess.run(['python', 'Extração.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Extração.py executado com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro com 'python Extração.py': {e}")
    
    try:
        # Tenta com py
        result = subprocess.run(['py', 'Extração.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Extração.py executado com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro com 'py Extração.py': {e}")
    
    print("❌ Falha ao executar Extração.py!")
    return False

def main():
    """Função principal"""
    print("=" * 50)
    print("    USAR CONFIGURAÇÃO VS CODE")
    print("=" * 50)
    
    # 1. Ler configurações do VS Code
    config = ler_config_vscode()
    if not config:
        return
    
    # 2. Aplicar configurações de rede
    aplicar_config_rede()
    
    # 3. Testar Python
    if not testar_python():
        print("\n❌ Sistema não configurado corretamente!")
        return
    
    # 4. Executar extração
    if executar_extracao():
        print("\n🎉 SISTEMA CONFIGURADO E FUNCIONANDO!")
    else:
        print("\n⚠️ Sistema configurado, mas extração falhou!")

if __name__ == "__main__":
    main()