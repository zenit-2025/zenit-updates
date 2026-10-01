@echo off
title TECNOLOGIA ZENIT - Inicializador del Sistema
color 0B

:: [SISTEMA ANTIBUCLE]
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
        echo [!] Nueva version del Lanzador detectada. Instalando...
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
    echo [OK] Modulo principal Python sincronizado y al dia.
) ELSE (
    color 0E
    echo [ADVERTENCIA] No se pudo conectar al servidor de GitHub.
)
echo.

echo =======================================================
echo      Verificando Dependencias de Software...
echo =======================================================
pip install -U yt-dlp -q
pip install pillow -q
pip install mutagen -q

echo.
IF NOT EXIST "ffmpeg\ffmpeg.exe" (
    color 0C
    echo [ERROR CRITICO] Falta el motor FFmpeg. 
    pause
    exit
)

color 0B
echo =======================================================
echo      Iniciando Sistema Principal ZENIT-MX...
echo =======================================================
python Gestor-ZENIT.py

exit
