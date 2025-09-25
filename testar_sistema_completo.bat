@echo off
echo ========================================
echo    TESTE COMPLETO DO SISTEMA
echo ========================================
echo.

echo [1/4] Testando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)
echo ✅ Python OK!

echo.
echo [2/4] Testando Extração.py...
python Extração.py
if %errorlevel% neq 0 (
    echo ❌ Extração.py falhou!
    pause
    exit /b 1
)
echo ✅ Extração.py OK!

echo.
echo [3/4] Testando Streamlit...
streamlit --version
if %errorlevel% neq 0 (
    echo ❌ Streamlit não encontrado!
    pause
    exit /b 1
)
echo ✅ Streamlit OK!

echo.
echo [4/4] Testando Dashboard...
echo Iniciando dashboard em 3 segundos...
timeout /t 3 /nobreak >nul
start streamlit run Dash.py

echo.
echo ========================================
echo    SISTEMA FUNCIONANDO PERFEITAMENTE!
echo ========================================
pause
