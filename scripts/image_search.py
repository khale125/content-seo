"""Tim anh co giay phep ro rang tren internet, tai ve, va ghi image-manifest.csv.

Hai nguon, deu tra ve giay phep kem tac gia bang may doc duoc:

  - Wikimedia Commons  (nguon chinh: metadata giay phep do cong dong kiem, on dinh)
  - Openverse          (nguon phu: gom anh CC tu Flickr va noi khac; giay phep phai
                        kiem lai o trang goc truoc khi CLEARED, xem --verified)

Chi nhan giay phep cho dung THUONG MAI va cho THAY DOI KICH THUOC: CC0, Public
Domain, CC BY, CC BY-SA. Loai NC (phi thuong mai), ND (khong phai sinh), GFDL don
le va moi giay phep khong nhan ra duoc. Blog Muaban.net la trang thuong mai, va
WordPress tu cat anh thanh nhieu co — tuc la tao ban phai sinh.

    python scripts/image_search.py search "damselfly" --slug <slug>
    python scripts/image_search.py search "Crocothemis servilia" --slug <slug> --source commons
    python scripts/image_search.py fetch c003 --slug <slug> --position body-2 \\
        --name chuon-chuon-kim.jpg --alt "..." --caption "..." --purpose "..."
    python scripts/image_search.py list --slug <slug>

`search` tai anh xem truoc (640px) vao work/<slug>/images/_preview/ de agent MO RA
XEM truoc khi chon. Tieu de va tag cua anh tren kho khong dang tin: tim "dragonfly
window" tra ve ca mot file ten "Leaf Window". Khong xem anh thi khong duoc chon.

Ma thoat: 0 = xong, 1 = khong co ung vien dat / bi tu choi, 2 = sai cach goi.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, "work")

# Wikimedia yeu cau User-Agent co cach lien he. Dung trang blog, KHONG dung email
# nguoi dung — email chi de dinh danh, khong gui cho dich vu ben ngoai.
UA = "muaban-content-seo/1.0 (+https://muaban.net/blog)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OPENVERSE_API = "https://api.openverse.org/v1/images/"

PREVIEW_W = 640
FINAL_W = 1200          # WordPress tu sinh cac co nho hon tu ban nay
MIN_W_DEFAULT = 1000

MANIFEST_COLS = ["position", "file_name", "purpose", "source_url", "creator", "license",
                 "license_url", "retrieved_date", "alt_text", "caption", "rights_status"]


# --------------------------------------------------------------------------
# Giay phep
# --------------------------------------------------------------------------

def classify_license(text: str) -> tuple[str | None, str]:
    """Tra ve (nhom, ly do). nhom thuoc {CC0, PD, BY, BY-SA} hoac None = tu choi."""
    t = (text or "").strip().lower()
    if not t:
        return None, "khong co thong tin giay phep"
    compact = re.sub(r"[\s_]+", "-", t)
    if re.search(r"(^|-)nc(-|$)|noncommercial|non-commercial", compact):
        return None, "NC: cam dung thuong mai"
    if re.search(r"(^|-)nd(-|$)|noderiv|no-deriv", compact):
        return None, "ND: cam ban phai sinh, ma WordPress se cat anh thanh nhieu co"
    if "cc0" in compact or compact in ("zero", "cc-zero"):
        return "CC0", ""
    if compact in ("pdm", "pd", "public-domain") or "public-domain" in compact \
            or compact.startswith("pd-"):
        return "PD", ""
    if re.search(r"by-sa", compact):
        return "BY-SA", ""
    if re.search(r"(^|cc-)by(-|$)|^attribution$", compact):
        return "BY", ""
    if "gfdl" in compact:
        return None, "GFDL don le: phai kem ca van ban giay phep, khong kha thi tren blog"
    return None, f"giay phep khong nhan ra duoc: {text!r}"


def needs_attribution(group: str | None) -> bool:
    return group in ("BY", "BY-SA")


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


# --------------------------------------------------------------------------
# Mang
# --------------------------------------------------------------------------

def http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:           # noqa: S310
        return json.load(r)


def http_download(url: str, dest: str) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:           # noqa: S310
        data = r.read()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(data)
    return len(data)


# --------------------------------------------------------------------------
# Nguon: Wikimedia Commons
# --------------------------------------------------------------------------

def commons_query(params: dict, width: int) -> list[dict]:
    base = {"action": "query", "prop": "imageinfo", "format": "json",
            "iiprop": "url|extmetadata|size|mime", "iiurlwidth": width}
    base.update(params)
    data = http_json(COMMONS_API + "?" + urllib.parse.urlencode(base))
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        info = (p.get("imageinfo") or [{}])[0]
        em = info.get("extmetadata") or {}
        val = lambda k: (em.get(k) or {}).get("value", "")          # noqa: E731
        lic_text = val("LicenseShortName") or val("UsageTerms")
        group, why = classify_license(lic_text)
        creator = strip_html(val("Artist")) or strip_html(val("Credit"))
        out.append({
            "source": "commons",
            "ref": p.get("title", ""),
            "title": p.get("title", "").replace("File:", ""),
            "description": strip_html(val("ImageDescription"))[:300],
            "creator": creator,
            "license": lic_text.strip(),
            "license_url": val("LicenseUrl"),
            "license_group": group,
            "reject_reason": why,
            "restrictions": strip_html(val("Restrictions")),
            "width": info.get("width"),
            "height": info.get("height"),
            "mime": info.get("mime", ""),
            "landing_url": info.get("descriptionurl", ""),
            "image_url": info.get("thumburl") or info.get("url", ""),
        })
    return out


def commons_search(q: str, limit: int, width: int = PREVIEW_W) -> list[dict]:
    return commons_query({"generator": "search", "gsrsearch": f"{q} filetype:bitmap",
                          "gsrnamespace": 6, "gsrlimit": limit}, width)


def commons_file(title: str, width: int = FINAL_W) -> dict | None:
    res = commons_query({"titles": title}, width)
    return res[0] if res else None


# --------------------------------------------------------------------------
# Nguon: Openverse
# --------------------------------------------------------------------------

def _openverse_item(r: dict) -> dict:
    code = (r.get("license") or "").lower()
    ver = r.get("license_version") or ""
    lic_text = ("CC0 1.0" if code == "cc0" else "Public Domain Mark" if code == "pdm"
                else f"CC {code.upper()} {ver}".strip())
    group, why = classify_license(code)
    return {
        "source": "openverse",
        "ref": r.get("id", ""),
        "title": r.get("title") or "",
        "description": "",
        "creator": r.get("creator") or "",
        "license": lic_text,
        "license_url": r.get("license_url") or "",
        "license_group": group,
        "reject_reason": why,
        "restrictions": "",
        "width": r.get("width"),
        "height": r.get("height"),
        "mime": r.get("filetype") or "",
        "landing_url": r.get("foreign_landing_url") or "",
        "image_url": r.get("url") or "",
        "thumb_url": r.get("thumbnail") or "",
        "provider": r.get("source") or "",
    }


def openverse_search(q: str, limit: int) -> list[dict]:
    params = {"q": q, "license_type": "commercial,modification", "page_size": limit,
              "mature": "false"}
    data = http_json(OPENVERSE_API + "?" + urllib.parse.urlencode(params))
    return [_openverse_item(r) for r in data.get("results") or []]


def openverse_file(ident: str) -> dict | None:
    try:
        return _openverse_item(http_json(OPENVERSE_API + urllib.parse.quote(ident) + "/"))
    except urllib.error.HTTPError:
        return None


# --------------------------------------------------------------------------
# Kho ung vien cua mot bai
# --------------------------------------------------------------------------

def folder_of(slug: str) -> str:
    folder = os.path.join(WORK, slug)
    if not os.path.isdir(folder):
        raise SystemExit(f"[ANH] Khong co thu muc {folder}")
    return folder


def preview_dir(slug: str) -> str:
    return os.path.join(folder_of(slug), "images", "_preview")


def load_candidates(slug: str) -> dict:
    p = os.path.join(preview_dir(slug), "candidates.json")
    if os.path.isfile(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_candidates(slug: str, cands: dict) -> None:
    d = preview_dir(slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "candidates.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cands, fh, ensure_ascii=False, indent=2)


def ext_from(url: str, mime: str) -> str:
    path = urllib.parse.urlparse(url).path.lower()
    for e in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        if path.endswith(e):
            return ".jpg" if e == ".jpeg" else e
    return {"image/png": ".png", "image/webp": ".webp", "png": ".png"}.get(mime, ".jpg")


# --------------------------------------------------------------------------
# Lenh: search
# --------------------------------------------------------------------------

def cmd_search(args) -> int:
    results: list[dict] = []
    sources = ["commons", "openverse"] if args.source == "all" else [args.source]
    for s in sources:
        try:
            got = commons_search(args.query, args.limit) if s == "commons" \
                else openverse_search(args.query, args.limit)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"[ANH] {s}: loi mang, bo qua ({exc})")
            continue
        results.extend(got)

    cands = load_candidates(args.slug)
    n_next = len(cands) + 1
    shown = kept = 0
    print(f"[ANH] \"{args.query}\" — {len(results)} ket qua tho\n")
    for r in results:
        shown += 1
        w = r.get("width") or 0
        if r["license_group"] is None:
            print(f"  loai  {r['title'][:60]}  ({r['reject_reason']})")
            continue
        if w and w < args.min_width:
            print(f"  loai  {r['title'][:60]}  (rong {w}px < {args.min_width}px)")
            continue
        if needs_attribution(r["license_group"]) and not r["creator"]:
            print(f"  loai  {r['title'][:60]}  ({r['license']} nhung khong ro tac gia, "
                  "khong ghi cong duoc)")
            continue

        # Trung ung vien da co thi dung lai ma cu
        cid = next((k for k, v in cands.items()
                    if v["source"] == r["source"] and v["ref"] == r["ref"]), None)
        if not cid:
            cid = f"c{n_next:03d}"
            n_next += 1
        prev_url = r.get("thumb_url") or r["image_url"]
        prev_path = os.path.join(preview_dir(args.slug), f"{cid}{ext_from(prev_url, r['mime'])}")
        if not os.path.isfile(prev_path):
            try:
                http_download(prev_url, prev_path)
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"  loai  {r['title'][:60]}  (khong tai duoc anh xem truoc: {exc})")
                continue
        r["preview"] = os.path.relpath(prev_path, ROOT).replace("\\", "/")
        r["query"] = args.query
        cands[cid] = r
        kept += 1

        attr = "can ghi cong" if needs_attribution(r["license_group"]) else "khong bat buoc ghi cong"
        print(f"  {cid}  [{r['source']}] {r['title'][:70]}")
        print(f"        {r.get('width')}x{r.get('height')} | {r['license']} ({attr}) | "
              f"tac gia: {r['creator'][:50] or '-'}")
        if r.get("restrictions"):
            print(f"        HAN CHE: {r['restrictions'][:120]}")
        if r.get("description"):
            print(f"        mo ta: {r['description'][:140]}")
        print(f"        xem truoc: {r['preview']}")
    save_candidates(args.slug, cands)
    print(f"\n[ANH] {kept} ung vien dat giay phep. MO TUNG ANH XEM TRUOC ra nhin truoc khi chon.")
    return 0 if kept else 1


# --------------------------------------------------------------------------
# Lenh: fetch
# --------------------------------------------------------------------------

def read_manifest(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_manifest(path: str, rows: list[dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=MANIFEST_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in MANIFEST_COLS})
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())


def safe_name(name: str) -> str:
    base, ext = os.path.splitext(name.lower())
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base, ext


def cmd_fetch(args) -> int:
    cands = load_candidates(args.slug)
    c = cands.get(args.candidate)
    if not c:
        print(f"[ANH] Khong co ung vien {args.candidate}. Chay `search` truoc.")
        return 2

    # Hoi lai nguon: giay phep co the da doi tu luc tim, va can ban 1200px
    fresh = commons_file(c["ref"]) if c["source"] == "commons" else openverse_file(c["ref"])
    if not fresh:
        print(f"[ANH] Khong con tim thay {c['ref']} o nguon. Bo ung vien nay.")
        return 1
    group, why = classify_license(fresh["license"] if fresh["source"] == "commons"
                                  else fresh["license"])
    if group is None:
        print(f"[ANH] TU CHOI {args.candidate}: {why}")
        return 1
    if needs_attribution(group) and not fresh["creator"]:
        print(f"[ANH] TU CHOI {args.candidate}: {fresh['license']} ma khong ro tac gia.")
        return 1

    # Openverse gom tu nhieu kho; giay phep phai duoc kiem o trang goc.
    status = "CLEARED"
    if fresh["source"] == "openverse" and not args.verified:
        status = "BLOCKED"

    cap_words = len(args.caption.split())
    if not 7 <= cap_words <= 20:
        print(f"[ANH] Chu thich dai {cap_words} tu, bai that dung 7-20 tu. Viet lai.")
        return 2

    folder = folder_of(args.slug)
    base, _ = safe_name(args.name)
    ext = ext_from(fresh["image_url"], fresh["mime"])
    file_name = f"{base}{ext}"
    dest = os.path.join(folder, "images", file_name)
    size = http_download(fresh["image_url"], dest)

    manifest = os.path.join(folder, "image-manifest.csv")
    rows = [r for r in read_manifest(manifest)
            if (r.get("file_name") or "").strip() and r.get("position") != args.position]
    rows.append({
        "position": args.position,
        "file_name": file_name,
        "purpose": args.purpose,
        "source_url": fresh["landing_url"],
        "creator": fresh["creator"],
        "license": fresh["license"],
        "license_url": fresh["license_url"],
        "retrieved_date": dt.date.today().isoformat(),
        "alt_text": args.alt,
        "caption": args.caption,
        "rights_status": status,
    })
    order = {"hero": 0}
    rows.sort(key=lambda r: (order.get(r["position"], 1),
                             int(re.sub(r"\D", "", r["position"]) or 0)))
    write_manifest(manifest, rows)

    print(f"[ANH] Da tai {file_name} ({size // 1024} KB) — {fresh['license']} — {status}")
    if status == "BLOCKED":
        print(f"      Anh tu Openverse: mo {fresh['landing_url']} kiem giay phep o trang goc,")
        print("      roi chay lai lenh nay voi --verified de dat CLEARED.")
    print("\nChen vao bai (dong trong giua anh va chu thich):\n")
    print(f"![{args.alt}](images/{file_name})\n")
    print(f"*{args.caption}*")
    return 0


# --------------------------------------------------------------------------
# Lenh: list
# --------------------------------------------------------------------------

def cmd_list(args) -> int:
    folder = folder_of(args.slug)
    rows = [r for r in read_manifest(os.path.join(folder, "image-manifest.csv"))
            if (r.get("file_name") or "").strip()]
    if not rows:
        print("[ANH] Manifest trong.")
        return 0
    for r in rows:
        exists = os.path.isfile(os.path.join(folder, "images", r["file_name"]))
        print(f"  {r['position']:8s} {r['rights_status']:8s} {r['file_name']:40s} "
              f"{r['license']:14s} {'' if exists else 'THIEU FILE'}")
    return 0


def main() -> int:
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    ap = argparse.ArgumentParser(description="Tim anh co giay phep va ghi manifest")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="tim anh va tai ban xem truoc")
    s.add_argument("query")
    s.add_argument("--slug", required=True)
    s.add_argument("--source", choices=["commons", "openverse", "all"], default="all")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--min-width", type=int, default=MIN_W_DEFAULT)

    f = sub.add_parser("fetch", help="tai anh da chon va ghi manifest")
    f.add_argument("candidate")
    f.add_argument("--slug", required=True)
    f.add_argument("--position", required=True, help="hero, body-1, body-2, ...")
    f.add_argument("--name", required=True, help="ten file khong dau, vd chuon-chuon-kim.jpg")
    f.add_argument("--alt", required=True, help="mo ta dung noi dung anh")
    f.add_argument("--caption", required=True, help="7-20 tu, gan voi y cua muc")
    f.add_argument("--purpose", required=True, help="anh nay giai thich duoc gi")
    f.add_argument("--verified", action="store_true",
                   help="chi voi Openverse: da mo trang goc va xac nhan giay phep")

    l = sub.add_parser("list", help="xem manifest cua bai")
    l.add_argument("--slug", required=True)

    args = ap.parse_args()
    return {"search": cmd_search, "fetch": cmd_fetch, "list": cmd_list}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
