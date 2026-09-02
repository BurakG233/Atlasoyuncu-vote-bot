@echo off
chcp 65001 >nul
title Atlasoyuncu G233 Vote - Vote Bot
cd /d "%~dp0..\.."

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              Atlasoyuncu G233 Vote - VOTE BOT                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

rem Python'u bul (py launcher veya python)
set "PY=python"
py --version >nul 2>&1 && set "PY=py"

%PY% --version >nul 2>&1
if errorlevel 1 (
    echo   [HATA] Python bulunamadi.
    echo   Once 'install.cmd' dosyasini calistir, o her seyi kurar.
    echo.
    pause
    exit /b 1
)

rem SeleniumBase kontrolü
%PY% -c "import seleniumbase" >nul 2>&1
if errorlevel 1 (
    echo   [BILGI] seleniumbase yuklu degil, yukleniyor...
    %PY% -m pip install --user seleniumbase
)

rem Kullanıcı adını göster
echo   Kullanıcı adı:
%PY% -c "import json,pathlib; print('   ->', json.loads(pathlib.Path('config/bot_config.json').read_text(encoding='utf-8')).get('vote_username','?'))"
echo.

rem --auto: otomatik mod (zamanlayıcı için)
if /i "%~1"=="--auto" (
    echo   Otomatik mod: oy veriliyor, islem bitince kapanacak...
    echo.
    %PY% main.py --auto
    echo.
    exit /b 0
)

echo   Bot baslatiliyor... (menüden [1] ile oy verebilirsin)
echo.
%PY% main.py

echo.
echo   Islem tamamlandi.
pause