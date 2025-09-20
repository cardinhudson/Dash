@echo off
chcp 65001 >nul
cls
echo ========================================
echo    DASHBOARD KE5Z - CONFIGURACAO TOTAL
echo ========================================
echo.
echo Sistema inteligente de configuracao
echo Detecta e instala tudo automaticamente
echo Compativel com qualquer PC Windows
echo.

REM ============================================
REM VERIFICACAO E INSTALACAO DO PYTHON
REM ============================================
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no sistema!
    echo.
    echo INSTALACAO NECESSARIA:
    echo    1. Acesse: https://python.org/downloads
    echo    2. Baixe Python 3.8 ou superior
    echo    3. Durante a instalacao, MARQUE "Add Python to PATH"
    echo    4. Reinicie o computador apos instalar
    echo    5. Execute este arquivo novamente
    echo.
    echo CRITICO: "Add Python to PATH" e obrigatorio!
    echo.
    pause
    exit /b 1
)

echo OK: Python encontrado:
%PYTHON_CMD% --version
echo.

REM ============================================
REM LIMPEZA PREVENTIVA
REM ============================================
echo Preparando ambiente limpo...

REM Remover ambiente virtual corrompido se existir
if exist "venv" (
    echo Removendo ambiente virtual anterior...
    rmdir /s /q venv >nul 2>&1
    timeout /t 2 >nul 2>&1
)

REM Limpar cache do pip
python -m pip cache purge >nul 2>&1

echo OK: Ambiente preparado
echo.

REM ============================================
REM CRIACAO DO AMBIENTE VIRTUAL
REM ============================================
echo Criando ambiente virtual limpo...

python -m venv venv --clear
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel criar ambiente virtual!
    echo.
    echo SOLUCOES:
    echo    1. Execute como Administrador
    echo    2. Verifique permissoes da pasta
    echo    3. Desative temporariamente o antivirus
    echo    4. Tente em pasta diferente
    echo.
    echo Tentando instalacao global como alternativa...
    set "ENV_TYPE=Global Python (Fallback)"
    set "INSTALL_MODE=global"
    goto :skip_venv
)

echo OK: Ambiente virtual criado
echo.

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "PIP_CMD=venv\Scripts\pip.exe"
    echo OK: Usando Python do ambiente virtual
    set "ENV_TYPE=Virtual Environment"
    set "INSTALL_MODE=venv"
) else (
    echo AVISO: Python do ambiente virtual nao encontrado
    echo Usando instalacao global...
    set "PYTHON_CMD=python"
    set "PIP_CMD=pip"
    set "ENV_TYPE=Global Python (Fallback)"
    set "INSTALL_MODE=global"
    goto :skip_venv
)

echo OK: Ambiente virtual ativado
set "ENV_TYPE=Virtual Environment"
set "INSTALL_MODE=venv"

:skip_venv
echo Ambiente configurado: %ENV_TYPE%
echo.

REM ============================================
REM ATUALIZACAO DO PIP
REM ============================================
echo Atualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip --no-warn-script-location --disable-pip-version-check --quiet
if %errorlevel% neq 0 (
    echo AVISO: Nao foi possivel atualizar pip (continuando...)
) else (
    echo OK: Pip atualizado
)
echo.

REM ============================================
REM VERIFICACAO E INSTALACAO DE DEPENDENCIAS
REM ============================================
echo Verificando dependencias essenciais...

REM Lista de dependencias essenciais
set "DEPS_OK=1"

REM Verificar cada dependencia
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: Streamlit
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import streamlit; print('   OK: Streamlit', streamlit.__version__)" 2>nul
)

%PYTHON_CMD% -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: Pandas
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import pandas; print('   OK: Pandas', pandas.__version__)" 2>nul
)

%PYTHON_CMD% -c "import altair" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: Altair
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import altair; print('   OK: Altair', altair.__version__)" 2>nul
)

%PYTHON_CMD% -c "import plotly" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: Plotly
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import plotly; print('   OK: Plotly', plotly.__version__)" 2>nul
)

%PYTHON_CMD% -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: OpenPyXL
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import openpyxl; print('   OK: OpenPyXL', openpyxl.__version__)" 2>nul
)

%PYTHON_CMD% -c "import pyarrow" >nul 2>&1
if %errorlevel% neq 0 (
    echo    FALTA: PyArrow
    set "DEPS_OK=0"
) else (
    %PYTHON_CMD% -c "import pyarrow; print('   OK: PyArrow', pyarrow.__version__)" 2>nul
)

REM Instalar dependencias se necessario
if "%DEPS_OK%"=="0" (
    echo.
    echo Instalando dependencias em falta...
    echo Isso pode demorar alguns minutos...
    echo.
    
    REM Instalar todas de uma vez para melhor compatibilidade
    echo Instalando pacotes essenciais...
    %PYTHON_CMD% -m pip install streamlit pandas altair plotly openpyxl pyarrow --no-warn-script-location --disable-pip-version-check --quiet
    
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Falha na instalacao das dependencias!
        echo.
        echo SOLUCOES RECOMENDADAS:
        echo    1. Verifique conexao com a internet
        echo    2. Execute como Administrador
        echo    3. Desative temporariamente antivirus/firewall
        echo    4. Tente instalacao manual:
        echo       %PYTHON_CMD% -m pip install streamlit pandas altair plotly openpyxl pyarrow
        echo.
        echo Tentando instalacao individual...
        
        REM Tentar instalar uma por uma
        %PYTHON_CMD% -m pip install streamlit --no-warn-script-location --quiet
        %PYTHON_CMD% -m pip install pandas --no-warn-script-location --quiet
        %PYTHON_CMD% -m pip install altair --no-warn-script-location --quiet
        %PYTHON_CMD% -m pip install plotly --no-warn-script-location --quiet
        %PYTHON_CMD% -m pip install openpyxl --no-warn-script-location --quiet
        %PYTHON_CMD% -m pip install pyarrow --no-warn-script-location --quiet
    )
    
    REM Verificar se instalacao funcionou
    echo.
    echo Verificando instalacao final...
    %PYTHON_CMD% -c "import streamlit, pandas, altair, plotly, openpyxl, pyarrow; print('OK: Todas as dependencias instaladas!')" 2>nul
    if %errorlevel% neq 0 (
        echo.
        echo AVISO: Algumas dependencias podem estar faltando
        echo O dashboard pode funcionar com funcionalidades limitadas
        echo.
        echo Para instalacao completa, execute manualmente:
        echo    %PYTHON_CMD% -m pip install streamlit pandas altair plotly openpyxl pyarrow
        echo.
        pause
    ) else (
        echo OK: Instalacao concluida com sucesso!
    )
) else (
    echo OK: Todas as dependencias ja estao instaladas!
)

