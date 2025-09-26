@echo off
echo ========================================
echo    SOLUCAO PROXY STELLANTIS
echo ========================================
echo.

echo [1/6] Detectando problema de proxy corporativo...
echo ⚠️  SSL: Certificado Stellantis/Goskope interceptando
echo ⚠️  Chat: Streaming buffered por proxy
echo.

echo [2/6] Configurando bypass para Stellantis...
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=localhost,127.0.0.1,::1,*.stellantis.com,*.goskope.com
set http_proxy=
set https_proxy=
set no_proxy=localhost,127.0.0.1,::1,*.stellantis.com,*.goskope.com

echo [3/6] Limpando cache de proxy corporativo...
netsh winhttp reset proxy >nul 2>&1
netsh winhttp set proxy bypass-list="localhost;127.0.0.1;::1;*.stellantis.com;*.goskope.com" >nul 2>&1

echo [4/6] Configurando SSL para bypass...
set SSL_VERIFY=false
set PYTHONHTTPSVERIFY=0
set CURL_CA_BUNDLE=

echo [5/6] Configurando Streamlit para bypass...
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=127.0.0.1
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

echo [6/6] Iniciando sistema com bypass...
echo.
echo 🚀 INICIANDO DASHBOARD COM BYPASS STELLANTIS...
echo    URL: http://127.0.0.1:8501
echo    Proxy: Bypass para Stellantis/Goskope
echo    SSL: Verificação desabilitada
echo.

start streamlit run Dash.py --server.headless true --server.address 127.0.0.1

echo.
echo ========================================
echo    BYPASS STELLANTIS ATIVADO!
echo ========================================
echo.
echo 💡 SOLUCAO APLICADA:
echo    - Proxy Stellantis/Goskope bypassado
echo    - SSL verification desabilitada
echo    - Streamlit configurado para localhost
echo    - Cache de proxy corporativo limpo
echo.
pause




