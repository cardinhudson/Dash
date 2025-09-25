@echo off
echo ========================================
echo    MODO EMERGENCIA - VPN FALHOU
echo ========================================
echo.

echo [1/4] Limpando cache de rede...
netsh winsock reset >nul 2>&1
netsh int ip reset >nul 2>&1
ipconfig /flushdns >nul 2>&1

echo [2/4] Reiniciando adaptadores de rede...
ipconfig /release >nul 2>&1
ipconfig /renew >nul 2>&1

echo [3/4] Testando conexao basica...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Conexao restaurada!
) else (
    echo ⚠️ Conexao ainda instavel
)

echo [4/4] Iniciando sistema local...
echo.
echo 🚀 EXECUTANDO DASHBOARD LOCAL...
echo    (Trabalhe offline enquanto VPN se estabiliza)
echo.

start streamlit run Dash.py

echo.
echo ========================================
echo    SISTEMA INICIADO EM MODO LOCAL
echo ========================================
pause
