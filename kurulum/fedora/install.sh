#!/bin/bash
# Atlasoyuncu G233 Vote - Fedora Kurulum Scripti
# Çalıştırma: ./kurulum/fedora/install.sh
set -e

PROJEN="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJEN"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        Atlasoyuncu G233 Vote - Fedora Kurulumu                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Python ──
echo "[1/6] Python kontrol ediliyor..."
if command -v python3 &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} $(python3 --version) bulundu"
else
    echo -e "  ${YELLOW}!${NC} python3 yükleniyor..."
    sudo dnf install python3 -y
fi

# ── 2. pip ──
echo "[2/6] pip kontrol ediliyor..."
if command -v pip3 &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} pip3 bulundu"
else
    echo -e "  ${YELLOW}!${NC} pip3 yükleniyor..."
    sudo dnf install python3-pip -y
fi

# ── 3. Chrome / Chromium ──
echo "[3/6] Chrome kontrol ediliyor..."
if command -v google-chrome &>/dev/null || command -v chromium-browser &>/dev/null || command -v chromium &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Chrome/Chromium bulundu"
else
    echo -e "  ${YELLOW}!${NC} Chrome yükleniyor..."
    # Google Chrome RPM repo ekle
    sudo tee /etc/yum.repos.d/google-chrome.repo >/dev/null <<'REPO'
[google-chrome]
name=google-chrome
baseurl=https://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
REPO
    sudo dnf install google-chrome-stable -y
fi

# ── 4. Kütüphaneler ──
echo "[4/6] Python kütüphaneleri yükleniyor..."
pip3 install --user seleniumbase nodriver cloudscraper requests
echo -e "  ${GREEN}✓${NC} Kütüphaneler yüklendi"

# ── 5. Kullanıcı adı ──
echo ""
echo "[5/6] Minecraft kullanıcı adınızı girin:"
read -p "Kullanıcı Adı: " USERNAME
if [ -z "$USERNAME" ]; then
    echo -e "${RED}✗${NC} Kullanıcı adı boş olamaz!"; exit 1
fi

# ── 6. Yapılandırma ──
echo "[6/6] Bot yapılandırılıyor..."
python3 - "$USERNAME" <<'PYEOF'
import json, sys, pathlib
name = sys.argv[1].strip()
p = pathlib.Path("config/bot_config.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["vote_username"] = name
p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print("  vote_username ayarlandı:", name)
PYEOF
echo -e "  ${GREEN}✓${NC} Kullanıcı adı ayarlandı: $USERNAME"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              KURULUM TAMAMLANDI! ✓                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Sonraki adımlar:"
echo "  1. Başlat:     python3 main.py"
echo "  2. Zamanlayıcı: sudo ./kurulum/fedora/setup_systemd.sh"
echo "  3. Log izle:   tail -f logs/atlas_vote_bot.log"
echo ""
