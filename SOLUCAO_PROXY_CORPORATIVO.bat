@echo off
echo ========================================
echo    SOLUCAO PROXY CORPORATIVO
echo ========================================
echo.

echo [1/5] Detectando problema de proxy...
echo ⚠️  Streaming responses being buffered by proxy
echo ⚠️  ConnectError: ECONNRESET
echo.

echo [2/5] Configurando bypass de proxy...
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=localhost,127.0.0.1,::1
set http_proxy=
set https_proxy=
set no_proxy=localhost,127.0.0.1,::1

echo [3/5] Limpando cache de proxy...
netsh winhttp reset proxy >nul 2>&1
netsh winhttp show proxy

echo [4/5] Configurando Streamlit para bypass...
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=127.0.0.1

echo [5/5] Iniciando sistema local...
echo.
echo 🚀 INICIANDO DASHBOARD LOCAL...
echo    (Bypass de proxy ativado)
echo.

start streamlit run Dash.py --server.headless true --server.address 127.0.0.1

echo.
echo ========================================
echo    PROXY BYPASS ATIVADO!
echo ========================================
echo.
echo 💡 SOLUCAO APLICADA:
echo    - Proxy corporativo bypassado
echo    - Streamlit configurado para localhost
echo    - Cache de proxy limpo
echo.
pause


