"""Shared helpers for the content-seo QA scripts.

Markdown parsing, finding records, and console reporting. The content is
Vietnamese, so everything is UTF-8 and diacritic-aware.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Iterable

BLOCK = "BLOCK"
WARN = "WARN"
INFO = "INFO"
SEVERITY_ORDER = {BLOCK: 0, WARN: 1, INFO: 2}

LEXICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexicon", "ai_phrases.json")


def force_utf8_stdout() -> None:
    """Windows consoles default to a legacy code page and mangle Vietnamese."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name)
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, io.UnsupportedOperation):
            pass


@dataclass
class Finding:
    check: str
    severity: str
    message: str
    line: int = 0
    snippet: str = ""
    guidance: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Report:
    name: str
    findings: list[Finding] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def add(self, check: str, severity: str, message: str, line: int = 0,
            snippet: str = "", guidance: str = "") -> None:
        self.findings.append(Finding(check, severity, message, line, snippet, guidance))

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    @property
    def blocked(self) -> bool:
        return self.count(BLOCK) > 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "metrics": self.metrics,
            "findings": [f.to_dict() for f in self.findings],
            "block_count": self.count(BLOCK),
            "warn_count": self.count(WARN),
        }


# --------------------------------------------------------------------------
# Markdown parsing
# --------------------------------------------------------------------------

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LIST_ITEM_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_LINK_RE = re.compile(r"<a\s[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", re.I | re.S)
CLAIM_REF_RE = re.compile(r"\[(C\d{1,3})\]")


@dataclass
class Heading:
    level: int
    text: str
    line: int


@dataclass
class Block:
    """A paragraph, list, table, quote or heading, with its source line."""
    kind: str
    text: str
    line: int
    items: list[str] = field(default_factory=list)


@dataclass
class Document:
    path: str
    raw: str
    front_matter: dict
    lines: list[str]
    headings: list[Heading]
    blocks: list[Block]
    body_text: str

    def line_of(self, needle: str, start: int = 0) -> int:
        low = needle.lower()
        for idx in range(start, len(self.lines)):
            if low in self.lines[idx].lower():
                return idx + 1
        return 0


def _clean_scalar(value: str) -> str:
    """Gia tri cua mot dong `key: value`, da bo ngoac va bo chu thich duoi dong.

    Phai bo chu thich, neu khong thi mot dong template nhu

        url_decision: ""                # CREATE | UPDATE | MERGE | SKIP

    se cho ra ca cum chu thich lam gia tri. Loi do tung lam push vo voi
    `not_found`, vi Base nhan mot ten option khong ton tai.

    Chi cat chu thich khi gia tri MO DAU bang ngoac va da dong ngoac: nho vay
    gia tri khong ngoac co chua dau thang (vi du mot tieu de) van giu nguyen.
    """
    value = value.strip()
    if value[:1] in "\"'":
        quote = value[0]
        end = value.find(quote, 1)
        if end != -1:
            return value[1:end]
    return value


def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Minimal YAML front matter reader: flat `key: value` plus simple lists."""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head = raw[3:end]
    rest = raw[end + 4:].lstrip("\n")
    data: dict = {}
    current_key = None
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and current_key:
            bucket = data.get(current_key)
            if not isinstance(bucket, list):
                bucket = []
                data[current_key] = bucket
            bucket.append(_clean_scalar(line.lstrip()[2:]))
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            value = value.strip()
            data[current_key] = _clean_scalar(value) if value else []
    return data, rest


def load_simple_yaml(path: str) -> dict:
    """Read a flat YAML file (the brief / seo-fields templates) without PyYAML."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        text = "---\n" + text + "\n---\n"
    data, _ = parse_front_matter(text)
    return data


