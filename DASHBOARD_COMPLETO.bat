@echo off
echo ========================================
echo    DASHBOARD KE5Z - SISTEMA COMPLETO
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado! Execute a instalacao primeiro.
    pause
    exit /b 1
)
echo ✅ Python OK!

echo [2/6] Backup automatico...
call backup_automatico.bat

echo [3/6] Configuracao de rede...
call usar_vscode_config.bat

echo [4/6] Testando Extração.py...
python Extração.py
if %errorlevel% neq 0 (
    echo ⚠️ Extração.py falhou, mas continuando...
)

echo [5/6] Verificando Streamlit...
streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Streamlit nao encontrado!
    pause
    exit /b 1
)
echo ✅ Streamlit OK!

echo [6/6] Iniciando Dashboard...
echo.
echo 🚀 DASHBOARD INICIANDO...
echo    URL: http://localhost:8501
echo.

start streamlit run Dash.py

echo.
echo ========================================
echo    DASHBOARD FUNCIONANDO!
echo ========================================
echo.
echo 💡 DICAS:
echo    - Se VPN falhar: Execute MODO_EMERGENCIA.bat
echo    - Para backup: Execute backup_automatico.bat
echo    - Para configurar: Execute usar_vscode_config.bat
echo.
pause
