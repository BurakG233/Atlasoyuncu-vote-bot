#!/bin/bash
# Atlasoyuncu G233 Vote - Cron zamanlayıcı (Ubuntu / Debian)
# Çalıştırma: ./kurulum/linux/setup_cron.sh

PROJEN="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJEN"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          CRON ZAMANLAYICI KURULUMU                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

crontab -l > crontab_backup.txt 2>/dev/null || true

(crontab -l 2>/dev/null
 echo "# Atlasoyuncu G233 Vote - Minecraft Vote Bot"
 echo "0 9 * * * cd $PROJEN && /usr/bin/python3 main.py --auto >> $PROJEN/bot_cron.log 2>&1"
) | crontab -

echo "✓ Cron görevi eklendi!"
echo "Her gün saat 09:00'da otomatik çalışacak."
echo ""
echo "Kontrol:"
echo "  crontab -l            # görevleri listele"
echo "  tail -f bot_cron.log  # logları izle"
echo ""
