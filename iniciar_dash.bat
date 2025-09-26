@echo off
echo 🚀 INICIANDO DASHBOARD KE5Z - VERSÃO SEGURA
echo ============================================

REM Configurar variáveis de ambiente para resolver problema de proxy
set PYTHONHTTPSVERIFY=0
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_VERIFY=False
set PYTHONIOENCODING=utf-8

echo ✅ Configuração de proxy aplicada para ambiente Stellantis
echo.

REM Executar o dashboard
echo 🎯 Iniciando Dashboard KE5Z...
streamlit run Dash.py

pause


