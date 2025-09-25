@echo off
chcp 65001 >nul
cls
echo ========================================
echo    DASHBOARD KE5Z - INICIO RAPIDO
echo ========================================
echo.

REM Verificar se Python existe
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python e adicione ao PATH
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version
echo.

REM Verificar arquivos essenciais
if not exist "Dash.py" (
    echo ERRO: Dash.py nao encontrado!
    pause
    exit /b 1
)

if not exist "auth_simple.py" (
    echo ERRO: auth_simple.py nao encontrado!
    pause
    exit /b 1
)

echo ✅ Arquivos verificados
echo.

REM Verificar dependências básicas
echo Verificando dependências...
python -c "import streamlit, pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Instalando dependências...
    pip install streamlit pandas altair plotly openpyxl pyarrow --quiet
)

echo ✅ Dependências verificadas
echo.

REM ============================================
REM CONFIGURACAO DE PROXY PARA STELLANTIS
REM ============================================
echo 🔧 Configurando proxy para ambiente Stellantis...
set PYTHONHTTPSVERIFY=0
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_VERIFY=False
set PYTHONIOENCODING=utf-8
echo ✅ Configuração de proxy aplicada!
echo.

echo ========================================
echo         INICIANDO DASHBOARD
echo ========================================
echo.

REM Usar porta alternativa para evitar conflitos
set "PORTA=8555"
echo Usando porta %PORTA% para evitar conflitos...

echo.
echo 🌐 URL: http://localhost:%PORTA%
echo 🔐 Login: admin / admin123
echo 👑 Admin: http://localhost:8650
echo.
echo Para parar: Pressione Ctrl+C
echo.

REM Abrir navegador
start http://localhost:%PORTA% >nul 2>&1

REM Iniciar dashboard
echo Iniciando servidor na porta %PORTA%...
streamlit run Dash.py --server.port %PORTA%

echo.
echo Dashboard encerrado.
pause
