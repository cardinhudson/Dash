@echo off
title Dashboard KE5Z - Execução Rápida

:: Verificar se existe ambiente virtual
if exist "venv\Scripts\python.exe" (
    echo Usando ambiente virtual
    venv\Scripts\python.exe -m streamlit run Dash.py --server.port 8501
) else (
    echo Usando Python global
    python -m streamlit run Dash.py --server.port 8501
)

pause
