@echo off
chcp 65001 >nul
cls
echo ========================================
echo      EXTRAÇÃO KE5Z - EXECUÇÃO DIRETA
echo ========================================
echo.

echo Usando Python do sistema...
python --version
echo.

echo Iniciando extração de dados...
echo.

REM Executar diretamente com Python do sistema
python Extração.py

echo.
echo ========================================
echo         EXTRAÇÃO CONCLUÍDA
echo ========================================
echo.
pause


