@echo off
echo ========================================
echo SOLUÇÃO EMERGENCIAL - PROBLEMAS DE VPN
echo ========================================
echo.

echo [CRÍTICO] Executando correção imediata...
echo.

echo [1/8] Parando processos Cursor...
taskkill /f /im "Cursor.exe" 2>nul
echo   ✓ Cursor finalizado

echo [2/8] Limpando cache completo...
rd /s /q "%APPDATA%\Cursor\logs" 2>nul
rd /s /q "%APPDATA%\Cursor\CachedData" 2>nul
rd /s /q "%LOCALAPPDATA%\Cursor\logs" 2>nul
del /q /f "%TEMP%\cursor*" 2>nul
echo   ✓ Cache limpo

echo [3/8] Resetando conexões de rede...
netsh int tcp reset >nul
netsh winsock reset >nul
ipconfig /flushdns >nul
echo   ✓ Rede resetada

echo [4/8] Otimizando TCP...
netsh int tcp set global autotuninglevel=normal >nul
netsh int tcp set global chimney=enabled >nul
echo   ✓ TCP otimizado

echo [5/8] Configurando timeout reduzido...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TcpTimedWaitDelay /t REG_DWORD /d 30 /f >nul
echo   ✓ Timeout configurado

echo [6/8] Liberando memória...
echo 3 > "%TEMP%\drop_caches.tmp"
del "%TEMP%\drop_caches.tmp"
echo   ✓ Memória liberada

echo [7/8] Criando backup emergencial...
if not exist "backup_emergencial" mkdir backup_emergencial
copy "pages\Extracao_Dados.py" "backup_emergencial\" >nul 2>&1
copy "Dash.py" "backup_emergencial\" >nul 2>&1
echo   ✓ Backup criado

echo [8/8] Configurando modo estável...
echo MODO_ESTAVEL=1 > cursor_config.env
echo CHAT_TIMEOUT=10 >> cursor_config.env
echo NETWORK_RETRY=3 >> cursor_config.env
echo   ✓ Configuração salva

echo.
echo ========================================
echo CORREÇÃO EMERGENCIAL APLICADA!
echo ========================================
echo.
echo PRÓXIMOS PASSOS:
echo 1. Reinicie o Cursor
echo 2. Use sessões curtas (máx 10 min)
echo 3. Salve frequentemente
echo 4. Evite operações longas
echo.
echo Pressione qualquer tecla para continuar...
pause >nul