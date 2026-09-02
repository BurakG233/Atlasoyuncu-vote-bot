#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
"""
Logger - Hem terminale hem dosyaya zaman damgalı log yazar.
Format: [HH:MM:SS] mesaj
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

_logger: logging.Logger | None = None


def setup_logger(log_file: str) -> logging.Logger:
    global _logger
    if _logger:
        return _logger

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s %(message)s",
        datefmt="[%H:%M:%S]"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)

    log = logging.getLogger("AtlasoyuncuG233VoteBot")
    log.setLevel(logging.DEBUG)
    log.handlers.clear()
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    log.propagate = False

    _logger = log
    return log


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        # Henüz kurulmadıysa basit bir fallback (setup_logger'ı bloklamaz)
        log = logging.getLogger("AtlasoyuncuG233VoteBot")
        if not log.handlers:
            log.addHandler(logging.StreamHandler(sys.stdout))
            log.setLevel(logging.DEBUG)
        return log
    return _logger
