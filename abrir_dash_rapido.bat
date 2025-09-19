@echo off
chcp 65001 >nul
title Dashboard KE5Z - Abertura Rapida

echo.
echo ==========================================
echo    DASHBOARD KE5Z - ABERTURA RAPIDA
echo ==========================================
echo.

:: Verificar se estamos na pasta correta
if not exist "Dash.py" (
    echo ERRO: Arquivo Dash.py nao encontrado!
    echo.
    echo SOLUCAO:
    echo    1. Navegue ate a pasta do projeto
    echo    2. Execute este arquivo na pasta correta
    echo.
    pause
    exit /b 1
)

:: Verificar se o ambiente virtual existe
if exist "venv\Scripts\python.exe" (
    echo Ambiente virtual encontrado
    set "PYTHON_PATH=venv\Scripts\python.exe"
    set "PIP_PATH=venv\Scripts\pip.exe"
) else (
    echo Ambiente virtual nao encontrado, usando Python global
    set "PYTHON_PATH=python"
    set "PIP_PATH=pip"
)

:: Verificar Python
%PYTHON_PATH% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo Python: OK

:: Verificar dependencias basicas
echo Verificando dependencias...

%PYTHON_PATH% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Streamlit...
    %PIP_PATH% install streamlit --quiet
)

%PYTHON_PATH% -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Pandas...
    %PIP_PATH% install pandas --quiet
)

echo Dependencias: OK

:: Verificar dados
if exist "KE5Z\KE5Z.parquet" (
    echo Dados: OK
) else (
    echo Dados: Nao encontrados (usara dados de exemplo)
)

:: Encontrar porta livre
set "PORTA=8501"
netstat -an | find ":8501 " >nul
if %errorlevel% equ 0 (
    set "PORTA=8502"
)

echo Porta: %PORTA%
echo.

:: Mostrar informacoes de acesso
echo ==========================================
echo    INFORMACOES DE ACESSO
echo ==========================================
echo.
echo URL: http://localhost:%PORTA%
echo.
echo Usuarios:
echo    admin / admin123 (Administrador)
echo    demo / demo123 (Usuario)
echo.
echo Para parar: Pressione Ctrl+C
echo.

:: Abrir navegador
start "" "http://localhost:%PORTA%"

:: Iniciar dashboard
echo Iniciando Dashboard KE5Z...
echo.

%PYTHON_PATH% -m streamlit run Dash.py --server.port %PORTA%

:: Mensagem final
echo.
echo Dashboard encerrado
pause