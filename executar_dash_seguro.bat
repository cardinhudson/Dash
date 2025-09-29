@echo off
echo 🚀 EXECUTANDO DASHBOARD COM CONFIGURAÇÃO DE PROXY SEGURA
echo ============================================================

REM Configurar variáveis de ambiente para resolver problema de proxy
set PYTHONHTTPSVERIFY=0
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_VERIFY=False

echo ✅ Variáveis de ambiente configuradas para proxy Stellantis
echo.

REM Executar o dashboard
echo 🎯 Iniciando Dashboard KE5Z...
streamlit run Dash.py

pause




