#!/bin/bash
# Atlasoyuncu G233 Vote - Minecraft Vote Bot Başlatıcı (v2.0)
# Proje köküne git (burası baslatma/linux/ altında)
cd "$(dirname "$0")/../.."

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           Atlasoyuncu G233 Vote - Vote Bot v2.0                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "[HATA] Python3 bulunamadı!"
    echo "Kurulum: sudo apt install python3 python3-pip"
    exit 1
fi

# SeleniumBase kontrolü
python3 -c "import seleniumbase" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[BILGI] SeleniumBase yükleniyor..."
    pip3 install --user seleniumbase
fi

echo "[BILGI] Bot başlatılıyor..."
echo ""

# --auto: zamanlayıcı için otomatik mod (bu script elle çalıştırılınca menü açılır)
if [ "$1" = "--auto" ]; then
    python3 main.py --auto
else
    python3 main.py
fi

echo ""
echo "Islem tamamlandi."
read -p "Devam etmek icin Enter'a basin..."