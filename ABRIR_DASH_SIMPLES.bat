@echo off
title Dashboard KE5Z - Abertura Simples

echo.
echo ==========================================
echo    🚀 DASHBOARD KE5Z - ABERTURA SIMPLES
echo ==========================================
echo.

:: Verificar se existe Dash.py
if not exist "Dash.py" (
    echo ❌ ERRO: Arquivo Dash.py não encontrado!
    echo 💡 Execute este arquivo na pasta do projeto
    pause
    exit /b 1
)

echo ✅ Arquivo Dash.py encontrado

:: Verificar ambiente virtual
if exist "venv\Scripts\python.exe" (
    echo ✅ Usando ambiente virtual
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else (
    echo ⚠️  Ambiente virtual não encontrado, usando Python global
    set "PYTHON_CMD=python"
)

:: Verificar se Python funciona
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python não encontrado!
    echo 💡 Instale o Python ou execute abrir_dashboard.bat
    pause
    exit /b 1
)

echo ✅ Python disponível

:: Verificar Streamlit
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit não encontrado, instalando...
    %PYTHON_CMD% -m pip install streamlit pandas altair plotly openpyxl --quiet
    
    if %errorlevel% neq 0 (
        echo ❌ ERRO na instalação
        pause
        exit /b 1
    )
    echo ✅ Streamlit instalado
) else (
    echo ✅ Streamlit disponível
)

:: Informações de acesso
echo.
echo ==========================================
echo    🎯 INFORMAÇÕES DE ACESSO
echo ==========================================
echo.
echo URL: http://localhost:8501
echo Admin: admin / admin123
echo Demo: demo / demo123
echo.
echo Para parar: Pressione Ctrl+C
echo.

:: Abrir navegador
start "" "http://localhost:8501"

:: Executar dashboard
echo Iniciando Dashboard KE5Z...
echo.
%PYTHON_CMD% -m streamlit run Dash.py --server.port 8501

:: Mensagem final
echo.
echo 👋 Dashboard encerrado
pause
