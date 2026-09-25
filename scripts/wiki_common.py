"""Doc va phan tich trang wiki tri thuc.

Wiki la lop tri thuc ben lau nam giua nguon goc va bai viet. No KHONG phai nguon.
Moi claim tren trang wiki deu phai mang theo source_url, supporting_quote nguyen van
va retrieved_date, de bai viet luon trich dan NGUON GOC chu khong trich dan wiki.

Dinh dang mot trang:

    ---
    id: nghi-dinh-50-2026
    type: van-ban
    title: "Nghi dinh 50/2026/ND-CP"
    status: con-hieu-luc
    updated: 2026-09-16
    related: [tien-su-dung-dat]
    used_in: [chi-phi-chuyen-dat-nong-nghiep-len-tho-cu-2026]
    ---

    # Tieu de

    ## Mot muc bat ky

    ### C: Cau claim, viet dung nhu se dung trong bai
    - source_url: https://...
    - source_type: LAW
    - published_date: 2026-02-14
    - retrieved_date: 2026-09-15
    - supporting_quote: "doan nguyen van trong nguon"
    - status: VERIFIED

Ten truong trung khop voi cot cua evidence-ledger.csv, de mot claim tren wiki
chuyen thang thanh mot dong ledger ma khong phai dich ten.
"""

from __future__ import annotations

import datetime as dt
import os
import re
from dataclasses import dataclass, field

# Loai trang <-> ten thu muc.
VALID_TYPES = ("van-ban", "khai-niem", "dia-ban", "so-lieu", "tong-hop")

# Tinh trang cua trang. 'khong-ap-dung' danh cho trang khai niem, khong co hieu luc phap ly.
VALID_PAGE_STATUS = ("con-hieu-luc", "het-hieu-luc", "sua-doi", "chua-ro", "khong-ap-dung")

# Dung chung tu vung voi evidence-ledger.csv.
VALID_CLAIM_STATUS = ("VERIFIED", "PARTIAL", "GAP")
VALID_SOURCE_TYPES = ("LAW", "GOV", "STATS", "REPORT", "NEWS", "MARKETPLACE", "NONE")
PRIMARY_SOURCES = ("LAW", "GOV", "STATS")

REQUIRED_META = ("id", "type", "title", "status", "updated")
DATE_META = ("updated", "review_after", "effective_from")
LIST_META = ("related", "used_in", "supersedes")
CLAIM_DATE_FIELDS = ("published_date", "retrieved_date", "effective_date")

MIN_QUOTE_CHARS = 25

# Nhip ra soat: so lieu cu nhanh hon van ban phap luat.
STALE_DAYS = {"so-lieu": 180, "dia-ban": 270}
STALE_DAYS_DEFAULT = 400

VALID_LOG_ACTIONS = ("INGEST", "UPDATE", "QUERY", "LINT", "RETIRE")

FRONT_MATTER_FENCE = "---"
CLAIM_RE = re.compile(r"^###\s*C\s*[:—-]\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^\s*[-*]\s*([a-z_]+)\s*:\s*(.*)$")
WIKI_LINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9-]*)(?:\|[^\]]*)?\]\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOG_LINE_RE = re.compile(
    r"^-\s*(\d{4}-\d{2}-\d{2})\s*·\s*([A-Z]+)\s*·\s*([a-z0-9-]+|—)\s*·\s*(.+)$"
)


# --------------------------------------------------------------------------
# Parse
# --------------------------------------------------------------------------

def strip_inline_comment(raw: str) -> str:
    """Cat phan chu thich sau dau '#', nhung khong cat dau '#' nam trong nhay."""
    out = []
    quote = ""
    i = 0
    while i < len(raw):
        ch = raw[i]
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or raw[i - 1].isspace()):
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out).strip()


def clean_scalar(raw: str) -> str:
    value = strip_inline_comment(raw)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def parse_inline_list(raw: str) -> list[str]:
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return []
    return [clean_scalar(part) for part in inner.split(",") if clean_scalar(part)]


