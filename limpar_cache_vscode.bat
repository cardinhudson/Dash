@echo off
chcp 65001 >nul
echo ===============================================
echo LIMPEZA COMPLETA DO CACHE VS CODE
echo ===============================================

REM Fechar VS Code completamente
echo Fechando VS Code...
taskkill /f /im "Code.exe" /t 2>nul
taskkill /f /im "python.exe" /t 2>nul
timeout /t 3 >nul

REM Limpar workspace state VS Code
echo Limpando workspace state...
if exist "%APPDATA%\Code\User\workspaceStorage" (
    for /d %%i in ("%APPDATA%\Code\User\workspaceStorage\*") do (
        if exist "%%i\workspace.json" (
            findstr /c:"Dash" "%%i\workspace.json" >nul 2>&1
            if not errorlevel 1 (
                echo Removendo cache do workspace Dash...
                rmdir /s /q "%%i" 2>nul
            )
        )
    )
)

REM Limpar configurações específicas do Python
echo Limpando configurações Python...
if exist "%APPDATA%\Code\User\settings.json" (
    echo Backup de settings.json...
    copy "%APPDATA%\Code\User\settings.json" "%APPDATA%\Code\User\settings.json.backup" >nul 2>&1
)

REM Remover interpretadores Python cachados
echo Limpando cache Python...
for /d %%i in ("%APPDATA%\Code\User\globalStorage\*python*") do rmdir /s /q "%%i" 2>nul
for /d %%i in ("%APPDATA%\Code\CachedExtensions\*python*") do rmdir /s /q "%%i" 2>nul

REM Forçar recriação do interpretador
echo Forçando redetecção Python...
if exist ".vscode\settings.json" (
    echo Configuração local encontrada - mantendo
) else (
    echo Criando configuração local...
    mkdir .vscode 2>nul
    echo { > .vscode\settings.json
    echo   "python.defaultInterpreterPath": "python", >> .vscode\settings.json
    echo   "python.terminal.activateEnvironment": false >> .vscode\settings.json
    echo } >> .vscode\settings.json
)

echo.
echo ===============================================
echo LIMPEZA CONCLUÍDA!
echo.
echo AGORA:
echo 1. Abra o VS Code
echo 2. Ctrl+Shift+P
echo 3. "Python: Select Interpreter"
echo 4. Escolha Python 3.13.7 (sistema)
echo 5. Execute: F5 ou python Extração.py
echo ===============================================
pause
