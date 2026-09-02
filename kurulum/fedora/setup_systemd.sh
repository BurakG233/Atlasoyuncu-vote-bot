#!/bin/bash
# Atlasoyuncu G233 Vote - systemd zamanlayıcı (Fedora)
# Çalıştırma: sudo ./kurulum/fedora/setup_systemd.sh
set -e

PROJEN="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJEN"

GREEN='\033[0;32m'; NC='\033[0m'

USER_NAME=$(whoami)
WORK_DIR="$PROJEN"
PYTHON_PATH=$(which python3)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        SYSTEMD ZAMANLAYICI KURULUMU (Fedora)                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Kullanıcı: $USER_NAME"
echo "Dizin   : $WORK_DIR"
echo "Python  : $PYTHON_PATH"
echo ""

echo "[1/3] Servis dosyası oluşturuluyor..."
sudo tee /etc/systemd/system/atlas-vote-bot.service >/dev/null <<EOF
[Unit]
Description=Atlasoyuncu G233 Vote - Minecraft Vote Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER_NAME
WorkingDirectory=$WORK_DIR
ExecStart=$PYTHON_PATH $WORK_DIR/main.py --auto
RemainAfterExit=no
StandardOutput=append:$WORK_DIR/bot_output.log
StandardError=append:$WORK_DIR/bot_error.log
Environment="HOME=$HOME"
Environment="PATH=$PATH"
Environment="DISPLAY=:1"

[Install]
WantedBy=multi-user.target
EOF
echo -e "  ${GREEN}✓${NC} Servis dosyası oluşturuldu"

echo "[2/3] Timer dosyası oluşturuluyor..."
sudo tee /etc/systemd/system/atlas-vote-bot.timer >/dev/null <<EOF
[Unit]
Description=Atlasoyuncu G233 Vote - Vote Bot Zamanlayıcı
Requires=atlas-vote-bot.service

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
echo -e "  ${GREEN}✓${NC} Timer dosyası oluşturuldu"

echo "[3/3] systemd yapılandırılıyor..."
sudo systemctl daemon-reload
sudo systemctl enable atlas-vote-bot.timer atlas-vote-bot.service
sudo systemctl start atlas-vote-bot.timer
echo -e "  ${GREEN}✓${NC} Timer etkinleştirildi"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           ZAMANLAYICI KURULDU! ✓                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Komutlar:"
echo "  Durum    : sudo systemctl status atlas-vote-bot.timer"
echo "  Çalıştır : sudo systemctl start atlas-vote-bot.service"
echo "  Log      : sudo journalctl -u atlas-vote-bot.service -f"
echo "  Durdur   : sudo systemctl stop atlas-vote-bot.timer"
echo ""