def strip_inline_markdown(text: str) -> str:
    text = MD_IMAGE_RE.sub(" ", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = HTML_LINK_RE.sub(r"\2", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", text)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(?<!\w)([*_])(?!\s)(.+?)(?<!\s)\1(?!\w)", r"\2", text)
    return text


def parse_markdown(path: str) -> Document:
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    front_matter, body = parse_front_matter(raw)

    lines: list[str] = []
    headings: list[Heading] = []
    blocks: list[Block] = []

    state = {"in_fence": False, "kind": "paragraph", "line": 0}
    buffer: list[str] = []
    list_items: list[str] = []

    def flush() -> None:
        if buffer:
            text = " ".join(s.strip() for s in buffer).strip()
            if text:
                blocks.append(Block(state["kind"], text, state["line"], list(list_items)))
        buffer.clear()
        list_items.clear()
        state["kind"] = "paragraph"

    for idx, line in enumerate(body.splitlines(), start=1):
        if FENCE_RE.match(line):
            state["in_fence"] = not state["in_fence"]
            flush()
            lines.append("")
            continue
        if state["in_fence"]:
            lines.append("")
            continue

        lines.append(line)

        if not line.strip():
            flush()
            continue

        m = HEADING_RE.match(line)
        if m:
            flush()
            text = strip_inline_markdown(m.group(2)).strip()
            headings.append(Heading(len(m.group(1)), text, idx))
            blocks.append(Block("heading", text, idx))
            continue

        if TABLE_ROW_RE.match(line):
            if state["kind"] != "table":
                flush()
                state["kind"] = "table"
                state["line"] = idx
            buffer.append(strip_inline_markdown(line))
            continue

        if LIST_ITEM_RE.match(line):
            if state["kind"] != "list":
                flush()
                state["kind"] = "list"
                state["line"] = idx
            item = strip_inline_markdown(LIST_ITEM_RE.sub("", line)).strip()
            list_items.append(item)
            buffer.append(item)
            continue

        if line.lstrip().startswith(">"):
            if state["kind"] != "quote":
                flush()
                state["kind"] = "quote"
                state["line"] = idx
            buffer.append(strip_inline_markdown(line.lstrip().lstrip(">").strip()))
            continue

        if state["kind"] != "paragraph":
            flush()
        if not buffer:
            state["line"] = idx
            state["kind"] = "paragraph"
        buffer.append(strip_inline_markdown(line))

    flush()

    prose = "\n".join(
        b.text for b in blocks if b.kind in ("paragraph", "list", "quote", "heading")
    )
    return Document(path, raw, front_matter, lines, headings, blocks, prose)


# --------------------------------------------------------------------------
# Text utilities
# --------------------------------------------------------------------------

UPPER_VI = "A-ZĐÀÁẢÃẠÂĂÊÔƠƯÍÌỊÓÒÕỌÚÙỦŨỤÝỲỸỶỴ"
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+(?=[" + UPPER_VI + r"0-9(\"“])")
ABBREV_GUARD = ["TP.", "Tp.", "Q.", "P.", "tr.", "vd.", "v.v.", "TT.", "H."]
DOT_SENTINEL = "\x01"


def split_sentences(text: str) -> list[str]:
    """Split Vietnamese prose into sentences.

    Dots inside numbers (1.500.000) and inside common abbreviations (TP.HCM)
    are masked with a sentinel so they do not end a sentence, then restored.
    """
    guarded = re.sub(r"(?<=\d)\.(?=\d)", DOT_SENTINEL, text)
    for abbr in ABBREV_GUARD:
        guarded = guarded.replace(abbr, abbr[:-1] + DOT_SENTINEL)

    parts: list[str] = []
    for chunk in guarded.split("\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.extend(s.strip() for s in SENTENCE_SPLIT_RE.split(chunk) if s.strip())
    return [s.replace(DOT_SENTINEL, ".") for s in parts]


WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


# Tu chuc nang tieng Viet — bo khi do do phu truy van, vi chung xuat hien
# o moi cau va lam nhieu ket qua. Giu lai tu chi huong nhu "len", "ra", "vao"
# vi chung mang nghia trong cum nhu "len tho cu".
VI_STOPWORDS = {
    "cua", "va", "cac", "nhung", "cho", "voi", "trong", "duoc", "la", "co",
    "thi", "ma", "de", "ve", "theo", "tai", "da", "se", "nay", "do", "khi",
    "nhu", "hay", "hoac", "neu", "bi", "boi", "tu", "den", "moi", "cung",
    "của", "và", "các", "những", "cho", "với", "trong", "được", "là", "có",
    "thì", "mà", "để", "về", "theo", "tại", "đã", "sẽ", "này", "đó", "khi",
    "như", "hay", "hoặc", "nếu", "bị", "bởi", "từ", "đến", "mỗi", "cũng",
}


def content_tokens(text: str) -> list[str]:
    """Tu mang nghia trong mot chuoi: bo tu chuc nang va tu mot ky tu."""
    return [t for t in WORD_RE.findall(normalize(text))
            if len(t) >= 2 and t not in VI_STOPWORDS]


def query_coverage(query: str, text: str) -> float:
    """Bao nhieu phan tram tu mang nghia cua truy van xuat hien trong text.

    Dung cho truy van dai kieu hoi thoai, noi doi khop nguyen cum gan nhu khong
    bao gio xay ra va ep no vao chinh la viet guong.
    """
    qt = list(dict.fromkeys(content_tokens(query)))
    if not qt:
        return 0.0
    have = set(content_tokens(text))
    return sum(1 for t in qt if t in have) / len(qt)


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace. Diacritics are kept: they carry meaning."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text.lower())


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    without = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", without).replace("đ", "d").replace("Đ", "D")


def make_slug(text: str, max_words: int = 0) -> str:
    """Sinh slug khong dau tu mot cum tieng Viet co dau.

    Dung cho lenh `intake`: nguoi dung go tu khoa tren Base, may tu dat ten thu muc
    `work/<slug>/`. Nguoi duyet sua lai o cong duyet outline neu khong vua y.

    Chi lam dung mot viec: bo dau, ha chu thuong, noi bang gach ngang. **Khong cat hu tu
    va khong cat ngan theo mac dinh**, vi ca hai deu lam sai:

    - Cat ngan theo so tu lam DUT TU GHEP tieng Viet. "tho cu" bi cat con "tho",
      "dai hoc" con "dai", "kiem tra" con "kiem" — slug thanh vo nghia. Tieng Viet da am
      tiet nen dem "tu" bang khoang trang khong tuong ung voi don vi nghia.
    - Bo hu tu thi nguoc voi chinh blog. Slug that cua toa soan GIU "gan":
      `kinh-nghiem-thue-tro-gan-truong-dai-hoc-su-pham-ky-thuat-tphcm`.

    Slug dai vi vay la binh thuong va dung voi bai that. `onpage_check.check_slug` canh
    bao khi qua 6 tu, va do la canh bao dem giai trinh chu khong phai loi.

    Ket qua khop regex ma `scripts/radar/radar.py` dung de kiem slug.
    `max_words` de danh cho nguoi goi nao thuc su can cat, mac dinh la khong cat.
    """
    plain = strip_diacritics(unicodedata.normalize("NFC", text or "")).lower()
    words = [w for w in re.split(r"[^a-z0-9]+", plain) if w]
    if not words:
        return ""
    if max_words and max_words > 0:
        words = words[:max_words]
    return "-".join(words)


def load_lexicon(path: str | None = None) -> dict:
    with open(path or LEXICON_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def compile_pattern(pattern: str) -> re.Pattern:
    if pattern.startswith("re:"):
        return re.compile(pattern[3:], re.IGNORECASE)
    return re.compile(re.escape(pattern), re.IGNORECASE)


def excerpt(text: str, at: int, width: int = 72) -> str:
    start = max(0, at - width // 3)
    end = min(len(text), start + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


def stdev(values: Iterable[float]) -> float:
    vals = list(values)
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return (sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

ICON = {BLOCK: "[BLOCK]", WARN: "[WARN ]", INFO: "[INFO ]"}


def print_report(report: Report, show_info: bool = False) -> None:
    print()
    print(f"=== {report.name} ===")
    if report.metrics:
        width = max(len(k) for k in report.metrics)
        for key, value in report.metrics.items():
            print(f"  {key.ljust(width)} : {value}")
    findings = [f for f in report.findings if show_info or f.severity != INFO]
    if not findings:
        print("  -> Khong co canh bao.")
        return
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 9), f.line))
    print()
    for f in findings:
        where = f"dong {f.line}" if f.line else "toan bai"
        print(f"  {ICON.get(f.severity, '[?]')} {f.check} ({where}): {f.message}")
        if f.snippet:
            print(f"          > {f.snippet}")
        if f.guidance:
            print(f"          => {f.guidance}")
