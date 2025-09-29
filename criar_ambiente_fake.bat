@echo off
chcp 65001 >nul
echo ===============================================
echo CRIANDO AMBIENTE FAKE PARA VS CODE
echo ===============================================

set PYTHON_ORIGEM=C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe
set PYTHON_DESTINO=Scripts\python.exe

echo Copiando Python do sistema...
if not exist "Scripts" mkdir Scripts

if exist "%PYTHON_ORIGEM%" (
    copy "%PYTHON_ORIGEM%" "%PYTHON_DESTINO%" >nul
    echo ✅ Python copiado para Scripts\python.exe
) else (
    echo ❌ Python nao encontrado em %PYTHON_ORIGEM%
    pause
    exit /b 1
)

echo Criando arquivo pyvenv.cfg na raiz...
echo home = C:\Users\u235107\AppData\Local\Programs\Python\Python313 > pyvenv.cfg
echo executable = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe >> pyvenv.cfg
echo command = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe -m venv C:\user\U235107\GitHub\Dash >> pyvenv.cfg
echo include-system-site-packages = true >> pyvenv.cfg
echo version = 3.13.7 >> pyvenv.cfg
echo prompt = Dash >> pyvenv.cfg
echo ✅ pyvenv.cfg criado na raiz

echo Criando arquivo pyvenv.cfg em Scripts...
echo home = C:\Users\u235107\AppData\Local\Programs\Python\Python313 > Scripts\pyvenv.cfg
echo executable = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe >> Scripts\pyvenv.cfg
echo command = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe -m venv C:\user\U235107\GitHub\Dash >> Scripts\pyvenv.cfg
echo include-system-site-packages = true >> Scripts\pyvenv.cfg
echo version = 3.13.7 >> Scripts\pyvenv.cfg
echo prompt = Dash >> Scripts\pyvenv.cfg
echo ✅ pyvenv.cfg criado em Scripts

echo.
echo ===============================================
echo AMBIENTE FAKE CRIADO COM SUCESSO!
echo Agora o VS Code deve encontrar o pyvenv.cfg
echo ===============================================
pause
