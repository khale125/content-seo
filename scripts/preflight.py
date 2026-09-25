"""Kiem may chu truoc khi chay du an. Chay dau tien tren mot VPS moi.

Moi dong in ra la ASCII thuan co y: mot VPS chua dat locale UTF-8 se vo ngay khi
in tieng Viet co dau, va script nay ton tai de BAO loi do chu khong phai de gap no.

    python3 scripts/preflight.py            # kiem may + chay hoi quy
    python3 scripts/preflight.py --lark     # kiem them dang nhap Lark (goi mang)
    python3 scripts/preflight.py --wp       # kiem them dang nhap WordPress (goi mang)

Ma thoat: 0 = du dieu kien chay, 1 = con muc BAT BUOC chua dat.
"""

from __future__ import annotations

import argparse
import locale
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PY_MIN = (3, 10)
CORPUS_MIN = 24          # so bai that trong reference/muaban-blog, nguong do tu day ra

results: list[tuple[str, bool, bool, str]] = []   # (ten, dat, bat_buoc, ghi chu)


def check(name: str, ok: bool, required: bool = True, note: str = "") -> bool:
    results.append((name, ok, required, note))
    mark = "OK  " if ok else ("FAIL" if required else "WARN")
    line = f"[{mark}] {name}"
    if note:
        line += f" -- {note}"
    print(line)
    return ok


def run(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout,
                              encoding="utf-8", errors="replace", cwd=ROOT)
    except FileNotFoundError:
        return 127, "khong tim thay lenh"
    except subprocess.TimeoutExpired:
        return 124, f"qua {timeout}s"
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


# --------------------------------------------------------------------------
# 1. Moi truong chay
# --------------------------------------------------------------------------

def check_runtime() -> None:
    print("--- 1. Moi truong chay ---")
    v = sys.version_info
    check(f"Python {v.major}.{v.minor}.{v.micro}", v[:2] >= PY_MIN,
          note="" if v[:2] >= PY_MIN else f"can >= {PY_MIN[0]}.{PY_MIN[1]}")

    # Day la loi hay gap nhat khi doi tu Windows sang VPS: locale POSIX lam
    # print() tieng Viet vo voi UnicodeEncodeError o giua mot lan chay dai. Moi
    # script cua du an tu goi reconfigure(encoding="utf-8") o ham main, nen dieu
    # can kiem khong phai encoding mac dinh ma la reconfigure co an hay khong.
    enc = (sys.stdout.encoding or "").lower()
    check(f"stdout encoding mac dinh = {enc or 'khong ro'}", "utf" in enc, required=False,
          note="" if "utf" in enc else "nen dat LANG=C.UTF-8 cho moi lenh go tay")
    try:
        "Điềm báo — chuồn chuồn".encode(sys.stdout.encoding or "ascii")
        viet_ok = True
    except (UnicodeEncodeError, LookupError):
        viet_ok = False
    check("in duoc tieng Viet co dau", viet_ok,
          note="" if viet_ok else "dat PYTHONIOENCODING=utf-8 va LANG=C.UTF-8 roi chay lai")

    fs = sys.getfilesystemencoding().lower()
    check(f"filesystem encoding = {fs}", "utf" in fs,
          note="" if "utf" in fs else "ten file tieng Viet se sai")

    try:
        loc = locale.getlocale()[1] or locale.getpreferredencoding(False)
    except Exception:
        loc = "?"
    check(f"locale encoding = {loc}", True, required=False)

    # Ghi duoc vao work/ va wiki/ moi chay duoc quy trinh
    for d in ("work", "wiki", "reference"):
        p = os.path.join(ROOT, d)
        check(f"ghi duoc vao {d}/", os.path.isdir(p) and os.access(p, os.W_OK),
              note="" if os.path.isdir(p) else "thieu thu muc")


# --------------------------------------------------------------------------
# 2. Du lieu do luong — thieu la moi nguong deu sai
# --------------------------------------------------------------------------

def check_data() -> None:
    print("--- 2. Du lieu do luong ---")
    corpus = os.path.join(ROOT, "reference", "muaban-blog")
    n = len([f for f in os.listdir(corpus) if f.endswith(".md")]) if os.path.isdir(corpus) else 0
    check(f"kho bai that: {n} bai", n >= CORPUS_MIN,
          note="" if n >= CORPUS_MIN else f"can >= {CORPUS_MIN}; moi nguong giong van do tu day")

    try:
        import PIL
        pil_ok, pil_note = True, f"Pillow {PIL.__version__}"
    except ImportError:
        pil_ok, pil_note = False, "Ubuntu: sudo apt install python3-pil · Windows: pip install pillow"
    check("Pillow (cat anh ve 800x600 khi tim anh)", pil_ok, note=pil_note if not pil_ok else pil_note)

    for rel, required in (
        ("scripts/lexicon/ai_phrases.json", True),
        ("scripts/lexicon/house_voice.json", True),
        ("reference/internal-links-mbn.csv", True),
        ("examples/fixture-dat-chuan/article.md", True),
        ("templates/outline.md", True),
    ):
        p = os.path.join(ROOT, rel)
        check(rel, os.path.isfile(p), required=required,
              note="" if os.path.isfile(p) else "thieu file")


