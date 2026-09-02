# 🎮 Atlasoyuncu G233 Vote — Minecraft Vote Bot Kullanım Kılavuzu

> Atlasoyuncu G233 Vote, Minecraft sunucunuz için oy (vote) sitelerine otomatik oy veren,
> Cloudflare engelini aşan ve isterseniz captcha'yı otomatik çözen terminal tabanlı bir bottur.

---

## 📋 İçindekiler

1. [Gereksinimler](#1-gereksinimler)
2. [Kurulum](#2-kurulum)
3. [Botu Başlatma](#3-botu-başlatma)
4. [Ana Menü Kullanımı](#4-ana-menü-kullanımı)
5. [Vote Oyuncu Adını Ayarlama](#5-vote-oyuncu-adını-ayarlama)
6. [Vote Sitesi Ekleme ve Yönetme](#6-vote-sitesi-ekleme-ve-yönetme)
7. [Captcha (reCAPTCHA) Otomatik Çözme](#7-captcha-recaptcha-otomatik-çözme)
8. [Otomatik Çalışma (Zamanlayıcı + Açılışta)](#8-otomatik-çalışma-zamanlayıcı--açılışta)
9. [Dosya Yapısı](#9-dosya-yapısı)
10. [Sık Karşılaşılan Sorunlar](#10-sık-karşılaşılan-sorunlar)
11. [Marka ve Paylaşım](#11-marka-ve-paylaşım)

---

## 1. Gereksinimler

| Gereksinim | Minimum | Kontrol |
|---|---|---|
| Python | 3.8+ | `python3 --version` |
| pip | herhangi | `pip3 --version` |
| Google Chrome / Chromium | herhangi | `google-chrome --version` |
| SeleniumBase | 4.x | `pip3 install seleniumbase` |
| RAM | 2 GB | — |

> Bu proje `atlas_vote_bot.py` ve `main.py` olmak üzere iki giriş noktası sunar.
> İkisi de aynıdır (`atlas_vote_bot.py`, `main.py`'ye yönlendirir). `main.py` kullanılır.

---

## 2. Kurulum

Detaylı kurulum için **KURULUM.md**'ye bak. Platforma özel kurulum dosyaları
`kurulum/` klasöründedir:

```bash
# Ubuntu / Debian
chmod +x kurulum/linux/install.sh && ./kurulum/linux/install.sh

# Fedora
chmod +x kurulum/fedora/install.sh && ./kurulum/fedora/install.sh

# Windows: kurulum\windows\install.cmd dosyasına çift tıkla
```

Elle kurulum (zorunlu kütüphane):
```bash
pip3 install seleniumbase
# isteğe bağlı yedek motorlar:
# pip3 install nodriver cloudscraper

# test
python3 -c "import seleniumbase; print('OK ✅')"
```

---

## 3. Botu Başlatma

```bash
python3 main.py            # menülü kullanım
# veya
./baslatma/linux/baslat.sh      # Linux (Ubuntu/Debian/Fedora)
baslatma\windows\baslat.cmd     # Windows (çift tık)
```

**Otomatik mod** (menüyü açmadan direkt oy verir, biter, kapanır):
```bash
python3 main.py --auto
```

---

## 4. Ana Menü Kullanımı

| Tuş | Ne Yapar |
|---|---|
| `1` | Botu çalıştırır, tüm aktif sitelere oy verir |
| `2` | Vote oyuncu adını değiştirir |
| `3` | Vote sitelerini yönet (ekle/düzenle/sil/aktif-pasif) |
| `4` | Ayarlar (headless, proxy, deneme, captcha) |
| `5` | Son log satırlarını gösterir |
| `0` | Çıkış |

---

## 5. Vote Oyuncu Adını Ayarlama

1. Menüden `2` → yeni oyuncu adını yaz
2. Veya `config/bot_config.json` içindeki `vote_username` değerini düzenle

Bot, formdaki kullanıcı adı alanını da bulur, tıklar, mevcut değeri kontrol eder:
- Alan **boş** veya **farklı** ise → yeni adı yazar ve oy verir
- Alan **aynı** adla dolu ise → olduğu gibi bırakıp oy verir

Her sitenin username alanı `config/vote_sites.json` içinde `username_input` ile ayarlanır
(ör. `minecraft-mp` → `input[name='nickname']`, `topminecraftservers` → `#username`).
Liste de verilebilir; ilk bulunan kullanılır:
```json
"username_input": ["#username", "input[name='mc_username']"]
```

---

## 6. Vote Sitesi Ekleme ve Yönetme

Menüden `3` ile site ekle/düzenle/sil/aktif-pasif yapabilirsin.

Her site `config/vote_sites.json` içinde saklanır. Gelişmiş ayarlar:

```json
{
  "site-adi": {
    "name": "site-adi",
    "display_name": "Görünen Ad",
    "url": "https://ornek.com/vote",
    "method": "seleniumbase",
    "username_param": "username",      // URL'ye ?username= eklenir (varsa)
    "username_input": "input[name='nickname']",  // form alanı selector'ı (string veya liste)
    "checkbox_selectors": ["input[name='accept']"],
    "vote_selectors": ["//button[contains(text(),'Vote')]"],
    "gui_captcha": false,              // GUI mouse tıklaması yapmasın
    "reconnect": 20,                   // Cloudflare bekleme (sn), ağır sitelerde artır
    "captcha_sitekey": "",             // captcha varsa sitekey (opsiyonel)
    "active": true
  }
}
```

> `gui_captcha: false` yapmak, botun pencerede mouse'u oynatmasını engeller
> (minecraft-mp.com bunu kullanır). Cloudflare "Just a moment" gösteren ağır
> sitelerde `reconnect` değerini 20+ yap ve `gui_captcha: true` bırak.

---

## 7. Captcha (reCAPTCHA) Otomatik Çözme

reCAPTCHA'ya sahip siteler için 2captcha veya Anti-Captcha servisi kullanılabilir.

1. Menüden `4` → `4` ile servisi seç (`2captcha` veya `anticaptcha`)
2. Menüden `4` → `5` ile API anahtarını gir

| Servis | API Anahtarı |
|---|---|
| 2captcha | https://2captcha.com hesabından alınır |
| Anti-Captcha | https://anti-captcha.com hesabından alınır |

Servis açıkken bot, sayfada reCAPTCHA/Turnstile algılarsa otomatik çözer ve
token'ı forma enjekte eder. `captcha_sitekey` bilinmiyorsa bot sayfadan otomatik bulur.

---

## 8. Otomatik Çalışma (Zamanlayıcı + Açılışta)

Bot `--auto` modunu destekler: menü açmadan oy verir, biter, kapanır. Zamanlayıcılar bunu kullanır.

### Linux — systemd (önerilen: her gün 09:00 + açılışta)

```bash
# Ubuntu / Debian
sudo ./kurulum/linux/setup_systemd.sh

# Fedora
sudo ./kurulum/fedora/setup_systemd.sh
```

- `atlas-vote-bot.timer` → her gün 09:00'da çalıştırır
- `atlas-vote-bot.service` → etkinleştirildiği için **sistem açıldığında** da çalışır

Kontrol:
```bash
systemctl status atlas-vote-bot.timer
journalctl -u atlas-vote-bot.service -n 30
```

### Linux — Cron (her gün 09:00)

```bash
# Ubuntu / Debian
./kurulum/linux/setup_cron.sh

# Fedora
./kurulum/fedora/setup_cron.sh
```

### Windows — Görev Zamanlayıcı

`kurulum\windows\setup_windows_zamanlayici.cmd` dosyasına **çift tıkla** (yönetici olarak):
```cmd
kurulum\windows\setup_windows_zamanlayici.cmd
```
İki görev oluşturur: `AtlasoyuncuG233VoteBotGunluk` (09:00) ve `AtlasoyuncuG233VoteBotAcilis` (oturum açılışta).

Kontrol / silme:
```cmd
schtasks /Query /TN AtlasoyuncuG233VoteBotGunluk
schtasks /Delete /F /TN AtlasoyuncuG233VoteBotGunluk
schtasks /Delete /F /TN AtlasoyuncuG233VoteBotAcilis
```

> Not: `--auto` modu, çalıştırıldığı gün daha önce oy verilmiş siteleri
> otomatik atlar (`config/vote_state.json` sayesinde). Günde bir kez oy verilir.

---

## 9. Dosya Yapısı

```
atlas_vote_bot_merged/
├── main.py                ← Botu buradan başlat
├── atlas_vote_bot.py      ← main.py'ye yönlendiren shim (eski komut desteği)
├── baslatma/              ← başlatma dosyaları (çift tık)
│   ├── linux/             ← baslat.sh + masaüstü kısayolu (çift tık)
│   └── windows/           ← baslat.cmd (çift tık)
├── kurulum/               ← platforma özel kurulum dosyaları
│   ├── linux/            ← Ubuntu / Debian
│   ├── fedora/           ← Fedora
│   └── windows/          ← Windows
├── LICENSE               ← MIT lisans
├── config/
│   ├── bot_config.json   ← genel ayarlar (otomatik)
│   ├── vote_sites.json   ← vote siteleri (otomatik)
│   └── vote_state.json   ← son oy tarihleri (otomatik)
├── modules/
│   ├── vote_engine.py    ← oy verme motoru + captcha çözücü
│   └── menu.py           ← terminal menüsü
├── utils/
│   └── logger.py         ← log sistemi
├── logs/
└── screenshots/
```

---

## 10. Sık Karşılaşılan Sorunlar

### ❌ `Permission denied: '/home/claude'`
Eski makineden kalan bozuk yol. Silip yeniden başlat (ConfigManager yolları otomatik onarır):
```bash
rm config/bot_config.json && python3 main.py
```

### ❌ Chrome bulunamadı
Chrome/Chromium kur: `sudo apt install google-chrome-stable` veya `chromium-browser`.

### ❌ Cloudflare'de takılı kalıyor
- Ayarlar → Headless kapalı (`False`) olsun
- İlgili sitenin `reconnect` değerini 20+ yap (`config/vote_sites.json`)
- `gui_captcha: true` yap (Cloudflare mouse/human kontrolü isteyebilir)

### ❌ reCAPTCHA engeli
Kılavuzun [7. bölümüne](#7-captcha-recaptcha-otomatik-çözme) bak; captcha servisi kur.

### ❌ Bugün oy verilmiş, bot atlıyor
Bu normaldir (günde bir oy). Sıfırlamak için:
```bash
rm config/vote_state.json
```

### ❌ Ekransız sunucu (GUI yok)
```bash
sudo apt install xvfb -y
xvfb-run python3 main.py --auto
```

---

*Atlasoyuncu G233 Vote v2.0 — sorular için sunucu Discord'una gel.*

---

## 11. Marka ve Paylaşım

Bu proje **Atlasoyuncu G233 Vote** markası altında MIT lisansıyla dağıtılır.
Dosyaların başındaki `© 2026 Atlasoyuncu G233 Vote` damgası her dosyada korunmalıdır.

**Projeyi paylaşmadan önce kişisel verileri temizle:**

```bash
# 1. Ekran görüntüleri ve loglar (test verisi içerir)
rm -rf screenshots/* logs/*

# 2. Oy geçmişini sıfırla
echo '{}' > config/vote_state.json

# 3. bot_config.json'daki kişisel bilgileri sil
#    - vote_username: kendi adın yerine "OyuncuAdi"
#    - captcha_api_key: boşalt ("")  ← gizli anahtar paylaşılmaz!
#    - log_file / screenshot_dir: klasör adına çevir (mutlak yol olmasın)
```

> ⚠️ **API anahtarın (`captcha_api_key`) gizlidir.** Projeyi paylaşırken mutlaka boş bırak.
> `config/vote_state.json`, `logs/` ve `screenshots/` `.gitignore`'a eklenmiştir; git'e yüklenmez.