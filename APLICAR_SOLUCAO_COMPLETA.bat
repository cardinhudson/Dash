@echo off
echo ============================================
echo APLICANDO SOLUÇÃO COMPLETA - VPN/CONEXÃO
echo ============================================
echo.

echo [1/5] Executando limpeza emergencial...
call SOLUCAO_EMERGENCIAL_VPN.bat
echo.

echo [2/5] Criando backup de segurança...
if not exist "backup_estabilidade" mkdir backup_estabilidade
copy "pages\Extracao_Dados.py" "backup_estabilidade\" >nul 2>&1
copy "Dash.py" "backup_estabilidade\" >nul 2>&1
echo   ✓ Backup criado em backup_estabilidade\

echo [3/5] Verificando dashboard...
python -m py_compile Dash.py
if %errorlevel% equ 0 (
    echo   ✓ Dashboard OK
) else (
    echo   ❌ Erro no dashboard
)

echo [4/5] Verificando página de extração...
python -m py_compile pages\Extracao_Dados.py
if %errorlevel% equ 0 (
    echo   ✓ Extração OK
) else (
    echo   ❌ Erro na extração
)

echo [5/5] Iniciando dashboard otimizado...
echo.
echo ============================================
echo SOLUÇÃO APLICADA COM SUCESSO!
echo ============================================
echo.
echo 📋 PRÓXIMOS PASSOS:
echo.
echo 1. Configure o Cursor:
echo    - Abra: Ctrl + Shift + P
echo    - Digite: "Preferences: Open Settings (JSON)"
echo    - Cole o conteúdo de: configurar_cursor_estavel.json
echo.
echo 2. Acesse o dashboard:
echo    http://localhost:8515
echo.
echo 3. Siga o GUIA_RAPIDO_ESTABILIDADE.md
echo.
echo 💡 LEMBRE-SE:
echo - Sessões curtas (máx 10 min)
echo - Salve frequentemente
echo - Execute este script diariamente
echo.
echo Pressione qualquer tecla para abrir o dashboard...
pause >nul

start http://localhost:8515
echo Dashboard aberto no navegador!
echo.
pause

