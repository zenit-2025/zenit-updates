@echo off
title TECNOLOGIA ZENIT - Inicializador del Sistema
color 0B

echo =======================================================
echo      Buscando Actualizaciones del Sistema...
echo =======================================================
echo.

:: ENLACE DIRECTO A TU CÓDIGO EN GITHUB (Con destructor de caché)
set "URL_SERVIDOR=https://raw.githubusercontent.com/zenit-2025/zenit-updates/main/Gestor-ZENIT.py?nocache=%RANDOM%"

:: Descarga el código a un archivo temporal
curl -s -f -L -o actualizacion_temp.py "%URL_SERVIDOR%"

IF EXIST actualizacion_temp.py (
    :: Reemplaza el archivo viejo con el nuevo
    move /y actualizacion_temp.py Gestor-ZENIT.py >nul
    color 0A
    echo [OK] Sistema sincronizado y actualizado a la ultima version de TECNOLOGIA ZENIT.
) ELSE (
    color 0E
    echo [ADVERTENCIA] No se pudo conectar con el servidor central.
    echo Iniciando la version local almacenada...
)
echo.

echo =======================================================
echo      Verificando Dependencias de Software...
echo =======================================================
echo.

echo [1/3] yt-dlp (Motor de Descarga)...
pip install -U yt-dlp -q
echo [2/3] Pillow (Motor Grafico)...
pip install pillow -q
echo [3/3] Mutagen (Metadatos)...
pip install mutagen -q

echo.
IF NOT EXIST "ffmpeg\ffmpeg.exe" (
    color 0C
    echo [ERROR CRITICO] Falta el motor FFmpeg. 
    echo Copia la carpeta "ffmpeg" original a esta computadora.
    pause
    exit
)

color 0B
echo =======================================================
echo      Iniciando Sistema Principal ZENIT-MX...
echo =======================================================
:: Ejecuta exactamente el nuevo nombre de tu archivo
python Gestor-ZENIT.py

exit