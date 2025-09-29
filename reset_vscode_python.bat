@echo off
chcp 65001 >nul
echo ===============================================
echo RESETANDO VSCODE PARA PYTHON DO SISTEMA
echo ===============================================

REM Parar qualquer processo do VS Code
echo Fechando processos do VS Code...
taskkill /f /im "Code.exe" 2>nul
taskkill /f /im "python.exe" 2>nul
timeout /t 2 >nul

REM Remover pastas problemáticas
echo Removendo ambientes virtuais...
if exist ".venv" rmdir /s /q ".venv" 2>nul
if exist "venv" rmdir /s /q "venv" 2>nul
if exist "venv_novo" rmdir /s /q "venv_novo" 2>nul
if exist "env" rmdir /s /q "env" 2>nul

REM Limpar cache do Python
echo Limpando cache Python...
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
for /d %%i in (*__pycache__*) do rmdir /s /q "%%i" 2>nul

REM Verificar Python disponível
echo.
echo Verificando Python do sistema...
python --version
echo Caminho: 
where python

echo.
echo ===============================================
echo RESET CONCLUÍDO!
echo Agora:
echo 1. Abra o VS Code
echo 2. Ctrl+Shift+P
echo 3. Digite: Python: Clear Cache and Reload Window
echo 4. Execute: Python: Select Interpreter
echo 5. Escolha o Python do sistema
echo ===============================================
pause
