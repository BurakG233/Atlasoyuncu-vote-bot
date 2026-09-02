@echo off
chcp 65001 >nul
title Atlasoyuncu G233 Vote - Zamanlayıcı Kurulumu (Windows)
color 0E
setlocal EnableDelayedExpansion

cd /d "%~dp0..\.."
set "WORKDIR=%CD%"
set "PYTHON=%SystemRoot%\py.exe"

if not exist "%PYTHON%" (
    where python >nul 2>&1
    if errorlevel 1 (
        echo  [HATA] python bulunamadi. Once install.cmd calistirin.
        pause
        exit /b 1
    )
    for /f %%i in ('where python') do set "PYTHON=%%i"
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║      WINDOWS GOREV ZAMANLAYICI KURULUMU                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Python : %PYTHON%
echo  Dizin  : %WORKDIR%
echo.

rem ── Görev 1: Her gün 09:00 ──
echo [1/2] "AtlasoyuncuG233VoteBotGunluk" gorevi olusturuluyor (09:00)...
schtasks /Create /F /TN "AtlasoyuncuG233VoteBotGunluk" /TR "\"%PYTHON%\" \"%WORKDIR%\main.py\" --auto" /SC DAILY /ST 09:00 /RL LIMITED >nul 2>&1
if errorlevel 1 (
    echo   [HATA] Gunluk gorev olusturulamadi. Yonetici olarak calistir.
) else (
    echo   [OK] Gunluk gorev olusturuldu (09:00).
)

rem ── Görev 2: Oturum açılışında ──
echo [2/2] "AtlasoyuncuG233VoteBotAcilis" gorevi olusturuluyor...
schtasks /Create /F /TN "AtlasoyuncuG233VoteBotAcilis" /TR "\"%PYTHON%\" \"%WORKDIR%\main.py\" --auto" /SC ONLOGON /RL LIMITED >nul 2>&1
if errorlevel 1 (
    echo   [HATA] Acilis gorevi olusturulamadi.
) else (
    echo   [OK] Acilis gorevi olusturuldu.
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           ZAMANLAYICI KURULDU!                               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  Kontrol / silme:
echo    schtasks /Query /TN AtlasoyuncuG233VoteBotGunluk
echo    schtasks /Delete /F /TN AtlasoyuncuG233VoteBotGunluk
echo    schtasks /Delete /F /TN AtlasoyuncuG233VoteBotAcilis
echo.
pause
