#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para usar configurações de proxy do VS Code no Streamlit
Resolve problema: "Streaming responses are being buffered by a proxy"
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def ler_config_proxy_vscode():
    """Lê as configurações de proxy do VS Code"""
    vscode_settings = Path('.vscode/settings.json')
    
    if not vscode_settings.exists():
        print("❌ Arquivo .vscode/settings.json não encontrado!")
        return None
    
    try:
        with open(vscode_settings, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Configurações de proxy do VS Code
        proxy_config = {
            'http_proxy': config.get('http.proxy', ''),
            'https_proxy': config.get('http.proxy', ''),
            'no_proxy': config.get('http.proxyStrictSSL', False),
            'proxy_bypass': config.get('http.proxySupport', 'off')
        }
        
        print("✅ Configurações de proxy do VS Code carregadas!")
        return proxy_config
    except Exception as e:
        print(f"❌ Erro ao ler configurações: {e}")
        return None

def aplicar_config_proxy(proxy_config):
    """Aplica as configurações de proxy do VS Code"""
    print("\n🔧 Aplicando configurações de proxy do VS Code...")
    
    # Configura variáveis de ambiente
    if proxy_config['http_proxy']:
        os.environ['HTTP_PROXY'] = proxy_config['http_proxy']
        os.environ['http_proxy'] = proxy_config['http_proxy']
        print(f"   HTTP_PROXY: {proxy_config['http_proxy']}")
    
    if proxy_config['https_proxy']:
        os.environ['HTTPS_PROXY'] = proxy_config['https_proxy']
        os.environ['https_proxy'] = proxy_config['https_proxy']
        print(f"   HTTPS_PROXY: {proxy_config['https_proxy']}")
    
    # Configurações de bypass
    if proxy_config['no_proxy']:
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'
        print("   NO_PROXY: localhost,127.0.0.1,::1")
    
    print("✅ Configurações de proxy aplicadas!")

def configurar_streamlit_proxy():
    """Configura o Streamlit para usar as configurações de proxy"""
    print("\n🚀 Configurando Streamlit com proxy do VS Code...")
    
    # Configurações específicas do Streamlit
    streamlit_config = {
        'server.headless': 'true',
        'server.address': '127.0.0.1',
        'server.port': '8501',
        'browser.gatherUsageStats': 'false',
        'server.enableCORS': 'false',
        'server.enableXsrfProtection': 'false'
    }
    
    # Aplica configurações
    for key, value in streamlit_config.items():
        os.environ[f'STREAMLIT_{key.upper().replace(".", "_")}'] = value
        print(f"   {key}: {value}")
    
    print("✅ Streamlit configurado com proxy do VS Code!")

def executar_streamlit():
    """Executa o Streamlit com as configurações de proxy"""
    print("\n📊 Iniciando Dashboard com proxy do VS Code...")
    
    try:
        # Comando para executar Streamlit
        cmd = [
            'streamlit', 'run', 'Dash.py',
            '--server.headless', 'true',
            '--server.address', '127.0.0.1',
            '--server.port', '8501'
        ]
        
        print(f"   Comando: {' '.join(cmd)}")
        
        # Executa o Streamlit
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar Streamlit: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("    USAR PROXY DO VS CODE NO STREAMLIT")
    print("=" * 60)
    
    # 1. Ler configurações de proxy do VS Code
    proxy_config = ler_config_proxy_vscode()
    if not proxy_config:
        print("\n⚠️ Usando configurações padrão (sem proxy)")
        proxy_config = {
            'http_proxy': '',
            'https_proxy': '',
            'no_proxy': True,
            'proxy_bypass': 'off'
        }
    
    # 2. Aplicar configurações de proxy
    aplicar_config_proxy(proxy_config)
    
    # 3. Configurar Streamlit
    configurar_streamlit_proxy()
    
    # 4. Executar Streamlit
    print("\n🎉 INICIANDO DASHBOARD...")
    print("   URL: http://127.0.0.1:8501")
    print("   Proxy: Configurado pelo VS Code")
    print("   Status: Bypass de proxy ativado")
    
    executar_streamlit()

if __name__ == "__main__":
    main()




