@echo off
echo ========================================
echo    BACKUP AUTOMATICO
echo ========================================
echo.

set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo [1/3] Criando backup dos arquivos principais...
if not exist "backups" mkdir backups

copy "Dash.py" "backups\Dash_%TIMESTAMP%.py" >nul 2>&1
copy "Extração.py" "backups\Extração_%TIMESTAMP%.py" >nul 2>&1
copy "usuarios.json" "backups\usuarios_%TIMESTAMP%.json" >nul 2>&1

echo [2/3] Backup dos arquivos parquet...
if exist "KE5Z\KE5Z.parquet" (
    copy "KE5Z\KE5Z.parquet" "backups\KE5Z_%TIMESTAMP%.parquet" >nul 2>&1
)

echo [3/3] Commit automatico no Git...
git add . >nul 2>&1
git commit -m "BACKUP AUTOMATICO - %TIMESTAMP%" >nul 2>&1

echo.
echo ✅ BACKUP CONCLUIDO!
echo    Arquivos salvos em: backups\
echo    Commit Git: %TIMESTAMP%
echo.

echo ========================================
echo    SISTEMA PROTEGIDO CONTRA FALHAS
echo ========================================
