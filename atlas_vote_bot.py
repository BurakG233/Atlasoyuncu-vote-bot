#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
"""
Geriye dönük uyumluluk shim.
Eski: python3 atlas_vote_bot.py  →  Yeni: python3 main.py
"""
import runpy, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
runpy.run_path(str(pathlib.Path(__file__).parent / "main.py"), run_name="__main__")
