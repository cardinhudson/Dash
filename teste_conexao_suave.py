#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Conexão Suave - Stellantis
Testa conexão sem interferir no sistema
"""

import os
import time
import requests
import subprocess

def testar_conexao_basica():
    """Teste básico de conexão"""
    print("🧪 Testando conexão básica...")
    
    try:
        # Configurar SSL
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        # Teste simples
        response = requests.get("https://httpbin.org/ip", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ IP: {response.json().get('origin', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_streamlit_local():
    """Teste local do Streamlit"""
    print("\n🧪 Testando Streamlit local...")
    
    try:
        # Verificar se streamlit está instalado
        result = subprocess.run(['streamlit', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Streamlit: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Streamlit não encontrado: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Streamlit: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 TESTE DE CONEXÃO SUAVE - STELLANTIS")
    print("=" * 50)
    
    # Teste 1: Conexão básica
    conexao_ok = testar_conexao_basica()
    
    # Teste 2: Streamlit
    streamlit_ok = testar_streamlit_local()
    
    # Resultado
    print("\n📊 RESULTADOS:")
    print(f"  Conexão: {'✅ OK' if conexao_ok else '❌ FALHA'}")
    print(f"  Streamlit: {'✅ OK' if streamlit_ok else '❌ FALHA'}")
    
    if conexao_ok and streamlit_ok:
        print("\n🎉 Sistema funcionando! Pode usar o dashboard normalmente.")
    else:
        print("\n⚠️ Alguns problemas detectados, mas sistema pode funcionar.")
    
    print("\n💡 DICA: Use 'python config_proxy_suave.py' para configuração gradual")

if __name__ == "__main__":
    main()

