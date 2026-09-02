#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
"""
Config Manager - Tüm kalıcı ayarları yönetir.
vote_sites.json ve bot_config.json dosyalarını okur/yazar.
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

CONFIG_FILE = BASE_DIR / "config" / "bot_config.json"
SITES_FILE  = BASE_DIR / "config" / "vote_sites.json"
STATE_FILE  = BASE_DIR / "config" / "vote_state.json"

# ─── Varsayılan değerler ──────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "bot_name":       "AtlasoyuncuG233VoteBot",
    "vote_username":  "BurakG233",
    "headless":       False,
    "proxy":          None,
    "retry_count":    3,
    "retry_delay":    30,
    "site_delay_min": 8,
    "site_delay_max": 20,
    "seleniumbase_reconnect": 6,
    "seleniumbase_timeout":   90,
    "captcha_service":       "none",      # none | 2captcha | anticaptcha
    "captcha_api_key":       "",
    "captcha_timeout":       180,         # çözüm için max bekleme (sn)
    "log_file":        str(BASE_DIR / "logs" / "atlas_vote_bot.log"),
    "screenshot_dir":  str(BASE_DIR / "screenshots"),
}

DEFAULT_SITES = {
    "minecraft-mp": {
        "name":           "minecraft-mp",
        "display_name":   "Minecraft-MP.com",
        "url":            "https://minecraft-mp.com/server/319522/vote/",
        "method":         "seleniumbase",
        "username_param": "username",
        "username_input": "input[name='nickname']",
        "checkbox_selectors": ["input[name='accept']"],
        "vote_selectors": ["//button[contains(text(),'Vote')]"],
        "gui_captcha":    False,
        "active":         True,
        "added":          "2026-08-08"
    },
    "topminecraftservers": {
        "name":           "topminecraftservers",
        "display_name":   "TopMinecraftServers.org",
        "url":            "https://topminecraftservers.org/vote/11861",
        "method":         "seleniumbase",
        "username_param": None,
        "username_input": ["#username", "input[name='mc_username']"],
        "reconnect":      20,
        "gui_captcha":    True,
        "active":         True,
        "added":          "2026-08-08"
    }
}

# ─── Yardımcı fonksiyonlar ────────────────────────────────────────────────────

def _load_json(path: Path, default: dict) -> dict:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return dict(default)
    return dict(default)


def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_url(url: str) -> bool:
    pattern = re.compile(r'^https?://.+\..+')
    return bool(pattern.match(url.strip()))

# ─── Ana API ─────────────────────────────────────────────────────────────────

class ConfigManager:
    """Tüm bot ayarlarını yöneten tekil nesne."""

    def __init__(self):
        self._cfg   = _load_json(CONFIG_FILE, DEFAULT_CONFIG)
        self._sites = _load_json(SITES_FILE,  DEFAULT_SITES)
        self._state = _load_json(STATE_FILE,  {})

        # Eksik varsayılanları tamamla
        for k, v in DEFAULT_CONFIG.items():
            self._cfg.setdefault(k, v)

        # Yol onarımı: log_file ve screenshot_dir bu projenin dışına
        # işaret ediyorsa (örn. eski makineden kalan /home/claude/...)
        # proje klasörüne geri çek. Böylece PermissionError oluşmaz.
        for key, default in (("log_file", "logs/atlas_vote_bot.log"),
                             ("screenshot_dir", "screenshots")):
            val = self._cfg.get(key)
            if not val or not str(val).startswith(str(BASE_DIR)):
                self._cfg[key] = str(BASE_DIR / default)

        # Mevcut vote_state.json'u taşı (eski tek dosyalı sistemden)
        legacy = BASE_DIR / "vote_state.json"
        if legacy.exists() and not STATE_FILE.exists():
            try:
                with open(legacy) as f:
                    self._state = json.load(f)
                _save_json(STATE_FILE, self._state)
            except Exception:
                pass

        self._save_config()
        self._save_sites()

    # ── Config (genel ayarlar) ────────────────────────────────────────────

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        self._save_config()

    def get_vote_username(self) -> str:
        return self._cfg.get("vote_username", "")

    def set_vote_username(self, name: str):
        self._cfg["vote_username"] = name.strip()
        self._save_config()

    def get_bot_name(self) -> str:
        return self._cfg.get("bot_name", "AtlasoyuncuG233VoteBot")

    def set_bot_name(self, name: str):
        self._cfg["bot_name"] = name.strip()
        self._save_config()

    def _save_config(self):
        _save_json(CONFIG_FILE, self._cfg)

    # ── Vote siteleri ─────────────────────────────────────────────────────

    def get_sites(self) -> dict:
        return dict(self._sites)

    def get_active_sites(self) -> dict:
        return {k: v for k, v in self._sites.items() if v.get("active", True)}

    def get_site(self, key: str) -> dict | None:
        return self._sites.get(key)

    def add_site(self, key: str, display_name: str, url: str,
                 username_param: str | None = None) -> bool:
        if not validate_url(url):
            return False
        self._sites[key] = {
            "name":           key,
            "display_name":   display_name,
            "url":            url.strip(),
            "method":         "seleniumbase",
            "username_param": username_param if username_param else None,
            "active":         True,
            "added":          datetime.now().strftime("%Y-%m-%d")
        }
        self._save_sites()
        return True

    def remove_site(self, key: str) -> bool:
        if key in self._sites:
            del self._sites[key]
            self._save_sites()
            return True
        return False

    def toggle_site(self, key: str) -> bool | None:
        """Aktif/Pasif değiştirir. Yeni durumu döndürür."""
        if key not in self._sites:
            return None
        self._sites[key]["active"] = not self._sites[key].get("active", True)
        self._save_sites()
        return self._sites[key]["active"]

    def edit_site(self, key: str, display_name: str = None,
                  url: str = None, username_param=None) -> bool:
        if key not in self._sites:
            return False
        if display_name is not None:
            self._sites[key]["display_name"] = display_name.strip()
        if url is not None:
            if not validate_url(url):
                return False
            self._sites[key]["url"] = url.strip()
        if username_param is not None:
            self._sites[key]["username_param"] = username_param if username_param else None
        self._save_sites()
        return True

    def _save_sites(self):
        _save_json(SITES_FILE, self._sites)

    # ── Oy durumu ─────────────────────────────────────────────────────────

    def can_vote(self, site_key: str) -> bool:
        last = self._state.get(site_key)
        if not last:
            return True
        try:
            last_dt = datetime.fromisoformat(last)
            now = datetime.now()
            return last_dt.date() < now.date()
        except Exception:
            return True

    def mark_voted(self, site_key: str):
        self._state[site_key] = datetime.now().isoformat()
        _save_json(STATE_FILE, self._state)

    def get_last_vote(self, site_key: str) -> str:
        last = self._state.get(site_key)
        if last:
            try:
                return datetime.fromisoformat(last).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        return "Hiç oy verilmemiş"

    def get_all_last_votes(self) -> dict:
        result = {}
        for k in self._sites:
            result[k] = self.get_last_vote(k)
        return result
