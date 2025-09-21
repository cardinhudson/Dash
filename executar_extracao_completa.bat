@echo off
echo 🚀 Executando Extração de Dados KE5Z...
echo.
echo ⏰ Iniciado em: %date% %time%
echo.

REM Usar caminho completo do Python para evitar erro "No pyvenv.cfg file"
C:\Users\u235107\AppData\Local\Programs\Python\Python311\python.exe Extração.py

echo.
echo ⏰ Concluído em: %date% %time%
echo.
echo 🎉 Extração finalizada!
echo.
pause