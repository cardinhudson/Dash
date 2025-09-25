@echo off
echo ========================================
echo    USAR CONFIGURACAO VS CODE
echo ========================================
echo.

echo [1/3] Lendo configuracoes do VS Code...
python usar_config_vscode.py

echo.
echo [2/3] Aplicando configuracoes de rede...
echo Configuracoes aplicadas com sucesso!

echo.
echo [3/3] Testando conexao...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Conexao OK! Sistema configurado.
) else (
    echo ⚠️ Conexao instavel. Execute novamente se necessario.
)

echo.
echo ========================================
echo    CONFIGURACAO CONCLUIDA
echo ========================================
pause
