#!/usr/bin/env python3
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
