@echo off
title Dashboard KE5Z - Execucao Rapida

echo.
echo ==========================================
echo    DASHBOARD KE5Z - EXECUCAO RAPIDA
echo ==========================================
echo.

:: Verificar se existe Dash.py
if not exist "Dash.py" (
    echo ERRO: Arquivo Dash.py nao encontrado!
    echo Execute este arquivo na pasta do projeto
    pause
    exit /b 1
)

:: Verificar ambiente virtual
if exist "venv\Scripts\python.exe" (
    echo Usando ambiente virtual
    echo Iniciando dashboard...
    echo.
    start "" "http://localhost:8501"
    venv\Scripts\python.exe -m streamlit run Dash.py --server.port 8501
) else (
    echo Usando Python global
    echo Iniciando dashboard...
    echo.
    start "" "http://localhost:8501"
    python -m streamlit run Dash.py --server.port 8501
)

echo.
echo Dashboard encerrado
pause
