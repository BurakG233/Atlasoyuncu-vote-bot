#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
"""
Terminal Menü Modülü
- Ana menü
- Vote sitesi yönetimi
- Ayarlar
- Log görüntüleyici
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

from config.config_manager import ConfigManager, validate_url
from utils.logger import get_logger

logger = get_logger()

W  = 46   # kutu genişliği (iç)

# ─── Renk kodları ─────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"


def clr():
    os.system("cls" if os.name == "nt" else "clear")


def _box_line(content: str = "", fill: str = " ") -> str:
    """İçerik metni verilen bir kutu satırı döndürür."""
    visible = _strip_ansi(content)
    pad = W - len(visible)
    if pad < 0:
        pad = 0
    return f"║ {content}{fill * pad} ║"


def _strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _hr(char: str = "═") -> str:
    return "╠" + char * (W + 2) + "╣"


def _top() -> str:
    return "╔" + "═" * (W + 2) + "╗"


def _bot() -> str:
    return "╚" + "═" * (W + 2) + "╝"


def _blank() -> str:
    return _box_line()


# ─── Ana menü ─────────────────────────────────────────────────────────────────

def draw_main_menu(cfg: ConfigManager, status: str = "Hazır") -> None:
    clr()
    sites        = cfg.get_sites()
    active_sites = cfg.get_active_sites()
    vote_user    = cfg.get_vote_username()
    bot_name     = cfg.get_bot_name()

    # Durum rengi
    if status == "Hazır":
        status_str = f"{C.GREEN}{status}{C.RESET}"
    elif "Hata" in status or "Başarısız" in status:
        status_str = f"{C.RED}{status}{C.RESET}"
    elif "Çalışıyor" in status or "Bağlan" in status:
        status_str = f"{C.YELLOW}{status}{C.RESET}"
    else:
        status_str = f"{C.CYAN}{status}{C.RESET}"

    lines = [
        _top(),
        _box_line(f"{C.BOLD}{C.GREEN}  ██╗  ██╗ ██████╗ ██████║ ██████║ {C.RESET}"),
        _box_line(f"{C.BOLD}{C.GREEN}  ██║  ██║██╔════╝ ╚════██╗██╔═████╗{C.RESET}"),
        _box_line(f"{C.BOLD}{C.GREEN}  ███████║██║  ███╗ █████╔╝██║██╔██║{C.RESET}"),
        _box_line(f"{C.BOLD}{C.GREEN}  ██╔══██║██║   ██║ ╚═══██╗████╔╝██║{C.RESET}"),
        _box_line(f"{C.BOLD}{C.GREEN}  ██║  ██║╚██████╔╝██████╔╝╚██████╔╝{C.RESET}"),
        _box_line(f"{C.BOLD}{C.GREEN}  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ {C.RESET}"),
        _box_line(f"{C.BOLD}{C.CYAN}   G233 VOTİNG • MINECRAFT VOTE BOT{C.RESET}"),
        _box_line(f"{C.BOLD}{C.CYAN}        v2.0  © 2026 G233 VOTİNG{C.RESET}"),
        _hr(),
        _box_line(f"{C.GRAY}Bot Adı     :{C.RESET} {C.WHITE}{bot_name}{C.RESET}"),
        _box_line(f"{C.GRAY}Vote Adı    :{C.RESET} {C.WHITE}{vote_user}{C.RESET}"),
        _box_line(f"{C.GRAY}Siteler     :{C.RESET} {C.WHITE}{len(active_sites)}/{len(sites)} aktif{C.RESET}"),
        _box_line(f"{C.GRAY}Durum       :{C.RESET} {status_str}"),
        _hr(),
        _box_line(f"  {C.GREEN}[1]{C.RESET} Botu Başlat"),
        _box_line(f"  {C.CYAN}[2]{C.RESET} Vote Oyuncu Adını Değiştir"),
        _box_line(f"  {C.CYAN}[3]{C.RESET} Vote Sitelerini Yönet"),
        _box_line(f"  {C.CYAN}[4]{C.RESET} Ayarlar"),
        _box_line(f"  {C.CYAN}[5]{C.RESET} Logları Gör"),
        _box_line(f"  {C.RED}[0]{C.RESET} Çıkış"),
        _bot(),
        _box_line(f"{C.GRAY}  © 2026 G233 VOTİNG - Atlas Vote Bot | İyi oylar! 🎮{C.RESET}"),
        _bot(),
    ]
    print("\n".join(lines))
    print()


# ─── Bot başlatma ekranı ──────────────────────────────────────────────────────

def draw_vote_session_header(cfg: ConfigManager) -> None:
    sites   = cfg.get_active_sites()
    clr()
    print(_top())
    print(_box_line(f"{C.BOLD}{C.CYAN}   🗳️  OY OTURUMU BAŞLATILIYOR   {C.RESET}"))
    print(_hr())
    print(_box_line(f"{C.GRAY}Vote Adı : {C.RESET}{C.WHITE}{cfg.get_vote_username()}{C.RESET}"))
    print(_box_line(f"{C.GRAY}Tarih    : {C.RESET}{C.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M')}{C.RESET}"))
    print(_hr())
    for k, s in sites.items():
        last = cfg.get_last_vote(k)
        can  = cfg.can_vote(k)
        icon = f"{C.GREEN}🗳 {C.RESET}" if can else f"{C.YELLOW}⏭ {C.RESET}"
        print(_box_line(f"{icon}{s['display_name'][:28]}"))
        if not can:
            print(_box_line(f"   {C.GRAY}Son oy: {last}{C.RESET}"))
    print(_bot())
    print()


# ─── Site listesi ─────────────────────────────────────────────────────────────

def draw_sites_menu(cfg: ConfigManager) -> None:
    sites = cfg.get_sites()
    clr()
    print(_top())
    print(_box_line(f"{C.BOLD}{C.CYAN}      VOTE SİTELERİ YÖNETİMİ{C.RESET}"))
    print(_hr())

    if not sites:
        print(_box_line(f"  {C.GRAY}Henüz site eklenmemiş.{C.RESET}"))
    else:
        for i, (k, s) in enumerate(sites.items(), 1):
            active_str = f"{C.GREEN}AKTİF{C.RESET}" if s.get("active") else f"{C.RED}PASİF{C.RESET}"
            name       = s["display_name"][:24]
            print(_box_line(f"  {C.WHITE}[{i}]{C.RESET} {name:<24} {active_str}"))

    print(_hr())
    print(_box_line(f"  {C.GREEN}[E]{C.RESET} Yeni Site Ekle"))
    print(_box_line(f"  {C.CYAN}[D]{C.RESET} Site Düzenle"))
    print(_box_line(f"  {C.RED}[S]{C.RESET} Site Sil"))
    print(_box_line(f"  {C.YELLOW}[T]{C.RESET} Aktif/Pasif Değiştir"))
    print(_box_line(f"  {C.GRAY}[0]{C.RESET} Ana Menüye Dön"))
    print(_bot())
    print()


# ─── Ayarlar menüsü ───────────────────────────────────────────────────────────

def draw_settings_menu(cfg: ConfigManager) -> None:
    clr()
    print(_top())
    print(_box_line(f"{C.BOLD}{C.CYAN}            AYARLAR{C.RESET}"))
    print(_hr())
    print(_box_line(f"{C.GRAY}Headless modu  :{C.RESET} {cfg.get('headless')}"))
    print(_box_line(f"{C.GRAY}Proxy          :{C.RESET} {cfg.get('proxy') or 'Yok'}"))
    print(_box_line(f"{C.GRAY}Deneme sayısı  :{C.RESET} {cfg.get('retry_count')}"))
    print(_box_line(f"{C.GRAY}Deneme aralığı :{C.RESET} {cfg.get('retry_delay')}s"))
    print(_box_line(f"{C.GRAY}Siteler arası  :{C.RESET} {cfg.get('site_delay_min')}-{cfg.get('site_delay_max')}s"))
    print(_box_line(f"{C.GRAY}Captcha servisi :{C.RESET} {cfg.get('captcha_service', 'none')}"))
    print(_box_line(f"{C.GRAY}Captcha API key :{C.RESET} {cfg.get('captcha_api_key') or 'Yok'}"))
    print(_hr())
    print(_box_line(f"  {C.CYAN}[1]{C.RESET} Headless Modu Değiştir"))
    print(_box_line(f"  {C.CYAN}[2]{C.RESET} Proxy Ayarla"))
    print(_box_line(f"  {C.CYAN}[3]{C.RESET} Deneme Sayısı Ayarla"))
    print(_box_line(f"  {C.CYAN}[4]{C.RESET} Captcha Servisi (none/2captcha/anticaptcha)"))
    print(_box_line(f"  {C.CYAN}[5]{C.RESET} Captcha API Anahtarı"))
    print(_box_line(f"  {C.GRAY}[0]{C.RESET} Ana Menüye Dön"))
    print(_bot())
    print()


# ─── Log görüntüleyici ────────────────────────────────────────────────────────

def draw_logs(cfg: ConfigManager, last_n: int = 40) -> None:
    log_file = Path(cfg.get("log_file", "logs/atlas_vote_bot.log"))
    clr()
    print(_top())
    print(_box_line(f"{C.BOLD}{C.CYAN}          SON {last_n} LOG SATIRI{C.RESET}"))
    print(_bot())

    if not log_file.exists():
        print(f"\n{C.YELLOW}  Log dosyası bulunamadı: {log_file}{C.RESET}\n")
    else:
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-last_n:]:
            # Renklendir
            if "[ERROR]" in line:
                print(f"  {C.RED}{line}{C.RESET}")
            elif "[WARNING]" in line:
                print(f"  {C.YELLOW}{line}{C.RESET}")
            elif "✅" in line or "başarı" in line.lower():
                print(f"  {C.GREEN}{line}{C.RESET}")
            else:
                print(f"  {C.GRAY}{line}{C.RESET}")

    print(f"\n{C.GRAY}Log dosyası: {log_file.absolute()}{C.RESET}")
    input(f"\n{C.CYAN}  Ana menüye dönmek için Enter'a bas...{C.RESET}")


# ─── Kullanıcı girişi yardımcıları ───────────────────────────────────────────

def prompt(msg: str, color: str = C.CYAN) -> str:
    try:
        return input(f"{color}  {msg}{C.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return ""


def confirm(msg: str) -> bool:
    ans = prompt(f"{msg} [e/h]: ", C.YELLOW).lower()
    return ans in ("e", "evet", "y", "yes")


def pause(msg: str = "Devam etmek için Enter'a bas..."):
    input(f"\n{C.CYAN}  {msg}{C.RESET}")


def info(msg: str):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")


def warn(msg: str):
    print(f"  {C.YELLOW}⚠️  {msg}{C.RESET}")


def error(msg: str):
    print(f"  {C.RED}❌ {msg}{C.RESET}")


# ─── Site yönetim akışları ────────────────────────────────────────────────────

def _site_key_from_index(cfg: ConfigManager, idx: int):
    sites = cfg.get_sites()
    keys  = list(sites.keys())
    if 1 <= idx <= len(keys):
        return keys[idx - 1], sites[keys[idx - 1]]
    return None, None


def flow_add_site(cfg: ConfigManager):
    print(f"\n{C.BOLD}  — Yeni Vote Sitesi Ekle —{C.RESET}\n")
    display = prompt("Site adı (görünen): ")
    if not display:
        error("Site adı boş olamaz.")
        pause()
        return

    url = prompt("Vote URL'si: ")
    if not validate_url(url):
        error("Geçersiz URL formatı. http:// veya https:// ile başlamalı.")
        pause()
        return

    has_param = confirm("URL'ye oyuncu adı parametre olarak eklenecek mi?")
    param = None
    if has_param:
        param = prompt("Parametre adı (örn: username): ") or "username"

    # Key = display adından türet (küçük harf, boşluğu tire)
    key = re.sub(r'[^a-z0-9\-]', '', display.lower().replace(" ", "-"))
    if not key:
        key = f"site_{len(cfg.get_sites())+1}"

    if key in cfg.get_sites():
        key = key + f"_{len(cfg.get_sites())+1}"

    ok = cfg.add_site(key, display, url, param)
    if ok:
        info(f"'{display}' başarıyla eklendi.")
        logger.info(f"🆕 Yeni site eklendi: {display} → {url}")
    else:
        error("Site eklenemedi.")
    pause()


def flow_edit_site(cfg: ConfigManager):
    sites = cfg.get_sites()
    if not sites:
        warn("Düzenlenecek site yok.")
        pause()
        return

    print(f"\n{C.BOLD}  — Site Düzenle —{C.RESET}")
    for i, (k, s) in enumerate(sites.items(), 1):
        print(f"  {C.WHITE}[{i}]{C.RESET} {s['display_name']}")
    print()

    try:
        idx = int(prompt("Düzenlenecek site numarası (0=iptal): "))
    except ValueError:
        return

    key, site = _site_key_from_index(cfg, idx)
    if not key:
        warn("Geçersiz seçim.")
        pause()
        return

    print(f"\n  Mevcut ad : {site['display_name']}")
    new_name = prompt("Yeni ad (boş bırak = değiştirme): ")
    print(f"  Mevcut URL: {site['url']}")
    new_url  = prompt("Yeni URL (boş bırak = değiştirme): ")
    print(f"  Mevcut param: {site.get('username_param')}")
    new_param = prompt("Yeni param adı (boş=yok, '-'=sil): ")

    kwargs = {}
    if new_name:
        kwargs["display_name"] = new_name
    if new_url:
        if not validate_url(new_url):
            error("Geçersiz URL.")
            pause()
            return
        kwargs["url"] = new_url
    if new_param == "-":
        kwargs["username_param"] = ""
    elif new_param:
        kwargs["username_param"] = new_param

    ok = cfg.edit_site(key, **kwargs)
    if ok:
        info("Site güncellendi.")
        logger.info(f"✏️  Site düzenlendi: {key}")
    else:
        error("Güncellenemedi.")
    pause()


def flow_delete_site(cfg: ConfigManager):
    sites = cfg.get_sites()
    if not sites:
        warn("Silinecek site yok.")
        pause()
        return

    print(f"\n{C.BOLD}  — Site Sil —{C.RESET}")
    for i, (k, s) in enumerate(sites.items(), 1):
        print(f"  {C.WHITE}[{i}]{C.RESET} {s['display_name']}")
    print()

    try:
        idx = int(prompt("Silinecek site numarası (0=iptal): "))
    except ValueError:
        return

    key, site = _site_key_from_index(cfg, idx)
    if not key:
        return

    if confirm(f"'{site['display_name']}' silinsin mi?"):
        cfg.remove_site(key)
        info("Site silindi.")
        logger.info(f"🗑️  Site silindi: {key}")
    pause()


def flow_toggle_site(cfg: ConfigManager):
    sites = cfg.get_sites()
    if not sites:
        warn("Site yok.")
        pause()
        return

    print(f"\n{C.BOLD}  — Aktif/Pasif Değiştir —{C.RESET}")
    for i, (k, s) in enumerate(sites.items(), 1):
        st = f"{C.GREEN}AKTİF{C.RESET}" if s.get("active") else f"{C.RED}PASİF{C.RESET}"
        print(f"  {C.WHITE}[{i}]{C.RESET} {s['display_name']:<28} {st}")
    print()

    try:
        idx = int(prompt("Site numarası (0=iptal): "))
    except ValueError:
        return

    key, site = _site_key_from_index(cfg, idx)
    if not key:
        return

    new_state = cfg.toggle_site(key)
    state_str = "AKTİF" if new_state else "PASİF"
    info(f"'{site['display_name']}' artık {state_str}.")
    logger.info(f"🔀 Site durumu değişti: {key} → {state_str}")
    pause()


# ─── Ayar akışları ────────────────────────────────────────────────────────────

def flow_settings(cfg: ConfigManager):
    while True:
        draw_settings_menu(cfg)
        choice = prompt("Seçim: ")

        if choice == "1":
            current = cfg.get("headless", False)
            cfg.set("headless", not current)
            info(f"Headless modu: {not current}")
            pause()

        elif choice == "2":
            p = prompt("Proxy (boş=kaldır, örn: http://user:pass@host:port): ")
            cfg.set("proxy", p if p else None)
            info("Proxy güncellendi.")
            pause()

        elif choice == "3":
            try:
                n = int(prompt("Deneme sayısı (1-10): "))
                if 1 <= n <= 10:
                    cfg.set("retry_count", n)
                    info(f"Deneme sayısı: {n}")
                else:
                    error("1-10 arasında olmalı.")
            except ValueError:
                error("Geçersiz sayı.")
            pause()

        elif choice == "4":
            print(f"\n  Mevcut: {C.WHITE}{cfg.get('captcha_service', 'none')}{C.RESET}")
            svc = prompt("Captcha servisi (none/2captcha/anticaptcha, boş=iptal): ").lower()
            if svc in ("none", "2captcha", "anticaptcha"):
                cfg.set("captcha_service", svc)
                info(f"Captcha servisi: {svc}")
            else:
                error("Geçersiz servis.")
            pause()

        elif choice == "5":
            print(f"\n  Mevcut: {C.WHITE}{cfg.get('captcha_api_key') or 'Yok'}{C.RESET}")
            key = prompt("2captcha/anticaptcha API anahtarı (boş=kaldır): ").strip()
            cfg.set("captcha_api_key", key if key else "")
            info("Captcha API anahtarı güncellendi.")
            pause()

        elif choice == "0":
            break
