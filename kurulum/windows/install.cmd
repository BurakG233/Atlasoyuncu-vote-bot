@echo off
chcp 65001 >nul
title Atlasoyuncu G233 Vote - Windows Kurulumu
color 0A

rem ── Proje kökünü bul (kurulum\windows\ üstü) ──
cd /d "%~dp0..\.."

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║        Atlasoyuncu G233 Vote - Windows Kurulum Sihirbazı              ║
echo ║                                                              ║
echo ║  1. Python kontrol / kurulum                                 ║
echo ║  2. SeleniumBase kurulumu                                    ║
echo ║  3. Minecraft kullanıcı adını ayarlama                       ║
echo ║  4. Opsiyonel: botu hemen test etme                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

rem ── ADIM 1: Python ──
echo [1/4] PYTHON KONTROLÜ
echo ----------------------------------------
set "PY=python"
py --version >nul 2>&1 && set "PY=py"

%PY% --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   [HATA] Python bulunamadi!
    echo   Indirme sayfasi aciliyor...
    start https://www.python.org/downloads/
    echo.
    echo   Kurulum sirasinda "Add Python to PATH" kutusunu isaretlemeyi unutma.
    echo   Kurulumu tamamlayip bu dosyayi YENIDEN cift tikla.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY% --version 2^>^&1') do echo   [OK] %%v

rem ── ADIM 2: pip ──
echo.
echo [2/4] PIP KONTROLÜ
echo ----------------------------------------
%PY% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo   pip kuruluyor...
    %PY% -m ensurepip --upgrade
)
for /f "tokens=*" %%v in ('%PY% -m pip --version 2^>^&1') do echo   [OK] %%v

rem ── ADIM 3: SeleniumBase ──
echo.
echo [3/4] KÜTÜPHANE KONTROLÜ
echo ----------------------------------------
%PY% -c "import seleniumbase" >nul 2>&1
if errorlevel 1 (
    echo   seleniumbase yukleniyor...
    %PY% -m pip install --user seleniumbase
    echo   [OK] seleniumbase kuruldu.
) else (
    echo   [OK] seleniumbase zaten yuklu.
)

rem ── ADIM 4: Kullanıcı adı ──
echo.
echo [4/4] MINECRAFT KULLANICI ADI
echo ----------------------------------------
set "USERNAME="
:askname
set /p "USERNAME=Minecraft kullanici adini yaz ve Enter'a bas: "
if "%USERNAME%"=="" (
    echo   Bos olamaz! Tekrar dene.
    goto askname
)

%PY% -c "import json,pathlib; p=pathlib.Path('config/bot_config.json'); d=json.loads(p.read_text(encoding='utf-8')); d['vote_username']='%USERNAME%'; p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8'); print('   [OK] Kullanici adi ayarlandi:', d['vote_username'])"

rem ── BİTTİ ──
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              KURULUM TAMAMLANDI!  ✓                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo   Kullanici adi : %USERNAME%
echo   Kurulum dizini: %CD%
echo.
echo   Ne yapmak istersin?
echo     [1] Botu hemen test et
echo     [2] Cikis (daha sonra 'baslatma\windows\baslat.cmd' ile baslat)
echo.
choice /c 12 /n /m "Secimin (1 veya 2): "
if errorlevel 2 goto end
if errorlevel 1 goto test

:test
echo.
%PY% main.py
goto end

:end
echo.
echo   Botu baslatmak icin 'baslatma\windows\baslat.cmd' dosyasina cift tikla.
echo.
pause
