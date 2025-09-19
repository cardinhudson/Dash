@echo off
echo ====================================
echo LIMPEZA COMPLETA DE CACHE DO CURSOR
echo ====================================
echo.

echo [1/6] Fechando processos do Cursor...
taskkill /f /im "Cursor.exe" 2>nul
timeout /t 3 /nobreak >nul

echo [2/6] Limpando cache do AppData...
if exist "%APPDATA%\Cursor\logs" (
    rd /s /q "%APPDATA%\Cursor\logs" 2>nul
    echo   ✓ Logs removidos
)

if exist "%APPDATA%\Cursor\CachedData" (
    rd /s /q "%APPDATA%\Cursor\CachedData" 2>nul
    echo   ✓ Cache de dados removido
)

if exist "%APPDATA%\Cursor\User\workspaceStorage" (
    rd /s /q "%APPDATA%\Cursor\User\workspaceStorage" 2>nul
    echo   ✓ Storage de workspace removido
)

echo [3/6] Limpando cache do LocalAppData...
if exist "%LOCALAPPDATA%\Cursor\logs" (
    rd /s /q "%LOCALAPPDATA%\Cursor\logs" 2>nul
    echo   ✓ Logs locais removidos
)

if exist "%LOCALAPPDATA%\Cursor\CachedData" (
    rd /s /q "%LOCALAPPDATA%\Cursor\CachedData" 2>nul
    echo   ✓ Cache local removido
)

echo [4/6] Limpando arquivos temporários...
del /q /f "%TEMP%\cursor*" 2>nul
del /q /f "%TEMP%\vscode*" 2>nul
echo   ✓ Temporários removidos

echo [5/6] Limpando DNS e rede...
ipconfig /flushdns >nul
echo   ✓ DNS limpo

echo [6/6] Otimizando configurações de rede...
netsh int tcp reset >nul
echo   ✓ TCP resetado

echo.
echo ====================================
echo LIMPEZA CONCLUÍDA COM SUCESSO!
echo ====================================
echo.
echo Cursor foi completamente limpo e otimizado.
echo Reinicie o Cursor para aplicar as mudanças.
echo.
pause



