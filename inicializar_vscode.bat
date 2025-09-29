@echo off
chcp 65001 >nul
echo ===============================================
echo INICIALIZANDO VSCODE COM PYTHON DO SISTEMA
echo ===============================================

REM Limpar COMPLETAMENTE todas as variaveis de ambiente virtual
set VIRTUAL_ENV=
set PYTHONHOME=
set CONDA_DEFAULT_ENV=
set PYTHONPATH=
set PIPENV_ACTIVE=
set POETRY_ACTIVE=
set PYENV_VERSION=
set CONDA_PYTHON_EXE=
set CONDA_EXE=

REM Definir Python especifico
set PYTHON_EXE=C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe

echo Python definido: %PYTHON_EXE%
echo.

REM Verificar se o Python existe
if not exist "%PYTHON_EXE%" (
    echo ERRO: Python nao encontrado em %PYTHON_EXE%
    pause
    exit /b 1
)

REM Verificar versao
echo Verificando versao do Python...
"%PYTHON_EXE%" --version

REM Verificar se pyvenv.cfg existe
if exist "pyvenv.cfg" (
    echo ✅ Arquivo pyvenv.cfg encontrado
) else (
    echo ⚠️  Criando arquivo pyvenv.cfg...
    echo home = C:\Users\u235107\AppData\Local\Programs\Python\Python313 > pyvenv.cfg
    echo executable = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe >> pyvenv.cfg
    echo command = C:\Users\u235107\AppData\Local\Programs\Python\Python313\python.exe -m venv C:\user\U235107\GitHub\Dash >> pyvenv.cfg
    echo include-system-site-packages = true >> pyvenv.cfg
    echo version = 3.13.7 >> pyvenv.cfg
    echo prompt = Dash >> pyvenv.cfg
    echo ✅ Arquivo pyvenv.cfg criado
)

echo.
echo ===============================================
echo CONFIGURACAO CONCLUIDA!
echo Agora abra o VS Code e:
echo 1. Pressione Ctrl+Shift+P
echo 2. Digite: Python: Select Interpreter
echo 3. Escolha: %PYTHON_EXE%
echo ===============================================
pause
