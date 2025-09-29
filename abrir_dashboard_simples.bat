@echo off
chcp 65001 >nul
cls
echo ========================================
echo    DASHBOARD KE5Z - INICIO RAPIDO
echo ========================================
echo.

REM ============================================
REM SOLUCAO DEFINITIVA PARA PROBLEMA PYVENV.CFG
REM ============================================
echo 🔧 Aplicando solucao para problemas de ambiente virtual...

REM Limpar variaveis de ambiente virtual que causam problemas
set VIRTUAL_ENV=
set PYTHONHOME=
set CONDA_DEFAULT_ENV=
set PIPENV_ACTIVE=
set POETRY_ACTIVE=
set PYTHONPATH=
set PYENV_VERSION=
set CONDA_PYTHON_EXE=
set CONDA_EXE=

REM Garantir que arquivo pyvenv.cfg existe se necessario
if not exist "pyvenv.cfg" (
    echo Criando arquivo pyvenv.cfg para compatibilidade...
    echo home = C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313 > pyvenv.cfg
    echo executable = C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe >> pyvenv.cfg
    echo command = python -m venv %~dp0 >> pyvenv.cfg
    echo include-system-site-packages = true >> pyvenv.cfg
    echo version = 3.13.7 >> pyvenv.cfg
    echo prompt = Dash >> pyvenv.cfg
    echo ✅ Arquivo pyvenv.cfg criado
)

echo ✅ Solucao de ambiente aplicada
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
    
    REM Configurar proxy para instalação
    set PYTHONHTTPSVERIFY=0
    set CURL_CA_BUNDLE=
    set REQUESTS_CA_BUNDLE=
    set SSL_VERIFY=False
    set HTTP_PROXY=
    set HTTPS_PROXY=
    set NO_PROXY=localhost,127.0.0.1
    
    echo Instalando pacotes essenciais...
    pip install streamlit pandas altair openpyxl pyarrow --quiet --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    echo Plotly removido devido a problemas de compatibilidade
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
