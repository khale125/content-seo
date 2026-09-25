"""Kho URL de di internal link, nhap tu sheet "BDS MBN" cua file tu khoa noi bo.

  python scripts/internal_links.py build --from <file.csv>     # nhap / lam moi kho
  python scripts/internal_links.py find "phong tro quan 10"    # tra URL phu hop
  python scripts/internal_links.py find --brief work/<slug>/brief.yaml
  python scripts/internal_links.py stats

Kho nam o `reference/internal-links-mbn.csv`, nguon goc ghi o
`reference/internal-links-mbn.meta.json`. Lam moi bang cach tai lai sheet:

  curl -sL "https://docs.google.com/spreadsheets/d/<id>/export?format=csv&gid=0" -o bds-mbn.csv
  python scripts/internal_links.py build --from bds-mbn.csv

Ba dieu da do tren chinh du lieu sheet, va chung quyet dinh cach doc file nay:

1. **Cot `URL` va `Keyword muc tieu` dang tin.** Tren 366 dong ma keyword co nhac ten
   tinh, khong dong nao co URL danh muc tro sai tinh do (0/366).
2. **Cot `Tinh/Tp` va `Quan Huyen` thi khong.** 24/1.076 dong danh muc ghi tinh khac
   voi tinh trong URL, va voi trang `/tags/` thi lech 47/51 — o day cot tinh gan nhu
   la nhieu. Vi vay dia ban dung de tra cuu duoc **suy ra tu slug URL**, con cot cua
   sheet chi giu lai o `sheet_province`/`sheet_district` de doi chieu.
3. **Cot `SubCate 2` mau thuan voi URL o 58 dong** (ghi "Mua ban nha dat" trong khi URL
   la `cho-thue-...` va nguoc lai). Nen loai giao dich (ban / cho thue) cung suy tu slug.

Khong dong nao bi sua noi dung: dong co URL rong thi bo qua va bao so luong, khong doan
URL thay cho nguoi nhap (quy tac 1).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(ROOT, "reference", "internal-links-mbn.csv")
META = os.path.join(ROOT, "reference", "internal-links-mbn.meta.json")
# Nguon goc cua kho, ghi vao meta de sau nay con biet lam moi tu dau. Chi doc tab
# "BDS MBN" (gid=0); tab "BDS Mogi" trong cung file la du lieu doi thu, khong dung.
SOURCE_SHEET = ("https://docs.google.com/spreadsheets/d/"
                "1tJhYa4rs7Habd_h4gY-q47czG_fTQKglB8LwrHxkq24/edit?gid=0")

STORE_FIELDS = [
    "keyword", "volume", "url", "kind", "deal", "property_type",
    "province", "district", "rank_latest", "cate2", "cate3",
    "sheet_province", "sheet_district",
]

# TPHCM la ten duy nhat trong sheet khong slug hoa thang ra slug cua URL.
PROVINCE_ALIAS = {"tphcm": "ho-chi-minh", "tp hcm": "ho-chi-minh",
                  "tp. hcm": "ho-chi-minh", "sai gon": "ho-chi-minh",
                  "hcm": "ho-chi-minh", "toan quoc": ""}

# Loai bat dong san. Thu tu quan trong: cum dai dung truoc cum ngan, vi
# "cho-thue-nha-tro-phong-tro" cung chua "nha".
PROPERTY_PATTERNS = [
    ("nha-tro-phong-tro", "nha tro, phong tro"),
    ("phong-tro", "nha tro, phong tro"),
    ("can-ho-chung-cu", "can ho"),
    ("chung-cu", "can ho"),
    ("can-ho", "can ho"),
    ("van-phong", "van phong"),
    ("mat-bang", "mat bang, cua hang"),
    ("cua-hang", "mat bang, cua hang"),
    ("shophouse", "mat bang, cua hang"),
    ("nha-xuong", "nha xuong, kho"),
    ("nha-kho", "nha xuong, kho"),
    ("kho-bai", "nha xuong, kho"),
    ("biet-thu", "biet thu, villa"),
    ("villa", "biet thu, villa"),
    ("nha-mat-tien", "nha mat tien"),
    ("nha-mat-pho", "nha mat tien"),
    ("dat-nen", "dat"),
    ("nha-dat", "nha dat"),
    ("quan-ca-phe", "sang nhuong quan"),
    ("quan-an", "sang nhuong quan"),
    ("nha", "nha"),
    ("dat", "dat"),
]

# Cach nguoi viet go ten dia ban trong truy van, doi sang slug cua URL. Khong co bang
# nay thi "TP.HCM" khong khop "ho-chi-minh" va tra cuu tra ve trang toan quoc.
QUERY_ALIAS = {
    "tphcm": "ho-chi-minh", "tp-hcm": "ho-chi-minh", "hcm": "ho-chi-minh",
    "sai-gon": "ho-chi-minh", "sg": "ho-chi-minh", "ho-chi-minh": "ho-chi-minh",
    "hn": "ha-noi", "ha-noi": "ha-noi",
    "q1": "quan-1", "q2": "quan-2", "q3": "quan-3", "q4": "quan-4", "q5": "quan-5",
    "q6": "quan-6", "q7": "quan-7", "q8": "quan-8", "q9": "quan-9", "q10": "quan-10",
    "q11": "quan-11", "q12": "quan-12",
}

DISTRICT_RE = re.compile(r"\b((?:quan|huyen|thi-xa|thanh-pho|tp)-[a-z0-9]+(?:-[a-z0-9]+)?)")
# "quan-ca-phe" la quan ca phe, khong phai quan noi thanh. Bay cum nay deu den tu nhom
# "Sang nhuong cua hang", nen liet ke thay vi doan theo do dai token.
NOT_DISTRICT = ("quan-ca-phe", "quan-an", "quan-bar", "quan-karaoke", "quan-cafe",
                "quan-tra-sua", "quan-an-uong")


def nod(text: str) -> str:
    """Bo dau, ha chu thuong. Giu nguyen khoang trang."""
    s = unicodedata.normalize("NFD", text or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower().strip()


def to_slug(text: str) -> str:
    s = nod(text)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def province_slug(name: str) -> str:
    key = nod(name)
    if key in PROVINCE_ALIAS:
        return PROVINCE_ALIAS[key]
    return to_slug(name)


def load_province_vocab(rows: list[dict]) -> list[str]:
    """Tu vung tinh lay tu chinh du lieu, khong viet tay danh sach 63 tinh."""
    vocab = set()
    for row in rows:
        name = (row.get("province") or row.get("sheet_province") or "").strip()
        if name:
            # Luon di qua province_slug: "TPHCM" phai ra "ho-chi-minh", va
            # "Toan quoc" phai ra chuoi rong. Bo qua buoc nay tung lam tu vung
            # thieu dung tinh dong nhat trong kho, keo theo quan/huyen suy sai.
            vocab.add(province_slug(name))
    vocab.discard("")
    # Cum dai truoc de "ba-ria-vung-tau" khong bi "vung-tau" an truoc.
    return sorted(vocab, key=len, reverse=True)


def parse_url(url: str, vocab: list[str]) -> dict:
    """Suy loai trang, loai giao dich, loai bat dong san va dia ban tu slug URL."""
    low = url.lower()
    kind = "tag" if "/tags/" in low else "cate"
    slug = low.rstrip("/").rsplit("/", 1)[-1]

    if re.search(r"(^|-)cho-thue|^thue-|-thue-", slug):
        deal = "cho thue"
    elif re.search(r"^ban-|^mua-ban-|-ban-", slug):
        deal = "ban"
    elif slug.startswith("sang-nhuong"):
        deal = "sang nhuong"
    else:
        deal = ""

    ptype = ""
    for needle, label in PROPERTY_PATTERNS:
        if needle in slug:
            ptype = label
            break

    province = next((p for p in vocab if p and (slug.endswith(p) or f"-{p}-" in slug
                                                or slug == p)), "")
    # Cat duoi tinh TRUOC khi do quan/huyen. Khong cat thi
    # "...-quan-7-ho-chi-minh" ra "quan-7-ho", vi regex an sang token dau cua ten tinh.
    rest = slug
    if province:
        # Go MOI cho xuat hien cua ten tinh, khong chi duoi slug: tren trang /tags/
        # ten tinh hay nam giua, vi du "...-quan-7-ho-chi-minh-duoi-3-ty".
        rest = re.sub(rf"-?{re.escape(province)}", "", slug).strip("-")
    district = ""
    for m in DISTRICT_RE.finditer(rest):
        if any(m.group(1).startswith(x) for x in NOT_DISTRICT):
            continue
        district = m.group(1)
        break
    return {"kind": kind, "deal": deal, "property_type": ptype,
            "province": province, "district": district}


# ----------------------------------------------------------------- build

def latest_rank(row: dict) -> str:
    """Rank cua tuan gan nhat co so. Sheet co ~35 cot Rank Wn, chi giu lai mot."""
    weeks = sorted((int(m.group(1)), k) for k in row
                   for m in [re.match(r"Rank W(\d+)$", k or "")] if m)
    for _, key in reversed(weeks):
        val = (row.get(key) or "").strip()
        if val and val.lower() != "not in top 30":
            return val
        if val:
            return "ngoai top 30"
    return ""


def build(source: str, url_mode: bool) -> int:
    if url_mode:
        with urllib.request.urlopen(source, timeout=120) as resp:   # noqa: S310
            raw = resp.read().decode("utf-8", "replace")
        lines = raw.splitlines()
    else:
        with open(source, encoding="utf-8-sig", newline="") as fh:
            lines = fh.read().splitlines()

    reader = csv.DictReader(lines)
    raw_rows = list(reader)
    if not raw_rows:
        print("[LINK] file nguon rong", file=sys.stderr)
        return 2

    # Vong mot: lay tu vung tinh tu cot cua sheet de con suy dia ban tu slug.
    vocab = load_province_vocab([{"sheet_province": r.get("Tỉnh/Tp") or ""}
                                 for r in raw_rows])

    out: dict[tuple[str, str], dict] = {}
    skipped_no_url = repaired = 0
    for row in raw_rows:
        url = (row.get("URL") or "").strip()
        keyword = (row.get("Keyword mục tiêu") or "").strip()
        if not url:
            skipped_no_url += 1
            continue
        # Loi dan mot lan trong sheet: tien to bi lap doi. Sua deterministic, khong doan.
        fixed = re.sub(r"^https?://muaban\.nethttps?://", "https://", url)
        if fixed != url:
            repaired += 1
            url = fixed
        if not url.startswith("http"):
            skipped_no_url += 1
            continue

        parsed = parse_url(url, vocab)
        rec = {
            "keyword": keyword,
            "volume": (row.get("Volume") or "").strip(),
            "url": url,
            "rank_latest": latest_rank(row),
            "cate2": (row.get("SubCate 2") or "").strip(),
            "cate3": (row.get("SubCate 3") or "").strip(),
            "sheet_province": (row.get("Tỉnh/Tp") or "").strip(),
            "sheet_district": (row.get("Quận Huyện") or "").strip(),
        }
        rec.update(parsed)
        key = (url.lower(), nod(keyword))
        out.setdefault(key, rec)

    rows = sorted(out.values(),
                  key=lambda r: (r["province"], r["deal"], r["property_type"],
                                 -vol_num(r["volume"]), r["keyword"]))
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=STORE_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in STORE_FIELDS})

    import datetime
    meta = {
        "source_sheet": SOURCE_SHEET,
        "imported_from": source if url_mode else os.path.basename(source),
        "imported_at": datetime.date.today().isoformat(),
        "sheet": "BĐS MBN",
        "rows_in_sheet": len(raw_rows),
        "rows_stored": len(rows),
        "skipped_no_url": skipped_no_url,
        "url_prefix_repaired": repaired,
        "unique_urls": len({r["url"].lower() for r in rows}),
        "with_province": sum(1 for r in rows if r["province"]),
        "with_district": sum(1 for r in rows if r["district"]),
        "cate_pages": sum(1 for r in rows if r["kind"] == "cate"),
        "tag_pages": sum(1 for r in rows if r["kind"] == "tag"),
    }
    with open(META, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    print(f"[LINK] {len(rows)} dong vao kho ({meta['unique_urls']} URL khac nhau)")
    print(f"       bo qua {skipped_no_url} dong khong co URL, "
          f"sua {repaired} URL bi lap tien to")
    print(f"       suy duoc tinh cho {meta['with_province']} dong, "
          f"quan/huyen cho {meta['with_district']} dong")
    print(f"       {meta['cate_pages']} trang danh muc, {meta['tag_pages']} trang tag")
    print(f"       kho:  {STORE}")
    return 0


def vol_num(text: str) -> float:
    """Volume trong sheet viet kieu '49.500' hoac '1.900'. Doc thanh so de xep hang."""
    s = re.sub(r"[^0-9]", "", text or "")
    return float(s) if s else 0.0


def rank_num(text: str) -> float:
    s = re.sub(r"[^0-9]", "", text or "")
    return float(s) if s else 999.0


# ------------------------------------------------------------------ find

STOP = {"o", "tai", "gan", "cho", "va", "cua", "khu", "vuc", "nao", "the",
        "kinh", "nghiem", "gia", "bao", "nhieu", "nhu"}


def load_store() -> list[dict]:
    if not os.path.isfile(STORE):
        print(f"[LINK] chua co kho. Chay: python scripts/internal_links.py build "
              f"--from <file.csv>", file=sys.stderr)
        return []
    with open(STORE, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", nod(text)) if t and t not in STOP]


def score(row: dict, q_tokens: list[str], q_slug: str, vocab: list[str]) -> float:
    kw = set(tokens(row["keyword"]))
    slug_tokens = set(tokens(row["url"].rsplit("/", 1)[-1]))
    hit = sum(1 for t in q_tokens if t in kw)
    hit_slug = sum(1 for t in q_tokens if t in slug_tokens and t not in kw)
    s = hit * 3.0 + hit_slug * 1.5

    if row["province"] and row["province"] in q_slug:
        s += 6.0
    elif row["province"]:
        s -= 2.0                      # tro sai tinh thi te hon la khong co tinh
    if row["district"] and row["district"] in q_slug:
        s += 8.0
    elif row["district"]:
        # Tru manh: bai khong nhac quan nao thi trang cap tinh hoac toan quoc dung hon
        # trang cua mot quan bat ky. Muc -3 tung lam trang Hoc Mon ngang diem voi trang
        # cap TPHCM cho mot bai khong he nhac Hoc Mon.
        s -= 6.0

    if row["deal"] and all(t in q_tokens for t in tokens(row["deal"])):
        s += 4.0
    if row["property_type"]:
        pt = tokens(row["property_type"])
        if pt and sum(1 for t in pt if t in q_tokens) >= max(1, len(pt) - 1):
            s += 4.0
    if row["kind"] == "cate":
        # docs/05 doi internal link tro toi DANH MUC dung dia ban va loai hinh, nen
        # trang danh muc thang trang tag khi diem xap xi. Can trang tag thi dung --kind tag.
        s += 3.0
    s += min(vol_num(row["volume"]), 50000) / 50000.0        # pha the bang volume
    return s


def find(query: str, limit: int, kind: str | None) -> int:
    rows = load_store()
    if not rows:
        return 2
    vocab = load_province_vocab(rows)
    q_tokens = tokens(query)
    q_slug = to_slug(query)
    for alias, slug in QUERY_ALIAS.items():
        if re.search(rf"(^|-){re.escape(alias)}(-|$)", q_slug) and slug not in q_slug:
            q_slug += "-" + slug
    # "quan 10" go roi thanh hai token nen slug da co "quan-10"; nhung "quan10" hay
    # "q10" thi khong, va ca hai deu xuat hien trong brief that.
    if not q_tokens:
        print("[LINK] truy van rong", file=sys.stderr)
        return 2

    scored = [(score(r, q_tokens, q_slug, vocab), r) for r in rows
              if not kind or r["kind"] == kind]
    scored.sort(key=lambda x: (-x[0], rank_num(x[1]["rank_latest"])))
    # Mot URL co nhieu dong keyword. Di internal link thi can MOT URL, nen gop lai va
    # giu dong diem cao nhat lam anchor de xuat; so keyword con lai chi de tham khao.
    best: dict[str, tuple[float, dict, int]] = {}
    for sc, row in scored:
        key = row["url"].lower()
        if key in best:
            prev = best[key]
            best[key] = (prev[0], prev[1], prev[2] + 1)
        else:
            best[key] = (sc, row, 1)
    top = sorted(best.values(), key=lambda x: (-x[0], rank_num(x[1]["rank_latest"])))
    top = [(sc, row, n) for sc, row, n in top if sc > 3.0][:limit]
    if not top:
        print(f'[LINK] khong co URL nao khop "{query}". Noi truy van rong hon, '
              f"hoac kiem lai bang: internal_links.py find \"<loai hinh> <dia ban>\"")
        return 1

    print(f'[LINK] {len(top)} URL khop nhat voi "{query}"\n')
    for s, r, n in top:
        dia = " · ".join(x for x in (r["province"], r["district"]) if x) or "toan quoc"
        them = f" (+{n - 1} keyword khac cung tro ve URL nay)" if n > 1 else ""
        print(f"  {s:5.1f}  {r['url']}")
        print(f"         anchor de xuat: \"{r['keyword']}\"{them}")
        print(f"         {r['kind']} · {r['deal'] or '-'} · "
              f"{r['property_type'] or '-'} · {dia} · "
              f"vol={r['volume'] or '-'} · rank={r['rank_latest'] or '-'}")
    print("\n  Anchor phai mo ta dich den va doc tu nhien trong cau — dung nguyen cum"
          "\n  keyword khi no doc duoc, dung nhoi nguyen van neu cau khong chiu noi.")
    return 0


def stats() -> int:
    rows = load_store()
    if not rows:
        return 2
    meta = {}
    if os.path.isfile(META):
        with open(META, encoding="utf-8") as fh:
            meta = json.load(fh)
    print(f"[LINK] kho: {STORE}")
    for k, v in meta.items():
        print(f"       {k:22}: {v}")
    import collections
    for col, title in (("deal", "loai giao dich"), ("property_type", "loai bat dong san")):
        c = collections.Counter(r[col] or "-" for r in rows)
        print(f"\n  {title}:")
        for k, v in c.most_common(12):
            print(f"     {v:5d}  {k}")
    c = collections.Counter(r["province"] or "-" for r in rows)
    print("\n  tinh (top 12):")
    for k, v in c.most_common(12):
        print(f"     {v:5d}  {k}")
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                          # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="Kho URL internal link cua Muaban.net.")
    sub = ap.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="nhap tu ban xuat CSV cua sheet BDS MBN")
    b.add_argument("--from", dest="src", required=True,
                   help="duong dan file CSV, hoac URL export neu dung --url")
    b.add_argument("--url", action="store_true", help="coi --from la URL de tai ve")

    f = sub.add_parser("find", help="tra URL phu hop noi dung bai")
    f.add_argument("query", nargs="?", default="")
    f.add_argument("--brief", default=None, help="lay truy van chinh tu brief.yaml")
    f.add_argument("--limit", type=int, default=5)
    f.add_argument("--kind", choices=["cate", "tag"], default=None)

    sub.add_parser("stats", help="xem kho co gi")
    args = ap.parse_args()

    if args.cmd == "build":
        return build(args.src, args.url)
    if args.cmd == "find":
        query = args.query
        if args.brief:
            sys.path.insert(0, HERE)
            from qa_common import load_simple_yaml
            brief = load_simple_yaml(args.brief)
            query = " ".join(x for x in [query, str(brief.get("primary_query") or "")] if x)
        return find(query, args.limit, args.kind)
    if args.cmd == "stats":
        return stats()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
