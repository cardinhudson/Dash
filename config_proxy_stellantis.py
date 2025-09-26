#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração de Proxy para Stellantis
Importe este arquivo no início de qualquer script para resolver ECONNRESET
"""

import os

def configurar_proxy_stellantis():
    """Configura variáveis de ambiente para resolver problema de proxy da Stellantis"""
    
    # Variáveis de ambiente para resolver SSL/proxy
    proxy_config = {
        'PYTHONHTTPSVERIFY': '0',
        'CURL_CA_BUNDLE': '',
        'REQUESTS_CA_BUNDLE': '',
        'SSL_VERIFY': 'False',
        'PYTHONIOENCODING': 'utf-8'
    }
    
    # Aplicar configurações
    for key, value in proxy_config.items():
        os.environ[key] = value
    
    return True

# Configurar automaticamente quando importado
configurar_proxy_stellantis()


