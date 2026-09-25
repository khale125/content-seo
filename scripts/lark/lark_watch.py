"""Bao khi o 'Ket qua duyet' tren Base doi. Moi chuyen tiep in DUNG MOT DONG.

  python -u scripts/lark/lark_watch.py                 # theo doi, tu dung sau 29 phut
  python -u scripts/lark/lark_watch.py --once          # kiem mot luot roi thoat

Vi sao phai doc dinh ky thay vi nhan su kien:

  Lark khong co event nao cho ban ghi Base thay doi (da tra het 26 EventKey).
  Duong vong qua tin nhan bot cung khong di duoc: bot chi nhan duoc tin nhom khi
  app khai `im:message.group_msg` hoac `im:message.group_at_msg:readonly`, ma
  the tin cua tro ly Base thi khong @nhac bot duoc. Nen doc dinh ky la cach con
  lai. Mot luot doc = mot loi goi API cho TAT CA bai, 60 giay mot lan.

Chuong trinh nay KHONG GHI GI len Lark:
  - khong goi `pull` (pull ghi mot dong vao bang Nhat ky moi lan chay)
  - khong goi `push`, khong tao/sua/xoa ban ghi
  - chi ghi mot file tai `work/.lark-watch.json` de nho da bao gi roi

Tin bao chi la chuong cua. Chi `lark_sync.py gate work/<slug>` tra ve exit 0 moi
la da duyet (CLAUDE.md quy tac 10).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import lark_cli as lc
import lark_sync as ls

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "work")
STATE = os.path.join(WORK, ".lark-watch.json")

# Khong con "BRIEF_PENDING": quy trinh moi bo cong duyet chu de vi nguoi dung tu dua
# tu khoa chinh kem volume. Chi con hai cong: duyet outline va duyet bai.
NEXT_SKILL = {
    "OUTLINE_PENDING": "seo-writer-bds",
    "ARTICLE_PENDING": "seo-qa-bds",
}


def slug_map() -> dict[str, str]:
    """{record_id: slug}, quet lai moi luot de bai vua push cung nhan ra duoc."""
    out = {}
    for name in sorted(os.listdir(WORK)) if os.path.isdir(WORK) else []:
        path = os.path.join(WORK, name, ls.STATE_FILE)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                rid = (json.load(fh).get("record_id") or "").strip()
        except Exception:                                      # noqa: BLE001
            continue
        if rid:                       # bo qua chuoi rong: push ghi record_id=""
            out[rid] = name           # truoc khi cham Lark, de map nham het
    return out


def load_seen() -> dict:
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:                                          # noqa: BLE001
        return {}


def save_seen(seen: dict) -> None:
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(seen, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE)            # doi cho nguyen tu, khong de file nua voi


def check(cfg: dict, seen: dict, slugs: dict) -> list[str]:
    """So voi luot truoc, tra ve cac dong can in. Khong in gi o day."""
    lines = []
    for rec in ls.read_table(cfg, "pipeline"):
        rid = rec["record_id"]
        v = rec["values"]
        g = ls.gate_status(v)
        cid = v.get("content_id", "?").strip()
        slug = slugs.get(rid, "-")
        # Chu ky gon: chi nhung gi lam doi hanh dong cua agent. Co ca cong tac tu khoa,
        # vi tich o do la mot thay doi can bao.
        now = (f"{g['state']}|{g['review']}|{g['reviewer']}|{int(g['open'])}"
               f"|{(v.get('keyword_ok') or '').strip().lower()}")
        was = seen.get(rid)
        seen[rid] = now

        # Dong tu khoa moi: da tich cong tac, con chua bat dau lam.
        # Nhanh nay CO Y bao ngay ca o lan dau thay, khac ba nhanh con lai. Ly do: dong
        # nay do nguoi dung vua go tay tren Base, khong phai do agent push len, nen "lan
        # dau thay" chinh la luc can bao. Ba nhanh duoi van giu le lay moc im lang.
        if (v.get("keyword_ok") or "").strip().lower() in ls.TRUTHY and not (v.get("state") or "").strip():
            if was != now:
                q = (v.get("primary_query") or "").strip()
                lines.append(f"[LARK] TU KHOA MOI {cid} \"{q[:70]}\" "
                             f"vol={v.get('search_volume') or '-'} next=intake+seo-outline-bds")
            continue

        if was is None or was == now:
            continue                  # lan dau thay -> lay lam moc, khong bao
        if g["open"]:
            lines.append(f"[LARK] DUYET {cid} {slug} gate={g['state']} "
                         f'by="{g["reviewer"]}" next={NEXT_SKILL.get(g["state"], "-")}')
        elif g["is_gate"] and g["review"] == "REJECTED":
            lines.append(f"[LARK] TU CHOI {cid} {slug} gate={g['state']} "
                         f'by="{g["reviewer"]}" gop-y="{g["feedback"][:200]}" next=sua+push')
        # Moi thay doi khac — ke ca cum duyet bi chinh push cua agent xoa trang —
        # deu im lang: agent da biet no roi.
    return lines


def todo(cfg: dict, slugs: dict) -> list[str]:
    """Viec dang cho, SUY RA TU TRANG THAI SONG tren Base — khong dung bo nho chenh lech.

    Vi sao can ham nay ben canh `check()`: `check()` bao *thay doi*, va no cap nhat moc
    ngay sau khi in. Neu dong tin bao do khong ai doc — phien dong ngay sau do, hoac
    Monitor chua duoc gan — thi luot sau khong bao lai nua, va phe duyet mat luon. Da
    xay ra that: nguoi dung tich duyet ma khong co gi chay.

    Ham nay khong co ky uc nen khong mat gi duoc. Moi luot doc lai Base va tra loi dung
    mot cau: *ngay bay gio co viec gi dang cho agent lam?* Dung o hook mo phien va hook
    ket luot, nen du bo qua bao nhieu lan thi viec van con do.
    """
    lines = []
    for rec in ls.read_table(cfg, "pipeline"):
        v = rec["values"]
        g = ls.gate_status(v)
        cid = (v.get("content_id") or "?").strip()
        slug = slugs.get(rec["record_id"], "-")

        if (v.get("keyword_ok") or "").strip().lower() in ls.TRUTHY \
                and not (v.get("state") or "").strip():
            q = (v.get("primary_query") or "").strip()
            lines.append(f'[VIEC] {cid} tu khoa moi "{q[:70]}" '
                         f'vol={v.get("search_volume") or "-"} '
                         f'-> chay: lark_sync.py intake, roi skill seo-outline-bds')
            continue

        if g["open"]:
            lines.append(f"[VIEC] {cid} {slug} cong {g['state']} DA MO "
                         f'by="{g["reviewer"]}" '
                         f'-> xac minh: lark_sync.py gate work/{slug} (exit 0), '
                         f'roi chay skill {NEXT_SKILL.get(g["state"], "-")}')
        elif g["is_gate"] and g["review"] == "REJECTED":
            lines.append(f"[VIEC] {cid} {slug} cong {g['state']} BI TU CHOI "
                         f'by="{g["reviewer"]}" gop-y="{g["feedback"][:200]}" '
                         f"-> sua theo gop y, chay QA, roi lark_sync.py push work/{slug}")
    return lines


def main() -> int:
    lc.force_utf8()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:                                          # noqa: BLE001
        pass

    ap = argparse.ArgumentParser(description="Bao khi ket qua duyet tren Base doi.")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--todo", action="store_true",
                    help="in viec dang cho suy ra tu trang thai song, khong dung moc")
    # Mac dinh 29 phut, khop tran cua cong cu Monitor. Neu tien trinh song lau
    # hon nguoi doc no, no van nuot chuyen tiep vao file trang thai — noi khong
    # ai doc — va phe duyet mat luon.
    ap.add_argument("--max-runtime", type=int, default=1740)
    args = ap.parse_args()

    try:
        cfg = lc.load_config()
    except lc.LarkError as exc:
        print(f"[LARK] LOI cau hinh: {exc}", flush=True)
        return 2

    if args.todo:
        try:
            lines = todo(cfg, slug_map())
        except lc.LarkError as exc:
            print(f"[LARK] khong doc duoc Base: {exc}", flush=True)
            return 2
        for line in lines:
            print(line, flush=True)
        # Ma thoat 3 = "co viec dang cho". Hook ket luot dung ma nay de biet co nen
        # chan luot ket hay khong, khong phai doan tu chuoi in ra.
        return 3 if lines else 0

    seen = load_seen()
    started = time.time()
    fails = 0
    if not args.once:
        print(f"[LARK] SAN SANG interval={args.interval}s max={args.max_runtime}s", flush=True)

    while True:
        try:
            lines = check(cfg, seen, slug_map())
            if fails:
                print(f"[LARK] OK doc lai duoc sau {fails} lan loi", flush=True)
                fails = 0
            for line in lines:
                print(line, flush=True)
            save_seen(seen)            # luu SAU khi in: chet giua chung thi bao
                                       # trung mot lan, con hon nuot mat mot lan
        except lc.LarkError as exc:
            msg = str(exc).lower()
            if any(k in msg for k in ("missing_scope", "unauthorized", "invalid token", "login")):
                print(f"[LARK] HONG XAC THUC: {exc}", flush=True)
                print("[LARK] chay `lark-cli auth login` roi bat lai", flush=True)
                return 2
            fails += 1
            if fails == 3:             # blip mang la chuyen thuong, im hai lan dau
                print(f"[LARK] LOI doc Base {fails} lan lien tiep: {exc}", flush=True)
        if args.once:
            return 0
        if args.max_runtime and time.time() - started >= args.max_runtime:
            print("[LARK] DUNG het gio · bat lai neu con bai dang cho duyet", flush=True)
            return 0
        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    sys.exit(main())