# --------------------------------------------------------------------------
# 3. Hoi quy — bo kiem con phan xu dung hay khong
# --------------------------------------------------------------------------

def check_regression() -> None:
    print("--- 3. Hoi quy bo kiem (ma thoat phai dung) ---")
    cases = [
        ("bai dat chuan -> PASS", ["run_qa.py", "examples/fixture-dat-chuan/article.md"], 0),
        ("bai co loi -> FAIL", ["run_qa.py", "examples/fixture-van-may/article.md"], 1),
        ("outline lech -> FAIL", ["outline_check.py", "examples/fixture-outline-lech/outline.md"], 1),
        ("wiki_lint -> sach", ["wiki_lint.py"], 0),
    ]
    for name, args, want in cases:
        code, out = run([sys.executable, os.path.join("scripts", args[0]), *args[1:]])
        check(f"{name}", code == want,
              note="" if code == want else f"ma thoat {code}, cho {want}: {out[:160]}")

    code, out = run([sys.executable, os.path.join("scripts", "internal_links.py"), "stats"])
    check("kho internal link doc duoc", code == 0,
          note="" if code == 0 else out[:160])


# --------------------------------------------------------------------------
# 4. Lark (tuy chon, goi mang)
# --------------------------------------------------------------------------

def check_lark() -> None:
    print("--- 4. Lark ---")
    sys.path.insert(0, os.path.join(ROOT, "scripts", "lark"))
    try:
        import lark_cli
    except Exception as exc:                                    # pragma: no cover
        check("nap lark_cli", False, note=str(exc)[:160])
        return

    node = lark_cli._discover_node()
    check(f"node: {node or 'khong thay'}", bool(node),
          note="" if node else "cai Node.js hoac dat LARK_NODE")
    entry = lark_cli._discover_cli()
    check(f"@larksuite/cli: {'thay' if entry else 'khong thay'}", bool(entry),
          note="" if entry else "npm i -g @larksuite/cli, hoac dat LARK_CLI_ENTRY")
    if not (node and entry):
        return

    try:
        cfg = lark_cli.load_config(required=False)
    except Exception as exc:
        check("doc config.json", False, note=str(exc)[:160])
        return
    check(f"app_token trong config: {'co' if cfg.get('app_token') else 'trong'}",
          bool(cfg.get("app_token")), required=False,
          note="" if cfg.get("app_token") else "chay lark_setup.py de dung Base moi")

    # Da dang nhap chua: goi mot lenh doc, khong sua gi
    code, out = run([sys.executable, os.path.join("scripts", "lark", "lark_watch.py"), "--todo"])
    check("phien dang nhap Lark con hieu luc", code in (0, 3),
          note="" if code in (0, 3) else out[:200] or "chay 'lark auth login' tren may co trinh duyet")


# --------------------------------------------------------------------------
# 5. WordPress (tuy chon, goi mang)
# --------------------------------------------------------------------------

def check_wp() -> None:
    print("--- 5. WordPress ---")
    # Hoi chinh wp_draft chu khong tu doan: no biet ca ba nguon (bien moi truong,
    # .env o goc du an, ~/.muaban-wp.json) va thu tu uu tien giua chung.
    sys.path.insert(0, os.path.join(ROOT, "scripts", "wp"))
    try:
        import wp_draft
        user, _ = wp_draft.load_credentials()
        has, why = True, f"tai khoan {user}"
    except Exception as exc:
        has, why = False, str(exc).splitlines()[0][:120]
    check("thong tin dang nhap WordPress", has, note=why)
    if not has:
        return
    code, out = run([sys.executable, os.path.join("scripts", "wp", "wp_draft.py"), "--check"])
    check("dang nhap WordPress thanh cong", code == 0, note="" if code == 0 else out[:200])


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiem may chu truoc khi chay du an")
    ap.add_argument("--lark", action="store_true", help="kiem them Lark (goi mang)")
    ap.add_argument("--wp", action="store_true", help="kiem them WordPress (goi mang)")
    ap.add_argument("--all", action="store_true", help="kiem tat ca")
    args = ap.parse_args()

    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    print(f"Du an: {ROOT}")
    print(f"Python: {sys.executable}")
    print()
    check_runtime()
    print()
    check_data()
    print()
    check_regression()
    if args.lark or args.all:
        print()
        check_lark()
    if args.wp or args.all:
        print()
        check_wp()

    failed = [r for r in results if not r[1] and r[2]]
    warned = [r for r in results if not r[1] and not r[2]]
    print()
    print(f"Tong: {len(results)} muc kiem, {len(failed)} that bai, {len(warned)} canh bao")
    if failed:
        print("Chua chay duoc, phai sua:")
        for name, _, _, note in failed:
            print(f"  - {name}{(': ' + note) if note else ''}")
        return 1
    print("Du dieu kien chay.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
