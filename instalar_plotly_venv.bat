@echo off
echo Ativando ambiente virtual e instalando Plotly...
call venv\Scripts\activate.bat
python -m pip install plotly==5.17.0 --no-cache-dir
echo.
echo Plotly instalado no ambiente virtual!
pause
