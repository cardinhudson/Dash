#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executar Dashboard com Configuração de Proxy Segura
Solução para problema ECONNRESET da Stellantis
"""

import os
import subprocess
import sys

def configurar_proxy():
    """Configura variáveis de ambiente para resolver problema de proxy"""
    print("🔧 Configurando proxy para ambiente Stellantis...")
    
    # Variáveis de ambiente para resolver SSL/proxy
    proxy_vars = {
        'PYTHONHTTPSVERIFY': '0',
        'CURL_CA_BUNDLE': '',
        'REQUESTS_CA_BUNDLE': '',
        'SSL_VERIFY': 'False',
        'PYTHONIOENCODING': 'utf-8'
    }
    
    for key, value in proxy_vars.items():
        os.environ[key] = value
        print(f"  ✅ {key} = {value}")
    
    print("✅ Configuração de proxy aplicada!")

def executar_dashboard():
    """Executa o dashboard com configurações de proxy"""
    print("\n🚀 Iniciando Dashboard KE5Z...")
    print("=" * 50)
    
    try:
        # Executar streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "Dash.py"]
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Dashboard interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar dashboard: {e}")
        print("\n💡 Tente executar manualmente: streamlit run Dash.py")

def main():
    """Função principal"""
    print("🎯 DASHBOARD KE5Z - VERSÃO SEGURA PARA PROXY")
    print("=" * 60)
    
    # Configurar proxy
    configurar_proxy()
    
    # Executar dashboard
    executar_dashboard()

if __name__ == "__main__":
    main()


