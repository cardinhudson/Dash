@echo off
chcp 65001 >nul
cls
echo ========================================
echo   CONFIGURAR VS CODE - PYTHON SISTEMA
echo ========================================
echo.

echo [PASSO 1] Removendo todos os ambientes virtuais...
if exist "venv" (
    echo Removendo venv...
    rmdir /s /q venv >nul 2>&1
)
if exist "venv_novo" (
    echo Removendo venv_novo...
    rmdir /s /q venv_novo >nul 2>&1
)

echo [PASSO 2] Verificando Python do sistema...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo [PASSO 3] Localizando Python do sistema...
where python

echo.
echo ========================================
echo        CONFIGURACAO VS CODE
echo ========================================
echo.
echo INSTRUCOES PARA CONFIGURAR VS CODE:
echo.
echo 1. Abra o VS Code
echo 2. Pressione Ctrl+Shift+P
echo 3. Digite: Python: Select Interpreter
echo 4. Escolha: Python 3.13.7 (global)
echo 5. NAO escolha opcoes com 'venv'
echo.
echo OU crie arquivo .vscode/settings.json com:
echo {
echo   "python.defaultInterpreterPath": "python"
echo }
echo.

echo [PASSO 4] Testando execucao direta...
echo Testando: python Extração.py
python Extração.py
if %errorlevel% neq 0 (
    echo ERRO: Problema na execucao
) else (
    echo OK: Execucao funcionando!
)

echo.
echo ========================================
echo          CONFIGURACAO CONCLUIDA
echo ========================================
echo.
echo Para usar no VS Code:
echo 1. Configure o interpretador Python correto
echo 2. Execute: python Extração.py
echo 3. Execute: python -m streamlit run Dash.py
echo.
pause


