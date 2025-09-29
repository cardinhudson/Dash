@echo off
chcp 65001 >nul
cls
echo ========================================
echo    CORRECAO DEFINITIVA DO AMBIENTE
echo ========================================
echo.

echo [PASSO 1] Removendo ambiente virtual corrompido...
if exist "venv" (
    echo Tentando remover pasta venv...
    
    REM Tentativa 1: Comando tradicional
    rmdir /s /q venv >nul 2>&1
    
    REM Tentativa 2: PowerShell
    if exist "venv" (
        echo Usando PowerShell para remocao forcada...
        powershell -Command "Get-ChildItem -Path 'venv' -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue" >nul 2>&1
        powershell -Command "Remove-Item -Path 'venv' -Force -ErrorAction SilentlyContinue" >nul 2>&1
    )
    
    REM Tentativa 3: Forcar remocao arquivo por arquivo
    if exist "venv" (
        echo Tentando remocao arquivo por arquivo...
        attrib -r -h -s venv\*.* /s /d >nul 2>&1
        del /f /s /q venv\*.* >nul 2>&1
        rmdir /s /q venv >nul 2>&1
    )
    
    REM Verificar se foi removido
    if exist "venv" (
        echo ERRO: Nao foi possivel remover o ambiente virtual
        echo Execute este arquivo como Administrador
        echo Ou remova a pasta 'venv' manualmente
        pause
        exit /b 1
    ) else (
        echo OK: Ambiente virtual removido com sucesso!
    )
) else (
    echo OK: Nenhum ambiente virtual encontrado
)

echo.
echo [PASSO 2] Verificando Python do sistema...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no sistema!
    echo Instale Python e adicione ao PATH
    pause
    exit /b 1
) else (
    echo OK: Python do sistema funcionando
    python --version
)

echo.
echo [PASSO 3] Testando execucao direta...
echo Testando: python Extração.py
echo.
python Extração.py
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Problema na execucao da Extração
) else (
    echo.
    echo OK: Extração executada com sucesso!
)

echo.
echo [PASSO 4] Testando dashboard...
echo Testando importacao do Dash.py...
python -c "import Dash; print('Dashboard OK!')" 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Problema no dashboard
) else (
    echo OK: Dashboard funcionando!
)

echo.
echo ========================================
echo        CORRECAO CONCLUIDA
echo ========================================
echo.
echo INSTRUCOES PARA USO:
echo.
echo 1. Para extrair dados:
echo    python Extração.py
echo.
echo 2. Para abrir dashboard:
echo    python -m streamlit run Dash.py
echo.
echo 3. Para uso automatico:
echo    Use abrir_dashboard_simples.bat
echo.
echo PROBLEMA RESOLVIDO: Ambiente virtual corrompido removido
echo SOLUCAO: Usando Python do sistema diretamente
echo.
pause
