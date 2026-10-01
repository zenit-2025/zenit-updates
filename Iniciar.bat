@echo off
title TECNOLOGIA ZENIT - Inicializador del Sistema
color 0B

:: =======================================================
:: 0. ESCANER DE SISTEMA (AUTO-INSTALADOR DE PYTHON)
:: =======================================================
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    color 0E
    echo =======================================================
    echo      SISTEMA BASE NO DETECTADO. PREPARANDO EQUIPO...
    echo =======================================================
    echo.
    echo [1/2] Descargando motor central (Python) desde el servidor oficial...
    curl -s -f -L -o python_installer.exe "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"

    echo [2/2] Instalando en segundo plano (Por favor espera, no cierres la ventana)...
    :: La variable PrependPath=1 es la que hace la magia de agregarlo al sistema
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

    del python_installer.exe
    color 0A
    echo.
    echo =======================================================
    echo   ¡INSTALACION DE SISTEMA BASE COMPLETADA!
    echo =======================================================
    echo Windows necesita actualizar sus registros para continuar.
    echo Por favor, presiona cualquier tecla para cerrar esta ventana.
    echo Despues, VUELVE A DAR DOBLE CLIC en "Iniciar.bat".
    pause >nul
    exit
)

:: =======================================================
:: 1. SISTEMA DE ACTUALIZACION REMOTA (OTA)
:: =======================================================
if "%~1"=="ACTUALIZADO" goto :fase_python

echo =======================================================
echo      Comprobando Actualizaciones del Sistema OTA...
echo =======================================================
echo.

set "URL_BAT=https://raw.githubusercontent.com/zenit-2025/zenit-updates/main/Iniciar.bat?nocache=%RANDOM%"
curl -s -f -L -o Iniciar_temp.bat "%URL_BAT%"

IF EXIST Iniciar_temp.bat (
    fc Iniciar.bat Iniciar_temp.bat >nul
    if errorlevel 1 (
        color 0E
        echo Novedad: Nueva version del Lanzador detectada. Instalando...
        copy /y Iniciar_temp.bat Iniciar.bat >nul
        del Iniciar_temp.bat
        start "" "Iniciar.bat" ACTUALIZADO
        exit
    )
    del Iniciar_temp.bat
)

:fase_python
set "URL_PYTHON=https://raw.githubusercontent.com/zenit-2025/zenit-updates/main/Gestor-ZENIT.py?nocache=%RANDOM%"
curl -s -f -L -o actualizacion_temp.py "%URL_PYTHON%"

IF EXIST actualizacion_temp.py (
    move /y actualizacion_temp.py Gestor-ZENIT.py >nul
    color 0A
    echo OK: Modulo principal sincronizado y al dia.
) ELSE (
    color 0E
    echo ADVERTENCIA: No se pudo conectar al servidor de GitHub.
)
echo.

:: =======================================================
:: 2. VERIFICACION DE DEPENDENCIAS Y LIBRERIAS
:: =======================================================
echo =======================================================
echo      Verificando Dependencias de Software...
echo =======================================================
pip install -U yt-dlp -q
pip install pillow -q
pip install mutagen -q

echo.
IF NOT EXIST "ffmpeg\ffmpeg.exe" (
    color 0C
    echo ERROR CRITICO: Falta el motor FFmpeg.
    pause
    exit
)

:: =======================================================
:: 3. ARRANQUE DEL SOFTWARE
:: =======================================================
color 0B
echo =======================================================
echo      Iniciando Sistema Principal ZENIT-MX...
echo =======================================================
python Gestor-ZENIT.py

exit
