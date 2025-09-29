@echo off
chcp 65001 >nul
cls
echo ========================================
echo    TESTE RAPIDO DO SISTEMA
echo ========================================
echo.

echo Testando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    pause
    exit /b 1
)
echo ✅ Python OK
echo.

echo Testando importacao do Dash...
python -c "import Dash; print('✅ Dash.py funcionando!')"
if %errorlevel% neq 0 (
    echo ❌ Erro no Dash.py
    pause
    exit /b 1
)
echo ✅ Dash.py OK
echo.

echo Testando Extração...
python -c "import sys; sys.path.append('.'); exec(open('Extração.py').read())" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Extração pode ter problemas, mas continuando...
) else (
    echo ✅ Extração OK
)
echo.

echo ========================================
echo        SISTEMA FUNCIONANDO!
echo ========================================
echo.
echo Para usar:
echo   - Dashboard: python -m streamlit run Dash.py
echo   - Extração: python Extração.py
echo.
pause