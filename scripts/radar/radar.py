"""Radar phat hien chu de — quan ly trang thai, chong de xuat trung, dung brief.

Radar KHONG tu di doc web: viec do la cua agent (skill seo-radar-bds), vi doc
va danh gia nguon la viec phan doan, khong phai viec parse HTML. Script nay lo
phan co the tu dong hoa mot cach dang tin:

  sources              in ra danh muc nguon da xac minh
  check                mot su kien da tung duoc de xuat chua
  add <file.json>      ghi nhan ung vien + dung work/<slug>/ san sang push
  list                 lich su da de xuat va ket cuc cua chung
  close <slug>         danh dau ket cuc (VIET | BO_QUA | GOP)

Rang buoc chong bia dat duoc kiem o day, khong de agent tu hua:
mot ung vien khong co source_url HTTPS + published_date thi bi tu choi.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SOURCES_PATH = os.path.join(HERE, "sources.json")
SEEN_PATH = os.path.join(HERE, "seen.json")
TEMPLATES = os.path.join(ROOT, "templates")
WORK = os.path.join(ROOT, "work")

REQUIRED = ["slug", "primary_query", "event", "source_url", "source_tier", "published_date"]
VALID_TIERS = {"LAW", "GOV", "STATS", "SIGNAL"}
OUTCOMES = {"DE_XUAT", "VIET", "BO_QUA", "GOP"}
STALE_DAYS = 400


def force_utf8() -> None:
    for name in ("stdout", "stderr"):
        try:
            getattr(sys, name).reconfigure(encoding="utf-8")
        except Exception:
            pass


def load_sources() -> dict:
    with io.open(SOURCES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_seen() -> dict:
    if not os.path.exists(SEEN_PATH):
        return {"version": 1, "items": {}}
    with io.open(SEEN_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def save_seen(data: dict) -> None:
    with io.open(SEEN_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------
# Van tay su kien
# --------------------------------------------------------------------------

def _strip_diacritics(text: str) -> str:
    d = unicodedata.normalize("NFD", text)
    return "".join(c for c in d if unicodedata.category(c) != "Mn").replace("đ", "d")


def normalize_url(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"[?#].*$", "", u)
    return u.rstrip("/")


def normalize_text(text: str) -> str:
    t = _strip_diacritics((text or "").lower())
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())


def fingerprint(source_url: str, event: str) -> str:
    """Van tay = URL nguon + noi dung su kien. Mot su kien duoc dua tin o nhieu
    noi van tao van tay khac nhau; phan trung lap con lai do 'check' bat bang
    cach so trung tu khoa."""
    key = normalize_url(source_url) + "|" + normalize_text(event)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def similarity(a: str, b: str) -> float:
    wa, wb = set(normalize_text(a).split()), set(normalize_text(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


# --------------------------------------------------------------------------
# Lenh
# --------------------------------------------------------------------------

def cmd_sources(_args) -> int:
    src = load_sources()
    print("NGUỒN ĐÃ XÁC MINH (xác minh ngày %s)\n" % src.get("verified_on", "?"))
    for s in src["sources"]:
        print("  [%s] %s" % (s["tier"], s["name"]))
        print("       %s" % s["url"])
        print("       nhịp quét: %s" % s.get("cadence", "—"))
        for w in s.get("watch_for", []):
            print("       · %s" % w)
        print()
    print("NGUỒN ĐỊA PHƯƠNG — không ghi sẵn URL, phải tự tìm và mở thật:")
    for h in src["provincial_method"]["how"]:
        print("  · %s" % h)
    print()
    print("TÍN HIỆU (báo chí) — phải truy ngược về văn bản gốc:")
    print("  %s" % ", ".join(src["signal_sources"]["domains"]))
    print()
    print("ĐÍCH ĐẾN: %s" % src["destination"]["real_estate_hub"])
    print("  kiểm tra trùng: %s" % src["destination"]["inventory_check"])
    print()
    print(src["competitor_note"]["text"])
    return 0


def cmd_check(args) -> int:
    seen = load_seen()
    items = seen["items"]
    fp = fingerprint(args.url, args.event or "")

    if fp in items:
        it = items[fp]
        print("ĐÃ ĐỀ XUẤT TRƯỚC ĐÓ (%s)" % it.get("proposed_on"))
        print("  slug     : %s" % it.get("slug"))
        print("  kết cuc  : %s" % it.get("outcome"))
        if it.get("note"):
            print("  ghi chú  : %s" % it["note"])
        return 1

    # Gan trung: cung su kien nhung khac URL
    near = []
    for other in items.values():
        sim = similarity(args.event or "", other.get("event", ""))
        if sim >= 0.55:
            near.append((sim, other))
    if near:
        near.sort(key=lambda x: -x[0])
        print("CÓ THỂ TRÙNG với đề xuất cũ:")
        for sim, o in near[:3]:
            print("  %.0f%% giống · %s · %s (%s)" % (sim * 100, o.get("slug"),
                                                     o.get("event", "")[:70], o.get("outcome")))
        print("\nKiểm tra kỹ trước khi đề xuất lại.")
        return 1

    print("CHƯA TỪNG ĐỀ XUẤT — dùng được.")
    return 0


def _validate(cand: dict, index: int) -> list[str]:
    errs = []
    for field in REQUIRED:
        if not str(cand.get(field) or "").strip():
            errs.append("ứng viên #%d thiếu '%s'" % (index, field))

    url = str(cand.get("source_url") or "")
    if url and not url.lower().startswith("https://"):
        errs.append("ứng viên #%d: source_url phải là HTTPS đầy đủ và đã mở được thật" % index)

    tier = str(cand.get("source_tier") or "").upper()
    if tier and tier not in VALID_TIERS:
        errs.append("ứng viên #%d: source_tier '%s' không hợp lệ" % (index, tier))

    pub = str(cand.get("published_date") or "")
    if pub:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", pub):
            errs.append("ứng viên #%d: published_date phải dạng YYYY-MM-DD" % index)
        else:
            try:
                d = date.fromisoformat(pub)
                if d > date.today():
                    errs.append("ứng viên #%d: published_date ở tương lai (%s)" % (index, pub))
                elif d < date.today() - timedelta(days=STALE_DAYS):
                    errs.append("ứng viên #%d: nguồn cũ hơn %d ngày, kiểm tra còn hiệu lực không"
                                % (index, STALE_DAYS))
            except ValueError:
                errs.append("ứng viên #%d: published_date không phải ngày hợp lệ" % index)

    slug = str(cand.get("slug") or "")
    if slug and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        errs.append("ứng viên #%d: slug phải là chữ thường không dấu, nối bằng gạch" % index)

    if tier == "SIGNAL" and not str(cand.get("primary_source_todo") or "").strip():
        errs.append("ứng viên #%d: nguồn báo chí phải ghi 'primary_source_todo' — "
                    "văn bản gốc cần truy ngược trước khi viết" % index)

    return errs


def _yaml_scalar(value) -> str:
    s = str(value if value is not None else "").replace('"', "'")
    return '"%s"' % s


def _write_brief(folder: str, cand: dict) -> None:
    lists = ("entities", "questions_to_answer", "ymyl_areas", "existing_urls",
             "internal_link_targets", "external_source_targets", "same_page_variants",
             "separate_pages")
    scalars = [
        ("content_id", ""), ("slug", cand.get("slug", "")),
        ("created", date.today().isoformat()), ("author_agent", "seo-radar-bds"),
        ("primary_query", cand.get("primary_query", "")),
        ("intent", cand.get("intent", "")),
        ("serp_format_expected", cand.get("serp_format_expected", "")),
        ("reader", cand.get("reader", "")),
        ("reader_task", cand.get("reader_task", "")),
        ("reader_knowledge", cand.get("reader_knowledge", "")),
        ("gap_type", cand.get("gap_type", "")),
        ("gap_evidence", cand.get("gap_evidence", "")),
        ("unique_angle", cand.get("unique_angle", "")),
        ("url_decision", cand.get("url_decision", "")),
        ("url_decision_reason", cand.get("url_decision_reason", "")),
        ("why_now", cand.get("why_now", "")),
        ("geography", cand.get("geography", "")),
        ("property_type", cand.get("property_type", "")),
        ("data_as_of", cand.get("published_date", "")),
        ("cta", cand.get("cta", "")),
        ("internal_host", "muaban.net"),
        ("review_after", cand.get("review_after", "")),
    ]
    out = ["# Brief do radar dựng tự động. Agent phải hoàn thiện trước khi lên outline.",
           "# Trường nào chưa tra được thì để trống — KHÔNG điền phỏng đoán.",
           ""]
    for key, value in scalars:
        out.append("%s: %s" % (key, _yaml_scalar(value)))
    out.append("")
    out.append("# --- Nguồn phát hiện (radar ghi, đã xác minh mở được) ---")
    out.append("discovery_source_url: %s" % _yaml_scalar(cand.get("source_url", "")))
    out.append("discovery_source_tier: %s" % _yaml_scalar(cand.get("source_tier", "")))
    out.append("discovery_event: %s" % _yaml_scalar(cand.get("event", "")))
    if cand.get("primary_source_todo"):
        out.append("primary_source_todo: %s" % _yaml_scalar(cand["primary_source_todo"]))
    out.append("")
    for key in lists:
        values = cand.get(key) or []
        if isinstance(values, str):
            values = [values]
        out.append("%s:" % key)
        for v in values:
            out.append("  - %s" % _yaml_scalar(v))
        if not values:
            out.append('  - ""')
        out.append("")
    out.append("refresh_triggers:")
    for t in ("văn bản pháp luật liên quan thay đổi", "số liệu hết kỳ",
              "nguồn chết", "SERP đổi format"):
        out.append("  - %s" % _yaml_scalar(t))
    out.append("")
    with io.open(os.path.join(folder, "brief.yaml"), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(out))


def _seed_folder(cand: dict) -> str:
    folder = os.path.join(WORK, cand["slug"])
    os.makedirs(folder, exist_ok=True)
    _write_brief(folder, cand)

    ledger = os.path.join(folder, "evidence-ledger.csv")
    if not os.path.exists(ledger):
        src = os.path.join(TEMPLATES, "evidence-ledger.csv")
        with io.open(src, encoding="utf-8-sig", newline="") as fh:
            header = next(csv.reader(fh))
        with io.open(ledger, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(header)

    # CHI seed nhung file thuoc buoc nghien cuu. KHONG copy outline.md hay
    # qa-report.md: mot template chua dien van la file co noi dung, va se bi
    # tinh nham la "outline da viet xong" -> nhay qua cong duyet chu de.
    for name in ("serp-notes.md",):
        dst = os.path.join(folder, name)
        if not os.path.exists(dst):
            with io.open(os.path.join(TEMPLATES, name), encoding="utf-8") as s:
                body = s.read()
            with io.open(dst, "w", encoding="utf-8", newline="") as d:
                d.write(body)
    return folder


def cmd_add(args) -> int:
    with io.open(args.file, encoding="utf-8") as fh:
        payload = json.load(fh)
    cands = payload if isinstance(payload, list) else payload.get("candidates", [])
    if not cands:
        print("File không có ứng viên nào.", file=sys.stderr)
        return 2

    errors = []
    for i, c in enumerate(cands, start=1):
        errors += _validate(c, i)
    if errors:
        print("TỪ CHỐI — ứng viên chưa đạt điều kiện chống bịa đặt:\n", file=sys.stderr)
        for e in errors:
            print("  - %s" % e, file=sys.stderr)
        print("\nMọi ứng viên phải có nguồn HTTPS đã mở được thật và ngày công bố.",
              file=sys.stderr)
        return 2

    seen = load_seen()
    added, skipped = [], []
    for c in cands:
        fp = fingerprint(c["source_url"], c["event"])
        if fp in seen["items"]:
            skipped.append((c["slug"], seen["items"][fp].get("proposed_on")))
            continue
        folder = _seed_folder(c)
        seen["items"][fp] = {
            "slug": c["slug"],
            "event": c["event"],
            "primary_query": c.get("primary_query", ""),
            "source_url": c["source_url"],
            "source_tier": c["source_tier"],
            "published_date": c["published_date"],
            "proposed_on": datetime.now().strftime("%Y-%m-%d"),
            "outcome": "DE_XUAT",
            "note": "",
        }
        added.append((c["slug"], folder))
    save_seen(seen)

    for slug, _ in skipped:
        print("BỎ QUA (đã đề xuất trước): %s" % slug)
    for slug, folder in added:
        print("ĐÃ DỰNG: %s" % folder)
    if added:
        print("\nBước tiếp theo — đẩy lên Lark để bạn duyệt chủ đề:")
        for slug, _ in added:
            print("  python scripts/lark/lark_sync.py push work/%s" % slug)
    return 0


def cmd_list(args) -> int:
    seen = load_seen()
    items = list(seen["items"].values())
    if args.outcome:
        items = [i for i in items if i.get("outcome") == args.outcome]
    if not items:
        print("Chưa có đề xuất nào.")
        return 0
    items.sort(key=lambda i: i.get("proposed_on", ""), reverse=True)
    print("%-11s %-9s %-30s %s" % ("NGÀY", "KẾT CỤC", "SLUG", "SỰ KIỆN"))
    print("-" * 108)
    for i in items:
        print("%-11s %-9s %-30s %s" % (i.get("proposed_on", ""), i.get("outcome", ""),
                                       i.get("slug", "")[:30], i.get("event", "")[:50]))
    return 0


def cmd_close(args) -> int:
    if args.outcome not in OUTCOMES:
        print("Kết cục phải thuộc: %s" % ", ".join(sorted(OUTCOMES)), file=sys.stderr)
        return 2
    seen = load_seen()
    hits = [k for k, v in seen["items"].items() if v.get("slug") == args.slug]
    if not hits:
        print("Không thấy đề xuất nào có slug '%s'." % args.slug, file=sys.stderr)
        return 1
    for k in hits:
        seen["items"][k]["outcome"] = args.outcome
        seen["items"][k]["note"] = args.note or seen["items"][k].get("note", "")
    save_seen(seen)
    print("Đã đặt %s -> %s" % (args.slug, args.outcome))
    return 0


def main() -> int:
    force_utf8()
    ap = argparse.ArgumentParser(description="Radar phat hien chu de bat dong san.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("sources", help="In danh muc nguon da xac minh")

    p = sub.add_parser("check", help="Su kien nay da tung duoc de xuat chua")
    p.add_argument("--url", required=True)
    p.add_argument("--event", default="")

    p = sub.add_parser("add", help="Ghi nhan ung vien va dung work/<slug>/")
    p.add_argument("file", help="File JSON danh sach ung vien")

    p = sub.add_parser("list", help="Lich su de xuat")
    p.add_argument("--outcome", default=None, choices=sorted(OUTCOMES))

    p = sub.add_parser("close", help="Danh dau ket cuc cua mot de xuat")
    p.add_argument("slug")
    p.add_argument("outcome", choices=sorted(OUTCOMES))
    p.add_argument("--note", default="")

    args = ap.parse_args()
    return {"sources": cmd_sources, "check": cmd_check, "add": cmd_add,
            "list": cmd_list, "close": cmd_close}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
