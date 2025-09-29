@echo off
chcp 65001 >nul
cls
echo ========================================
echo    CORRIGIR AMBIENTE VIRTUAL
echo ========================================
echo.

echo Removendo ambiente virtual corrompido...
if exist "venv" (
    echo Tentativa 1: CMD
    rmdir /s /q venv >nul 2>&1
    
    if exist "venv" (
        echo Tentativa 2: PowerShell
        powershell -Command "Remove-Item -Recurse -Force 'venv' -ErrorAction SilentlyContinue" >nul 2>&1
    )
    
    if exist "venv" (
        echo Tentativa 3: Forçando remoção arquivo por arquivo
        del /f /s /q venv\*.* >nul 2>&1
        rmdir /s /q venv >nul 2>&1
    )
)

if exist "venv" (
    echo ⚠️ Não foi possível remover completamente
    echo Execute como Administrador ou remova manualmente
) else (
    echo ✅ Ambiente virtual removido
)

echo.
echo Testando Python do sistema...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado no sistema
    pause
    exit /b 1
)

echo ✅ Python do sistema funcionando
echo.

echo Testando execução da extração...
echo python Extração.py
python Extração.py
if %errorlevel% neq 0 (
    echo ⚠️ Erro na extração
) else (
    echo ✅ Extração funcionando
)

echo.
echo ========================================
echo        CORREÇÃO CONCLUÍDA
echo ========================================
echo.
echo Agora use:
echo   python Extração.py
echo   python -m streamlit run Dash.py
echo.
pause