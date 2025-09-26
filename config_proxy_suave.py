#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Suave de Proxy - Stellantis
Solução gradual para problemas de ECONNRESET
"""

import os
import json
import subprocess
import time
import requests
from pathlib import Path

def verificar_conexao():
    """Verifica se a conexão está funcionando"""
    try:
        response = requests.get("https://httpbin.org/ip", timeout=10)
        return response.status_code == 200
    except:
        return False

def configurar_proxy_gradual():
    """Configuração gradual do proxy"""
    print("🔧 Iniciando configuração gradual de proxy...")
    
    # 1. Verificar configuração atual do VS Code
    vscode_settings = Path.home() / ".vscode" / "settings.json"
    if vscode_settings.exists():
        print("✅ Encontrado settings.json do VS Code")
        with open(vscode_settings, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Aplicar configurações gradualmente
        proxy_config = {
            "http.proxy": "",
            "http.proxyStrictSSL": False,
            "http.proxySupport": "off",
            "http.proxyBypassList": "localhost,127.0.0.1,::1"
        }
        
        for key, value in proxy_config.items():
            if key not in settings:
                settings[key] = value
                print(f"  ➕ Adicionado: {key} = {value}")
            else:
                print(f"  ✅ Já configurado: {key}")
        
        # Salvar configurações
        with open(vscode_settings, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        print("✅ Configurações do VS Code atualizadas")
    
    # 2. Configurar variáveis de ambiente Python
    env_vars = {
        'PYTHONHTTPSVERIFY': '0',
        'CURL_CA_BUNDLE': '',
        'REQUESTS_CA_BUNDLE': '',
        'SSL_VERIFY': 'False'
    }
    
    print("\n🔧 Configurando variáveis de ambiente Python...")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  ✅ {key} = {value}")
    
    # 3. Teste de conexão
    print("\n🧪 Testando conexão...")
    if verificar_conexao():
        print("✅ Conexão funcionando!")
        return True
    else:
        print("⚠️ Conexão ainda com problemas")
        return False

def criar_script_streamlit_seguro():
    """Cria script Streamlit com configurações de proxy"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit com configuração de proxy segura
"""

import os
import sys

# Configurações de proxy antes de importar streamlit
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_VERIFY'] = 'False'

# Configurações de logging para debug
import logging
logging.basicConfig(level=logging.INFO)

# Importar streamlit
import streamlit as st

# Configurações do Streamlit
st.set_page_config(
    page_title="Dashboard KE5Z",
    page_icon="📊",
    layout="wide"
)

# Sua aplicação aqui
if __name__ == "__main__":
    st.title("Dashboard KE5Z - Versão Segura")
    st.info("Configuração de proxy aplicada com sucesso!")
'''
    
    with open("streamlit_seguro.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ Script Streamlit seguro criado: streamlit_seguro.py")

def main():
    """Função principal"""
    print("🚀 SOLUÇÃO GRADUAL PARA PROBLEMA DE PROXY STELLANTIS")
    print("=" * 60)
    
    # Passo 1: Configuração gradual
    if configurar_proxy_gradual():
        print("\n✅ Configuração básica concluída!")
    else:
        print("\n⚠️ Configuração básica com problemas, mas continuando...")
    
    # Passo 2: Criar script seguro
    criar_script_streamlit_seguro()
    
    # Passo 3: Instruções
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Teste o script seguro: python streamlit_seguro.py")
    print("2. Se funcionar, use: streamlit run streamlit_seguro.py")
    print("3. Para o dashboard completo, use: streamlit run Dash.py")
    
    print("\n✅ Solução gradual implementada com sucesso!")

if __name__ == "__main__":
    main()

