@echo off
title TECNOLOGIA ZENIT - Inicializador del Sistema
color 0B

:: [SISTEMA ANTIBUCLE]
if "%~1"=="ACTUALIZADO" goto :fase_python

echo =======================================================
echo      Comprobando Actualizaciones del Sistema OTA...
echo =======================================================
echo.

:: [MEJORA] Pre-chequeo de conectividad a Internet (Modo Off-line)
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
    :: [MEJORA] Proteccion de almacenamiento usando FC para evitar sobreescrituras innecesarias
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
echo =================================
