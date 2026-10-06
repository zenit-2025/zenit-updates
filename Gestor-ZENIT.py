@echo off
title TECNOLOGIA ZENIT - Inicializador del Sistema
color 0B

:: [SISTEMA ANTIBUCLE]
if "%~1"=="ACTUALIZADO" goto :fase_python

echo =======================================================
echo      Comprobando Actualizaciones del Sistema OTA...
echo =======================================================
echo.

:: [MEJORA] Pre-chequeo de conectividad a Internet
ping -n 1 raw.githubusercontent.com >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [ADVERTENCIA] Sin conexion a Internet. Iniciando en modo Off-line...
    goto :verificar_dependencias
)

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
    :: [REPARACION] Comparar archivo Python antes de sobreescribir para evitar desgaste
    IF EXIST Gestor-ZENIT.py (
        fc Gestor-ZENIT.py actualizacion_temp.py >nul
        if errorlevel 1 (
            move /y actualizacion_temp.py Gestor-ZENIT.py >nul
            color 0A
            echo [OK] Modulo principal Python actualizado a la ultima version.
        ) ELSE (
            del actualizacion_temp.py
            color 0A
            echo [OK] Modulo principal Python ya esta al dia.
        )
    ) ELSE (
        move /y actualizacion_temp.py Gestor-ZENIT.py >nul
        color 0A
        echo [OK] Modulo principal Python descargado por primera vez.
    )
) ELSE (
    color 0E
    echo [ADVERTENCIA] No se pudo descargar la actualizacion de GitHub.
)
echo.

:verificar_dependencias
echo =======================================================
echo      Verificando Dependencias de Software...
echo =======================================================

:: [REPARACION] Verificar si Python existe antes de intentar usarlo
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR CRITICO] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python en esta PC para continuar.
    pause
    exit
)

:: [MEJORA] Silenciar los warnings amarillos molestos de PIP
pip install -U yt-dlp -q >nul 2>&1
pip install pillow -q >nul 2>&1
pip install mutagen -q >nul 2>&1

echo.
:: [MEJORA] Buscar FFmpeg en la carpeta local, y si no esta, buscarlo en el sistema
IF NOT EXIST "ffmpeg\ffmpeg.exe" (
    where ffmpeg >nul 2>&1
    if errorlevel 1 (
        color 0C
        echo [ERROR CRITICO] Falta el motor FFmpeg ^(ni en carpeta local ni en el sistema general^). 
        pause
        exit
    )
)

:: [REPARACION] Evitar ejecucion fantasma si no hay script que ejecutar
IF NOT EXIST "Gestor-ZENIT.py" (
    color 0C
    echo [ERROR CRITICO] No se encontro "Gestor-ZENIT.py" y no hay internet para descargarlo.
    pause
    exit
)

color 0B
echo =======================================================
echo      Iniciando Sistema Principal ZENIT-MX...
echo =======================================================
python Gestor-ZENIT.py

:: [MEJORA] Atrapar crasheos (Si Python falla, se pausa para que puedas leer el error)
if %errorlevel% neq 0 (
    echo.
    color 0C
    echo [ERROR] El sistema Python se cerro de forma inesperada.
    pause
)

:: [REPARACION FINAL] Evitar que la ventana se cierre si todo sale bien o si falla.
pause
exit
