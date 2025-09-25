@echo off
echo ========================================
echo    USAR PROXY DO VS CODE
echo ========================================
echo.

echo [1/3] Lendo configuracoes de proxy do VS Code...
python usar_proxy_vscode.py

echo.
echo [2/3] Configurando bypass de proxy...
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=localhost,127.0.0.1,::1
set http_proxy=
set https_proxy=
set no_proxy=localhost,127.0.0.1,::1

echo [3/3] Iniciando Dashboard com proxy do VS Code...
echo.
echo 🚀 DASHBOARD INICIANDO...
echo    URL: http://127.0.0.1:8501
echo    Proxy: Configurado pelo VS Code
echo    Status: Bypass de proxy ativado
echo.

start streamlit run Dash.py --server.headless true --server.address 127.0.0.1

echo.
echo ========================================
echo    PROXY VS CODE ATIVADO!
echo ========================================
echo.
echo 💡 SOLUCAO APLICADA:
echo    - Proxy do VS Code configurado
echo    - Bypass para localhost ativado
echo    - Streamlit configurado para local
echo.
pause


