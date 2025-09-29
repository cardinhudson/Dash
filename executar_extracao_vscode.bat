@echo off
chcp 65001 >nul
echo ===============================================
echo EXECUTANDO EXTRACAO COM PYTHON DO SISTEMA
echo ===============================================

REM Limpar variaveis de ambiente virtual
set VIRTUAL_ENV=
set PYTHONHOME=
set CONDA_DEFAULT_ENV=
set PYTHONPATH=

REM Definir Python especifico
set PYTHON_EXE=C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe

echo Python usando: %PYTHON_EXE%
echo.

REM Verificar se o Python existe
if not exist "%PYTHON_EXE%" (
    echo ERRO: Python nao encontrado em %PYTHON_EXE%
    pause
    exit /b 1
)

REM Executar a extracao com nome correto
echo Executando Extracao.py...
echo.
"%PYTHON_EXE%" "Extração.py"

REM Verificar se houve erro
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha na execucao da extracao
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ===============================================
echo EXTRACAO CONCLUIDA COM SUCESSO!
echo ===============================================
pause