"""Chay khi agent ket mot luot. Neu tren Lark dang co viec cho, keo agent lam tiep.

Day la mat xich lam cho "duyet la tu chay" thanh that trong mot phien lam viec.
Truoc khi co hook nay, chuoi phu thuoc vao mot thu duy nhat: agent phai nho gan cong
cu Monitor va nho gan lai moi 29 phut. Quen mot lan la nguoi dung tich duyet xong roi
ngoi cho — da xay ra hai lan.

Hook nay khong co ky uc va khong doc moc chenh lech. No goi `lark_watch.py --todo`,
tuc doc lai trang thai SONG tren Base, nen bo qua bao nhieu luot cung khong mat viec.

Ba chot chong vong lap, can ca ba:

1. `stop_hook_active` — Claude Code dat co nay khi luot hien tai da bi chinh hook Stop
   chan mot lan. Thay co thi thoi ngay, khong chan nua.
2. Chu ky viec — chan roi thi ghi chu ky ra `work/.lark-stop.json`. Cung viec do thi
   khong chan lan hai, vi agent co the da doc va co ly do chua lam duoc (vi du gap GAP
   phai hoi nguoi dung). Viec doi thi chu ky doi, va chan lai.
3. Luon thoat 0 khi loi — Lark hong, mang hong hay chua dang nhap deu khong duoc phep
   lam agent mac ket khong ket duoc luot.

Ma thoat cua `--todo`: 0 = khong co viec, 3 = co viec, khac = loi.
"""

import hashlib
import json
import os
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WATCH = os.path.join(ROOT, "scripts", "lark", "lark_watch.py")
STATE = os.path.join(ROOT, "work", ".lark-stop.json")

HOW = (
    "Tren Lark dang co viec cho. Lam tiep ngay trong luot nay, dung ket luot va dung "
    "hoi lai nhung gi da ro:\n\n"
    "{work}\n\n"
    "Thu tu bat buoc:\n"
    "1. Xac minh bang `python scripts/lark/lark_sync.py gate work/<slug>` - chi exit 0 "
    "moi la da duyet (CLAUDE.md quy tac 10). Dong [VIEC] o tren chi la chuong cua.\n"
    "2. Cong DA MO thi chay dung skill duoc ghi trong dong do.\n"
    "3. BI TU CHOI thi doc ky gop y, sua, chay QA, roi `lark_sync.py push work/<slug>`.\n"
    "4. TU KHOA MOI thi `lark_sync.py intake` roi skill seo-outline-bds.\n"
    "Neu that su khong lam duoc (vi du thieu bang chung, phai hoi nguoi dung mot cau) "
    "thi noi ro con thieu gi roi ket luot; hook se khong chan lai cung viec nay."
)


def read_hook_input() -> dict:
    try:
        raw = sys.stdin.read()
    except Exception:                                          # noqa: BLE001
        return {}
    try:
        return json.loads(raw) if raw.strip() else {}
    except Exception:                                          # noqa: BLE001
        return {}


def last_signature() -> str:
    try:
        with open(STATE, encoding="utf-8") as fh:
            return str(json.load(fh).get("signature") or "")
    except Exception:                                          # noqa: BLE001
        return ""


def save_signature(sig: str) -> None:
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        tmp = STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"signature": sig}, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE)
    except Exception:                                          # noqa: BLE001
        pass


def main() -> int:
    # Console Windows mac dinh cp1252, va JSON in ra day co tieng Viet (gop y cua nguoi
    # duyet). Khong ep UTF-8 thi dau tieng Viet thanh '?' ngay trong chuoi reason.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                          # noqa: BLE001
        pass

    data = read_hook_input()
    if data.get("stop_hook_active"):
        return 0
    if not os.path.isfile(WATCH):
        return 0

    try:
        proc = subprocess.run(
            [sys.executable, "-u", WATCH, "--todo"],
            cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace",
            timeout=90,
        )
    except Exception:                                          # noqa: BLE001
        return 0                       # mang cham hay treo: de agent ket luot binh thuong

    work = (proc.stdout or "").strip()
    if proc.returncode != 3 or not work:
        return 0

    sig = hashlib.sha256(work.encode("utf-8")).hexdigest()[:16]
    if sig == last_signature():
        return 0                       # cung viec do, da nhac mot lan
    save_signature(sig)

    print(json.dumps({"decision": "block", "reason": HOW.format(work=work)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