echo.

REM ============================================
REM VERIFICACAO DE ARQUIVOS ESSENCIAIS
REM ============================================
echo Verificando arquivos do projeto...

REM Arquivos obrigatorios
if not exist "Dash.py" (
    echo ERRO: Arquivo principal Dash.py nao encontrado!
    echo    Verifique se voce esta na pasta correta do projeto.
    pause
    exit /b 1
)
echo    OK: Dash.py encontrado

if not exist "auth_simple.py" (
    echo ERRO: Arquivo auth_simple.py nao encontrado!
    echo    Sistema de autenticacao nao funcionara.
    pause
    exit /b 1
)
echo    OK: auth_simple.py encontrado

REM Criar diretorios necessarios
if not exist "KE5Z" (
    mkdir KE5Z
    echo    Pasta KE5Z criada
) else (
    echo    OK: Pasta KE5Z existe
)

if not exist "downloads" (
    mkdir downloads
    echo    Pasta downloads criada
) else (
    echo    OK: Pasta downloads existe
)

if not exist "pages" (
    mkdir pages
    echo    Pasta pages criada
) else (
    echo    OK: Pasta pages existe
)

if not exist "logs" (
    mkdir logs
    echo    Pasta logs criada
) else (
    echo    OK: Pasta logs existe
)

REM Verificar arquivo de usuarios (opcional)
if not exist "usuarios.json" (
    echo    INFO: usuarios.json sera criado automaticamente
) else (
    echo    OK: usuarios.json encontrado
)

REM Verificar arquivo de dados
if not exist "KE5Z\KE5Z.parquet" (
    echo    INFO: KE5Z.parquet nao encontrado
    echo.
    echo DADOS NAO ENCONTRADOS:
    echo    O dashboard funcionara para demonstracao
    echo    Para dados reais, coloque KE5Z.parquet na pasta KE5Z\
    echo.
) else (
    echo    OK: KE5Z.parquet encontrado
)

echo.

REM ============================================
REM VERIFICACAO FINAL DO SISTEMA
REM ============================================
echo Teste final do sistema...

REM Testar se Streamlit pode ser executado
%PYTHON_CMD% -c "import streamlit; print('OK: Streamlit funcionando!')" 2>nul
if %errorlevel% neq 0 (
    echo AVISO: Streamlit pode nao estar funcionando corretamente
    echo O sistema tentara iniciar mesmo assim...
)

REM Testar se Dash.py pode ser compilado
%PYTHON_CMD% -m py_compile Dash.py 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Dash.py contem erros de sintaxe!
    echo    Verifique o arquivo e corrija os erros.
    pause
    exit /b 1
) else (
    echo OK: Dash.py verificado e sem erros!
)

echo OK: Sistema verificado!
echo.

REM ============================================
REM INFORMACOES DO SISTEMA CONFIGURADO
REM ============================================
echo ========================================
echo        SISTEMA CONFIGURADO
echo ========================================
echo.
echo Ambiente: %ENV_TYPE%
echo Python: 
%PYTHON_CMD% --version
echo Dependencias: Verificadas
echo Estrutura: Completa
echo.

REM ============================================
REM INICIANDO O DASHBOARD
REM ============================================
echo ========================================
echo         INICIANDO DASHBOARD
echo ========================================
echo.
echo URL do Dashboard: http://localhost:8501
echo Login padrao: admin / admin123
echo.
echo INSTRUCOES:
echo    Para parar: Pressione Ctrl+C nesta janela
echo    Para reabrir: Execute este arquivo novamente
echo.
echo Ambiente: %ENV_TYPE%
echo Modo: %INSTALL_MODE%
echo.
echo ========================================

REM Aguardar alguns segundos e abrir navegador
echo Iniciando em 3 segundos...
timeout /t 3 >nul 2>&1

REM Tentar abrir no navegador
start http://localhost:8501 >nul 2>&1

REM Iniciar servidor Streamlit
echo.
echo Iniciando servidor Streamlit...
echo.
echo AGUARDE: O dashboard esta carregando...
echo Quando aparecer "You can now view your Streamlit app in your browser"
echo o dashboard estara pronto para uso!
echo.

%PYTHON_CMD% -m streamlit run Dash.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

REM Se chegou aqui, servidor foi encerrado
echo.
echo ========================================
echo         DASHBOARD ENCERRADO
echo ========================================
echo.
echo Para reiniciar: Execute este arquivo novamente
echo Ambiente: %ENV_TYPE%
echo.
echo Obrigado por usar o Dashboard KE5Z!
echo.
pause