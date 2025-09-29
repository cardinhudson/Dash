@echo off
chcp 65001 >nul
cls
echo ========================================
echo    REINSTALACAO COMPLETA DO AMBIENTE
echo ========================================
echo.

echo [PASSO 1] Finalizando processos Python...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

echo [PASSO 2] Removendo ambiente virtual antigo...
if exist "venv" (
    echo Removendo venv...
    attrib -r -h -s venv\*.* /s /d >nul 2>&1
    del /f /s /q venv\*.* >nul 2>&1
    rmdir /s /q venv >nul 2>&1
    
    if exist "venv" (
        echo Usando PowerShell para remocao forcada...
        powershell -Command "Remove-Item -Recurse -Force 'venv' -ErrorAction SilentlyContinue" >nul 2>&1
    )
    
    timeout /t 2 >nul
    
    if exist "venv" (
        echo AVISO: Nao foi possivel remover completamente
    ) else (
        echo OK: Ambiente virtual removido
    )
) else (
    echo OK: Nenhum ambiente virtual encontrado
)

echo.
echo [PASSO 3] Criando novo ambiente virtual...
python -m venv venv_novo --clear
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel criar ambiente virtual
    echo Continuando com Python do sistema...
    goto :usar_sistema
)

echo OK: Novo ambiente virtual criado
echo.

echo [PASSO 4] Movendo novo ambiente...
if exist "venv_novo" (
    if exist "venv" (
        rmdir /s /q venv >nul 2>&1
    )
    move venv_novo venv >nul 2>&1
    echo OK: Ambiente virtual configurado
)

echo.
echo [PASSO 5] Ativando ambiente virtual...
if exist "venv\Scripts\python.exe" (
    echo OK: Python do ambiente virtual disponivel
    set "PYTHON_CMD=venv\Scripts\python.exe"
) else (
    echo AVISO: Usando Python do sistema
    set "PYTHON_CMD=python"
)

echo.
echo [PASSO 6] Instalando dependencias...
%PYTHON_CMD% -m pip install --upgrade pip >nul 2>&1
%PYTHON_CMD% -m pip install streamlit pandas altair openpyxl pyarrow --quiet
if %errorlevel% neq 0 (
    echo ERRO: Falha na instalacao
) else (
    echo OK: Dependencias instaladas
)

goto :teste

:usar_sistema
set "PYTHON_CMD=python"
echo Usando Python do sistema...

:teste
echo.
echo [PASSO 7] Testando instalacao...
echo Testando Python...
%PYTHON_CMD% --version

echo Testando Streamlit...
%PYTHON_CMD% -c "import streamlit; print('Streamlit OK')" 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Streamlit nao funcionando
) else (
    echo OK: Streamlit funcionando
)

echo.
echo [PASSO 8] Testando extracao...
echo Executando: %PYTHON_CMD% Extração.py
%PYTHON_CMD% Extração.py
if %errorlevel% neq 0 (
    echo ERRO: Problema na extracao
) else (
    echo OK: Extracao funcionando
)

echo.
echo ========================================
echo        REINSTALACAO CONCLUIDA
echo ========================================
echo.
echo Para usar:
echo   Extracao: %PYTHON_CMD% Extração.py
echo   Dashboard: %PYTHON_CMD% -m streamlit run Dash.py
echo.
pause
