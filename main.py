#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
r"""
  ____ _  __ ___ _  ___    _   _  ____ ___ _____ _   _  ____
 / ___| |/ /_ _| \ | \ \  / \ | |/ ___|_ _|_   _| | | |  _ \
| |  _| ' / | ||  \| |\ \/ /  \| | |  _ | |  | | | |_| | |_) |
| |_| | . \ | || |\  | \  /  |\  | |_| || |  | | |  _  |  __/
 \____|_|\_\___|_| \_|  \/   |_| |_|\___|___| |_| |_| |_|_|
  G233 VOTİNG  -  Minecraft Vote Bot (v2.0)
  Kullanım: python3 main.py
  © 2026 G233 VOTİNG - Atlasoyuncu Vote Bot - projeyi değiştirirken bu isim üzerinde kal.
"""

import sys
import time
import random
from pathlib import Path

# Proje kök dizinini Python path'e ekle
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from config.config_manager import ConfigManager
from utils.logger import setup_logger, get_logger
from modules.menu import (
    draw_main_menu, draw_vote_session_header, draw_sites_menu,
    flow_add_site, flow_edit_site, flow_delete_site, flow_toggle_site,
    flow_settings, draw_logs,
    prompt, info, warn, error, pause, confirm, C
)

# ─── Başlatma ─────────────────────────────────────────────────────────────────

cfg = ConfigManager()
setup_logger(cfg.get("log_file"))
logger = get_logger()

# ─── Atlasoyuncu G233 Vote banner ───────────────────────────────────────────────────────

BANNER = r"""
  ____ _  __ ___ _  ___    _   _  ____ ___ _____ _   _  ____
 / ___| |/ /_ _| \ | \ \  / \ | |/ ___|_ _|_   _| | | |  _ \
| |  _| ' / | ||  \| |\ \/ /  \| | |  _ | |  | | | |_| | |_) |
| |_| | . \ | || |\  | \  /  |\  | |_| || |  | | |  _  |  __/
 \____|_|\_\___|_| \_|  \/   |_| |_|\___|___| |_| |_| |_|_|
        G233 VOTİNG  -  Minecraft Vote Bot v2.0
"""

def draw_banner():
    print(f"{C.CYAN}{BANNER}{C.RESET}")
    print(f"{C.GRAY}  © 2026 G233 VOTİNG | Atlas Vote Bot | İyi oylar! 🎮{C.RESET}")


# ─── Bot çalıştırma ───────────────────────────────────────────────────────────

