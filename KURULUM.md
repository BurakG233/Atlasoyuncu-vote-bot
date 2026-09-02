# Atlasoyuncu G233 Vote — Vote Bot Kurulum Rehberi

> Bot, Minecraft sunucun icin oy sitelerine otomatik oy verir.
> Cloudflare engelini asar, istersen reCAPTCHA'yi otomatik cozer.

---

## Icindekiler

1. [Sistem Gereksinimleri](#1-sistem-gereksinimleri)
2. [Dosya Yapisi](#2-dosya-yapisi)
3. [Linux Kurulumu (Ubuntu / Debian)](#3-linux-kurulumu-ubuntu--debian)
4. [Fedora Kurulumu](#4-fedora-kurulumu)
5. [Windows Kurulumu](#5-windows-kurulumu)
6. [Ilk Calistirma ve Test](#6-ilk-calistirma-ve-test)
7. [Otomatik Calisma (Zamanlayici)](#7-otomatik-calisma-zamanlayici)
8. [Captcha (reCAPTCHA) Ayarlama](#8-captcha-recaptcha-ayarlama)
9. [Sorun Giderme](#9-sorun-giderme)

---

## 1. Sistem Gereksinimleri

| Gereksinim | Linux (Ubuntu/Debian) | Fedora | Windows |
|---|---|---|---|
| Isletim Sistemi | Ubuntu 20.04+ / Debian 11+ | Fedora 36+ | Windows 10 / 11 |
| Python | 3.8+ | 3.8+ | 3.8+ (PATH'e ekli) |
| Tarayici | Google Chrome / Chromium | Google Chrome / Chromium | Google Chrome / Edge |
| RAM | 2 GB+ | 2 GB+ | 2 GB+ |

---

## 2. Dosya Yapisi

```
atlas_vote_bot_merged/
├── main.py                    ← botun giris noktasi
├── atlas_vote_bot.py          ← geriye donuk uyumluluk shim
│
├── baslatma/                  ← baslatma dosyalari (cift tikla)
│   ├── linux/                 ← Linux (Ubuntu/Debian/Fedora)
│   │   ├── baslat.sh          ← Linux baslatma scripti
│   │   └── AtlasoyuncuG233VoteBot.desktop  ← masaustu kisa yolu (cift tik)
│   └── windows/               ← Windows
│       └── baslat.cmd         ← Windows baslatma scripti (cift tik)
│
├── kurulum/                   ← platforma ozel kurulum
│   ├── linux/                 ← Ubuntu / Debian
│   │   ├── install.sh
│   │   ├── G233Kurulum.desktop
│   │   ├── setup_systemd.sh
│   │   └── setup_cron.sh
│   ├── fedora/                ← Fedora
│   │   ├── install.sh
│   │   ├── G233Kurulum.desktop
│   │   ├── setup_systemd.sh
│   │   └── setup_cron.sh
│   └── windows/               ← Windows
│       ├── install.cmd
│       └── setup_windows_zamanlayici.cmd
│
├── config/
│   ├── bot_config.json        ← genel ayarlar
│   ├── vote_sites.json        ← vote siteleri
│   └── vote_state.json        ← son oy tarihleri
├── modules/
│   ├── vote_engine.py         ← oy verme motoru
│   └── menu.py                ← terminal menusu
├── utils/
│   └── logger.py              ← log sistemi
├── logs/
├── screenshots/
├── KURULUM.md                 ← bu dosya
├── KULLANIM_KILAVUZU.md
└── LICENSE
```

---

## 3. Linux Kurulumu (Ubuntu / Debian)

### Otomatik Kurulum (Onekirli)

```bash
cd ~/atlas_vote_bot_merged
chmod +x kurulum/linux/install.sh
./kurulum/linux/install.sh
```

Script sirayla:
- Python ve pip kontrol eder (yoksa `apt` ile kurar)
- Google Chrome / Chromium kurar (yoksa)
- SeleniumBase + yardimci kutuphaneleri yukler
- Minecraft kullanici adini sorar ve `config/bot_config.json`'a yazar

### Manuel Kurulum

```bash
sudo apt update
sudo apt install python3 python3-pip google-chrome-stable -y
pip3 install --user seleniumbase
```

### Baslatma

```bash
python3 main.py                # menu
./baslatma/linux/baslat.sh      # kontrol + baslat
```

---

## 4. Fedora Kurulumu

### Otomatik Kurulum (Onekirli)

```bash
cd ~/atlas_vote_bot_merged
chmod +x kurulum/fedora/install.sh
./kurulum/fedora/install.sh
```

Script sirayla:
- Python ve pip kontrol eder (yoksa `dnf` ile kurar)
- Google Chrome RPM repo'sunu ekler ve kurar
- SeleniumBase + yardimci kutuphaneleri yukler
- Minecraft kullanici adini sorar ve `config/bot_config.json`'a yazar

### Manuel Kurulum

```bash
sudo dnf install python3 python3-pip -y
# Chrome icin Google RPM repo ekle (yukaridaki script otomatik yapar)
pip3 install --user seleniumbase
```

### Baslatma

```bash
python3 main.py                # menu
./baslatma/linux/baslat.sh      # kontrol + baslat (Fedora da ayni baslatici)
```

---

## 5. Windows Kurulumu

### En Kolay Yol: install.cmd (Onekirli)

1. Proje klasorunu Windows'a kopyala.
2. `kurulum\windows\install.cmd` dosyasina **cift tikla**.
3. Sihirbaz sana adim adim yol gosterir:
   - Python yoksa indirme sayfasini otomatik acar
   - Python varsa SeleniumBase'i kurar
   - Minecraft kullanici adini ayarlar
   - Sonunda botu test etmek isteyip istemedigini sorar

Bittiginda her gun oy vermek icin `baslatma\windows\baslat.cmd`'ye cift tik yeterli.

### Manuel Kurulum

```cmd
cd C:\path\to\atlas_vote_bot_merged
python -m pip install seleniumbase
python main.py
```

> **Not:** Windows'ta `python3` yerine `python` kullanilir.
> Bot, tarayici penceresi acarak oy verir — bu normaldir.

---

## 6. Ilk Calistirma ve Test

1. Botu baslat (`python3 main.py` veya `python main.py`).
2. Ana menude **Vote Adi** alaninda oyuncu adinin dogru oldugunu kontrol et.
3. Menu'den **1** ile oy ver → bot tarayiciyi acip sitelere oy verir.
4. Sonuclar `logs/atlas_vote_bot.log` ve `screenshots/` klasorune yazilir.

> Bot, ayni gun icerisinde tekrar calistirilirsa daha once oy verilen
> siteleri **otomatik atlar** (`config/vote_state.json` sayesinde).
> Gunde bir kez oy verilir.

---

## 7. Otomatik Calisma (Zamanlayici)

Bot `--auto` modunu destekler: menu acmadan oy verir, biter, kapanir.

```bash
python3 main.py --auto        # Linux
python main.py --auto         # Windows
```

### Linux — systemd (her gun 09:00 + acilista)

```bash
# Ubuntu / Debian
sudo ./kurulum/linux/setup_systemd.sh

# Fedora
sudo ./kurulum/fedora/setup_systemd.sh
```

Kontrol:
```bash
systemctl status atlas-vote-bot.timer
journalctl -u atlas-vote-bot.service -n 30
```

### Linux — Cron (her gun 09:00)

```bash
# Ubuntu / Debian
./kurulum/linux/setup_cron.sh

# Fedora
./kurulum/fedora/setup_cron.sh
```

### Windows — Gorev Zamanlayici

`kurulum\windows\setup_windows_zamanlayici.cmd` dosyasina **cift tikla**:
```cmd
kurulum\windows\setup_windows_zamanlayici.cmd
```

Iki gorev olusturur:
- `AtlasoyuncuG233VoteBotGunluk` → her gun 09:00
- `AtlasoyuncuG233VoteBotAcilis` → Windows acildiginda

Kontrol / silme:
```cmd
schtasks /Query /TN AtlasoyuncuG233VoteBotGunluk
schtasks /Delete /F /TN AtlasoyuncuG233VoteBotGunluk
schtasks /Delete /F /TN AtlasoyuncuG233VoteBotAcilis
```

---

## 8. Captcha (reCAPTCHA) Ayarlama

reCAPTCHA'li siteler icin 2captcha veya Anti-Captcha kullan:

1. Menu'den `4` → `4` ile servisi sec (`2captcha` / `anticaptcha`)
2. Menu'den `4` → `5` ile API anahtarini gir

| Servis | Web sitesi |
|---|---|
| 2captcha | https://2captcha.com |
| Anti-Captcha | https://anti-captcha.com |

Servis acikken bot, sayfada reCAPTCHA/Turnstile gorurse otomatik cozer
ve token'i enjekte eder.

---

## 9. Sorun Giderme

### `python` veya `python3` bulunamadi
- **Windows:** Python'u PATH'e ekleyerek yeniden kur.
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip -y`
- **Fedora:** `sudo dnf install python3 python3-pip -y`

### `ModuleNotFoundError: No module named 'seleniumbase'`
```bash
pip3 install --user seleniumbase    # Linux
python -m pip install seleniumbase   # Windows
```

### Chrome bulunamadi
- **Ubuntu/Debian:** `sudo apt install google-chrome-stable`
- **Fedora:** `sudo dnf install google-chrome-stable`
- **Windows:** Chrome/Edge kur.

### Cloudflare'de takili kaliyor
- Ayarlar → Headless **kapali** (`False`) olsun.
- `config/vote_sites.json` icinde o sitenin `reconnect` degerini **20+** yap.
- `gui_captcha: true` yap.

### reCAPTCHA engeli
Captcha servisi kur (Bolum 8).

### Bugun oy verilmis, bot atliyor
Normaldir. Sifirlamak icin:
```bash
rm config/vote_state.json
```

### Ekransiz Linux sunucusu (GUI yok)
```bash
sudo apt install xvfb -y
xvfb-run python3 main.py --auto
```

---

*Atlasoyuncu G233 Vote v2.0 — kurulum sonrasi kullanim icin `KULLANIM_KILAVUZU.md`'ye bak.*
