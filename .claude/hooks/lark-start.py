"""Chay luc mo phien Claude Code. In ra context cho agent, khong lam gi khac.

Hai viec:

1. Chay `lark_watch.py --todo` de liet ke VIEC DANG CHO, suy ra tu trang thai
   song tren Base. Day moi la nguon su that: `--once` chi bao *thay doi* va no
   cap nhat moc ngay sau khi in, nen mot tin bao khong ai doc la mat luon. Da
   xay ra that hai lan. `--todo` khong co ky uc nen khong mat gi duoc.

   Chay ca `lark_watch.py --once` de dat moc cho kenh theo doi, va de thay
   nhung chuyen tiep da xay ra trong luc khong co phien nao mo.

2. Nhac agent gan kenh theo doi. Monitor la cong cu cua agent, hook khong tu gan
   duoc — nhung context nay se lam agent gan ngay o luot dau tien.

Luon thoat ma 0. Lark hong khong duoc lam hong ca phien lam viec.
"""

import os
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WATCH = os.path.join(ROOT, "scripts", "lark", "lark_watch.py")

ARM = (
    "Kenh theo doi cong duyet CHUA chay trong phien nay. Hay gan Monitor ngay "
    "bang cong cu Monitor voi lenh:\n"
    '    cd "' + ROOT + '" && python -u scripts/lark/lark_watch.py --interval 60 --max-runtime 1740\n'
    "timeout_ms 1800000. Khi Monitor het han thi gan lai, chung nao con bai dang "
    "dung o cong duyet. Moi dong [LARK] la mot chuyen tiep: DUYET thi chay skill "
    "tuong ung, TU CHOI thi doc gop y va sua. Luon chay `lark_sync.py gate "
    "work/<slug>` xac minh truoc khi hanh dong - tin bao chi la chuong cua."
)


def main() -> int:
    # Console Windows mac dinh cp1252; ep UTF-8 de gop y tieng Viet khong thanh
    # dau hoi nguoc khi di qua stdout cua hook.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                          # noqa: BLE001
        pass

    if not os.path.isfile(WATCH):
        return 0

    def run(*flags: str) -> str:
        proc = subprocess.run(
            [sys.executable, "-u", WATCH, *flags],
            cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace",
            timeout=90,
        )
        return (proc.stdout or "").strip()

    try:
        changed = run("--once")        # dat moc cho kenh theo doi
        work = run("--todo")           # viec dang cho, doc lai trang thai song
    except Exception as exc:                                   # noqa: BLE001
        print(f"[LARK] khong chay duoc lark_watch: {exc}")
        print(ARM)
        return 0

    if changed:
        print("Thay doi tren Lark ke tu lan kiem truoc:")
        print(changed)
    if work:
        print("VIEC DANG CHO tren Lark - lam ngay, dung hoi lai nhung gi da ro:")
        print(work)
        print("Xac minh bang `lark_sync.py gate work/<slug>` (exit 0) truoc khi hanh dong.")
    if not changed and not work:
        print("[LARK] Khong co cong duyet nao doi, va khong co viec nao dang cho.")
    print(ARM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