def run_vote_session(cfg: ConfigManager, auto: bool = False) -> str:
    """Oy oturumunu yürütür. Döndürdüğü string ana menüde gösterilir."""
    from modules.vote_engine import get_voter

    draw_vote_session_header(cfg)

    active_sites = cfg.get_active_sites()
    if not active_sites:
        warn("Aktif site yok. Önce site ekle.")
        if not auto:
            pause()
        return "Hazır"

    sites_to_vote = {k: v for k, v in active_sites.items() if cfg.can_vote(k)}

    if not sites_to_vote:
        info("Tüm siteler için bugün zaten oy verilmiş.")
        logger.info("⏭️  Bugün tüm siteler için oy verilmiş, atlanıyor.")
        if not auto:
            pause()
        return "Tamamlandı"

    logger.info("=" * 60)
    logger.info(f"👤 Vote adı: {cfg.get_vote_username()}")
    logger.info(f"📅 Tarih: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    print(f"\n{C.YELLOW}  🔧 Oy verici seçiliyor...{C.RESET}")
    voter = get_voter(cfg)

    if voter is None:
        error("Hiçbir kütüphane yüklü değil!")
        error("Kurulum: pip install seleniumbase nodriver cloudscraper")
        logger.error("❌ Oy verici kütüphanesi bulunamadı.")
        if not auto:
            pause()
        return "Hata - Kütüphane eksik"

    results = {}
    keys    = list(sites_to_vote.keys())

    for i, (site_key, site_cfg_data) in enumerate(sites_to_vote.items()):
        print()
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 [{site_key}] İşlem başlatılıyor...")
        logger.info(f"{'='*60}")

        try:
            result = voter.vote(site_key, site_cfg_data)
        except Exception as e:
            logger.error(f"❌ [{site_key}] Beklenmeyen hata: {e}")
            result = {"success": False, "already_voted": False, "message": str(e)}

        results[site_key] = result

        if result["success"]:
            cfg.mark_voted(site_key)

        # Siteler arası bekleme
        if i < len(keys) - 1:
            delay = random.uniform(
                cfg.get("site_delay_min", 8),
                cfg.get("site_delay_max", 20)
            )
            logger.info(f"\n⏳ Sonraki site için {delay:.1f}s bekleniyor...")
            time.sleep(delay)

    # Sonuç raporu
    print()

    if not auto:
        # Kullanıcı onayı olmadan sonuç raporunu yazdırma
        # (raporu göstermeden önce sor)
        print(f"{C.YELLOW}  ---- OY OTURUMU TAMAMLANDI ----{C.RESET}")
        if confirm(f"Sonuç raporunu göstermek istiyor musun?"):
            show_report = True
        else:
            show_report = False
            logger.info("Kullanıcı sonuç raporunu görmeyi atladı.")
    else:
        show_report = True

    if show_report:
        print()
        logger.info("\n" + "=" * 60)
        logger.info("📊 SONUÇ RAPORU")
        logger.info("=" * 60)

        all_ok = True
        for sk, res in results.items():
            display = cfg.get_site(sk)
            name    = display["display_name"] if display else sk
            icon    = "✅" if res["success"] else "❌"
            logger.info(f"{icon} {name:30s} | {res['message']}")
            if not res["success"]:
                all_ok = False

        logger.info("=" * 60)

        if all_ok:
            logger.info("🏆 Tüm oylamalar tamamlandı!")
            status = "Tamamlandı ✅"
        else:
            logger.info("⚠️  Bazı oylamalar başarısız.")
            status = "Kısmen Başarılı ⚠️"
    else:
        # Rapor atlanınca yine de durum özeti (log'a)
        all_ok = all(r["success"] for r in results.values())
        status = "Tamamlandı ✅" if all_ok else "Kısmen Başarılı ⚠️"
        logger.info("Sonuç raporu atlandı. Durum: " + status)

    if not auto:
        pause("Ana menüye dönmek için Enter...")
    return status


# ─── Site yönetim döngüsü ─────────────────────────────────────────────────────

def sites_menu_loop(cfg: ConfigManager):
    while True:
        draw_sites_menu(cfg)
        choice = prompt("Seçim: ").lower()

        if choice == "e":
            flow_add_site(cfg)
        elif choice == "d":
            flow_edit_site(cfg)
        elif choice == "s":
            flow_delete_site(cfg)
        elif choice == "t":
            flow_toggle_site(cfg)
        elif choice == "0":
            break
        else:
            warn("Geçersiz seçim.")
            pause()


# ─── Ana döngü ────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Atlasoyuncu G233 Vote - Minecraft Vote Bot")
    parser.add_argument("--auto", action="store_true",
                        help="Menüyü açmadan direkt oy oturumunu çalıştır ve kapat (cron/systemd için)")
    args = parser.parse_args()

    status = "Hazır"

    draw_banner()

    logger.info("=" * 60)
    logger.info("🚀 Atlasoyuncu G233 Vote - Minecraft Vote Bot v2.0 başlatıldı")
    logger.info(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    if args.auto:
        status = run_vote_session(cfg, auto=True)
        logger.info(f"🏁 Otomatik mod sonucu: {status}")
        sys.exit(0)

    while True:
        draw_main_menu(cfg, status)
        choice = prompt("Seçim: ")

        if choice == "1":
            # ─── Botu Başlat ────────────────────────────────────────────
            status = "Çalışıyor..."
            try:
                status = run_vote_session(cfg)
            except KeyboardInterrupt:
                logger.warning("⛔ Kullanıcı tarafından durduruldu.")
                status = "Durduruldu"
            except Exception as e:
                logger.error(f"❌ Beklenmeyen hata: {e}")
                status = f"Hata"

        elif choice == "2":
            # ─── Vote Oyuncu Adını Değiştir ─────────────────────────────
            print(f"\n  Mevcut vote adı: {C.WHITE}{cfg.get_vote_username()}{C.RESET}")
            new_vote = prompt("Yeni vote oyuncu adı (boş=iptal): ")
            if new_vote:
                cfg.set_vote_username(new_vote)
                info(f"Vote adı güncellendi: {new_vote}")
                logger.info(f"✏️  Vote oyuncu adı değiştirildi: {new_vote}")
            else:
                warn("İptal edildi.")
            pause()

        elif choice == "3":
            # ─── Vote Sitelerini Yönet ───────────────────────────────────
            sites_menu_loop(cfg)

        elif choice == "4":
            # ─── Ayarlar ────────────────────────────────────────────────
            flow_settings(cfg)

        elif choice == "5":
            # ─── Logları Gör ─────────────────────────────────────────────
            draw_logs(cfg, last_n=50)

        elif choice == "0":
            # ─── Çıkış ───────────────────────────────────────────────────
            if confirm("Çıkmak istediğine emin misin?"):
                print(f"\n  {C.CYAN}Atlasoyuncu G233 Vote - İyi oyunlar! 🎮{C.RESET}\n")
                logger.info("👋 Bot kapatıldı.")
                sys.exit(0)

        else:
            warn("Geçersiz seçim, tekrar dene.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}Ctrl+C ile çıkıldı.{C.RESET}\n")
        sys.exit(0)