def parse_front_matter(lines: list[str]) -> tuple[dict, int]:
    """Tra ve (meta, so dong da tieu thu). Khong co front matter thi tra ({}, 0)."""
    if not lines or lines[0].strip() != FRONT_MATTER_FENCE:
        return {}, 0

    meta: dict = {}
    key = ""
    for n, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONT_MATTER_FENCE:
            return meta, n + 1
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- ") and key:
            item = clean_scalar(stripped[2:])
            if item:
                meta.setdefault(key, [])
                if isinstance(meta[key], list):
                    meta[key].append(item)
            continue
        if ":" not in stripped:
            continue
        key, _, raw = stripped.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            meta[key] = parse_inline_list(raw)
        elif raw == "":
            meta[key] = [] if key in LIST_META else ""
        else:
            meta[key] = clean_scalar(raw)
    return meta, len(lines)


@dataclass
class Claim:
    text: str
    line: int
    fields: dict = field(default_factory=dict)

    def get(self, key: str) -> str:
        return (self.fields.get(key) or "").strip()


@dataclass
class Page:
    path: str
    rel_path: str
    page_id: str
    meta: dict = field(default_factory=dict)
    claims: list = field(default_factory=list)
    links: list = field(default_factory=list)
    parse_error: str = ""

    @property
    def page_type(self) -> str:
        return (self.meta.get("type") or "").strip()

    @property
    def title(self) -> str:
        return (self.meta.get("title") or "").strip()

    @property
    def status(self) -> str:
        return (self.meta.get("status") or "").strip()

    def meta_list(self, key: str) -> list[str]:
        value = self.meta.get(key)
        if isinstance(value, list):
            return [v for v in value if v]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def count_status(self, status: str) -> int:
        return sum(1 for c in self.claims if c.get("status").upper() == status)


def parse_page(path: str, root: str) -> Page:
    rel_path = os.path.relpath(path, root).replace("\\", "/")
    with open(path, "r", encoding="utf-8-sig") as fh:
        lines = fh.read().splitlines()

    meta, consumed = parse_front_matter(lines)
    page = Page(path=path, rel_path=rel_path,
                page_id=(meta.get("id") or "").strip(), meta=meta)
    if not consumed:
        page.parse_error = "Thieu front matter (khoi '---' o dau file)."
        return page

    current: Claim | None = None
    in_fence = False
    for n, line in enumerate(lines[consumed:], start=consumed + 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for target in WIKI_LINK_RE.findall(line):
            if target not in page.links:
                page.links.append(target)

        m = CLAIM_RE.match(line)
        if m:
            current = Claim(text=m.group(1).strip(), line=n)
            page.claims.append(current)
            continue

        if line.startswith("#"):
            current = None
            continue

        if current is not None:
            fm = FIELD_RE.match(line)
            if fm:
                current.fields[fm.group(1)] = clean_scalar(fm.group(2))
            elif line.strip():
                # Van xuoi giua cac claim khong lam hong khoi, chi ket thuc no.
                if not line.lstrip().startswith(("-", "*", ">")):
                    current = None
    return page


def load_pages(wiki_root: str) -> list[Page]:
    pages: list[Page] = []
    for type_dir in VALID_TYPES:
        folder = os.path.join(wiki_root, type_dir)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".md") or name.startswith("_"):
                continue
            pages.append(parse_page(os.path.join(folder, name), wiki_root))
    return pages


# --------------------------------------------------------------------------
# Tien ich
# --------------------------------------------------------------------------

def parse_date(value: str):
    value = (value or "").strip()
    if not DATE_RE.match(value):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def days_since(value: str, today: dt.date | None = None):
    parsed = parse_date(value)
    if parsed is None:
        return None
    return ((today or dt.date.today()) - parsed).days


def stale_limit(page_type: str) -> int:
    return STALE_DAYS.get(page_type, STALE_DAYS_DEFAULT)


def work_slugs(work_root: str) -> set[str]:
    if not os.path.isdir(work_root):
        return set()
    return {name for name in os.listdir(work_root)
            if os.path.isdir(os.path.join(work_root, name))}


def ledger_refs(work_root: str) -> list[tuple[str, str, str]]:
    """Tra ve [(slug, claim_id, wiki_ref)] cho moi dong ledger co wiki_ref."""
    import csv

    refs: list[tuple[str, str, str]] = []
    if not os.path.isdir(work_root):
        return refs
    for slug in sorted(work_slugs(work_root)):
        path = os.path.join(work_root, slug, "evidence-ledger.csv")
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        for row in rows:
            ref = (row.get("wiki_ref") or "").strip()
            if ref:
                refs.append((slug, (row.get("claim_id") or "").strip(), ref))
    return refs


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
