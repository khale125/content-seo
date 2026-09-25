#!/usr/bin/env bash
# Cai dat content-seo tren Linux / macOS.
#
#   bash install.sh
#
# Script nay KHONG cai goi Python nao, vi du an chi dung thu vien chuan. Viec cua
# no la: kiem phien ban, dung .env, do Node/Lark CLI, roi chay preflight.
# Chi tiet may chu: docs/15-trien-khai-vps.md

set -uo pipefail
cd "$(dirname "$0")"

PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
    echo "[LOI] Khong tim thay python3. Cai Python 3.10 tro len roi chay lai."
    exit 1
fi

VER=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
OK=$("$PY" -c 'import sys; print(1 if sys.version_info[:2] >= (3,10) else 0)')
if [ "$OK" != "1" ]; then
    echo "[LOI] Python $VER qua cu, can 3.10 tro len."
    exit 1
fi
echo "[OK] Python $VER ($PY)"

# Locale: day la loi hay gap nhat tren VPS, bat duoc som thi do mat mot buoi
case "${LANG:-}" in
    *UTF-8|*utf8|*utf-8) echo "[OK] LANG=$LANG" ;;
    *) echo "[CANH BAO] LANG='${LANG:-chua dat}' khong phai UTF-8."
       echo "           Them vao ~/.bashrc:  export LANG=C.UTF-8 PYTHONIOENCODING=utf-8" ;;
esac

# .env: tao tu ban mau, khong ghi de neu da co
if [ -f .env ]; then
    echo "[OK] .env da co, giu nguyen"
else
    cp .env.example .env
    chmod 600 .env
    echo "[OK] Da tao .env tu .env.example — hay dien MBWP_USER va MBWP_APP_PASSWORD"
fi

# Node + Lark CLI: canh bao thoi, vi bo kiem chay duoc ma khong can chung.
# Do bang chinh ham cua du an chu khong bang `command -v lark`: cai bang pnpm thi
# `lark` khong nam tren PATH nhung du an van goi duoc qua node + run.js.
if command -v node >/dev/null 2>&1; then
    echo "[OK] node $(node --version)"
    if "$PY" -c "import sys; sys.path.insert(0,'scripts/lark'); import lark_cli; sys.exit(0 if lark_cli._discover_cli() else 1)" 2>/dev/null; then
        echo "[OK] @larksuite/cli da cai"
    else
        echo "[CANH BAO] Chua co @larksuite/cli. Phan dong bo Lark se khong chay."
        echo "           Cai: npm install -g @larksuite/cli   roi: lark auth login"
    fi
else
    echo "[CANH BAO] Chua co Node.js. Phan dong bo Lark se khong chay."
    echo "           Xem docs/15-trien-khai-vps.md muc 3."
fi

echo
echo "--- Kiem may ---"
"$PY" scripts/preflight.py
CODE=$?

echo
if [ $CODE -eq 0 ]; then
    cat <<'NEXT'
Cai dat xong. Ba viec tiep theo:

  1. Dien .env            : MBWP_USER va MBWP_APP_PASSWORD (WP Admin -> Profile -> Application Passwords)
  2. Dang nhap Lark       : lark auth login        (can trinh duyet; may khong man hinh xem docs/15 muc 6)
  3. Mo Claude Code trong thu muc nay roi doc CLAUDE.md

Kiem lai bat ky luc nao:  python3 scripts/preflight.py --all
NEXT
else
    echo "Preflight con muc chua dat — sua theo danh sach o tren roi chay lai:"
    echo "  python3 scripts/preflight.py"
fi
exit $CODE
