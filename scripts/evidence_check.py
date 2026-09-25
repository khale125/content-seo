"""Doi chieu ban thao voi evidence ledger de chan bia dat.

Hai chieu kiem tra:
  1. Ledger co hop le khong: VERIFIED phai co trich dan nguyen van, nguon HTTPS,
     ngay thang; claim FACT rui ro cao phai dua tren nguon goc.
  2. Ban thao co vuot qua ledger khong: moi con so, ty le, ngay, so hieu van ban
     xuat hien trong bai phai tim duoc cho dua trong ledger.

Chay:
  python scripts/evidence_check.py work/<slug>/article.md --ledger work/<slug>/evidence-ledger.csv
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import sys

from qa_common import (
    BLOCK, WARN, INFO, Report, CLAIM_REF_RE,
    excerpt, force_utf8_stdout, normalize, parse_markdown, print_report, split_sentences,
)

REQUIRED_COLUMNS = [
    "claim_id", "claim", "claim_type", "risk", "source_type", "source_url",
    "source_title", "published_date", "retrieved_date", "supporting_quote", "status",
]
VALID_TYPES = {"FACT", "INTERPRETATION", "FORECAST", "EXPERIENCE"}
VALID_RISK = {"LOW", "MED", "HIGH"}
VALID_STATUS = {"VERIFIED", "PARTIAL", "GAP"}
PRIMARY_SOURCES = {"LAW", "GOV", "STATS"}
VALID_SOURCE_TYPES = {"LAW", "GOV", "STATS", "REPORT", "NEWS", "MARKETPLACE", "NONE"}
MIN_QUOTE_CHARS = 25

# So co don vi, ty le, tien, dien tich, thoi gian xu ly, ngay thang, so hieu van ban.
NUMERIC_CLAIM_RE = re.compile(
    r"(?<![\w/])("
    r"\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?"            # 1.500.000
    r"|\d+(?:[.,]\d+)?\s*%"                          # 12,5 %
    r"|\d+(?:[.,]\d+)?\s*(?:triệu|tỷ|nghìn|đồng|vnđ|vnd|m2|m²|ha|km|phút|giờ|"
    r"ngày|tuần|tháng|năm|lần|căn|tin|hộ|tầng|phòng|người)"
    r"|\d{1,2}/\d{1,2}/\d{4}"                        # 01/04/2026
    r"|(?:số|Số)\s*\d+[/\w.-]*"                      # so hieu van ban
    r"|\b(?:19|20)\d{2}\b"                           # nam
    r")",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUM_ONLY_RE = re.compile(r"[\d.,]+")

# Cac con so khong can nguon: so thu tu trong danh sach, so muc, don vi tien te chung.
BENIGN_CONTEXT_RE = re.compile(r"^(bước|phần|mục|chương|điều|khoản|hình|bảng)\s", re.IGNORECASE)


def read_ledger(path: str, report: Report) -> list[dict]:
    if not os.path.exists(path):
        report.add("ledger", BLOCK, f"Khong tim thay evidence ledger: {path}",
                   guidance="Moi bai phai co evidence-ledger.csv. Copy tu templates/evidence-ledger.csv.")
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        report.add("ledger", BLOCK, "Evidence ledger rong.")
        return []
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        report.add("ledger", BLOCK, "Ledger thieu cot: " + ", ".join(missing),
                   guidance="Dung dung header trong templates/evidence-ledger.csv.")
    return rows


def check_ledger_rows(rows: list[dict], report: Report) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    today = dt.date.today()

    for n, row in enumerate(rows, start=2):   # dong 1 la header
        cid = (row.get("claim_id") or "").strip()
        if not cid:
            report.add("ledger", BLOCK, f"Dong {n}: thieu claim_id.")
            continue
        if cid in by_id:
            report.add("ledger", BLOCK, f"Dong {n}: claim_id trung '{cid}'.")
        by_id[cid] = row

        ctype = (row.get("claim_type") or "").strip().upper()
        risk = (row.get("risk") or "").strip().upper()
        status = (row.get("status") or "").strip().upper()
        stype = (row.get("source_type") or "").strip().upper()
        url = (row.get("source_url") or "").strip()
        quote = (row.get("supporting_quote") or "").strip()
        claim_text = (row.get("claim") or "").strip()

        if not claim_text:
            report.add("ledger", BLOCK, f"{cid}: thieu noi dung claim.")
        if ctype not in VALID_TYPES:
            report.add("ledger", BLOCK, f"{cid}: claim_type '{ctype}' khong hop le.",
                       guidance="Dung mot trong: " + ", ".join(sorted(VALID_TYPES)))
        if risk not in VALID_RISK:
            report.add("ledger", WARN, f"{cid}: risk '{risk}' khong hop le.")
        if status not in VALID_STATUS:
            report.add("ledger", BLOCK, f"{cid}: status '{status}' khong hop le.")
        if stype and stype not in VALID_SOURCE_TYPES:
            report.add("ledger", WARN, f"{cid}: source_type '{stype}' khong nam trong danh muc.")

        if status == "VERIFIED":
            if len(quote) < MIN_QUOTE_CHARS:
                report.add("ledger", BLOCK,
                           f"{cid}: VERIFIED nhung supporting_quote qua ngan hoac trong.",
                           guidance="Dan dung cau chu trong nguon chung minh claim. Tom tat khong "
                                    "thay duoc trich dan nguyen van.")
            if not url.lower().startswith("https://"):
                report.add("ledger", BLOCK, f"{cid}: source_url phai la HTTPS day du.",
                           snippet=url or "(trong)",
                           guidance="Khong bao gio dung URL suy doan. Chi dan URL da that su mo duoc.")
            if not (row.get("retrieved_date") or "").strip():
                report.add("ledger", BLOCK, f"{cid}: thieu retrieved_date.")
            if not (row.get("published_date") or "").strip():
                report.add("ledger", WARN, f"{cid}: thieu published_date cua nguon.")
            if ctype == "FACT" and risk == "HIGH" and stype not in PRIMARY_SOURCES:
                report.add("ledger", BLOCK,
                           f"{cid}: claim rui ro cao dua tren nguon '{stype or 'trong'}'.",
                           guidance="FACT + risk HIGH (phap ly, thue, tin dung, an toan, gia) bat buoc "
                                    "nguon LAW/GOV/STATS. Bao chi chi la tin hieu dan duong.")
            if ctype == "EXPERIENCE":
                report.add("ledger", WARN,
                           f"{cid}: claim loai EXPERIENCE duoc danh dau VERIFIED.",
                           guidance="Trai nghiem chi hop le khi co bang chung that va duoc phep dung. "
                                    "Nguoi duyet phai xac nhan truoc khi dang.")

        for field in ("published_date", "retrieved_date", "effective_date"):
            val = (row.get(field) or "").strip()
            if val and not DATE_RE.match(val):
                report.add("ledger", WARN, f"{cid}: {field}='{val}' khong theo dang YYYY-MM-DD.")
            elif val and DATE_RE.match(val):
                try:
                    d = dt.date.fromisoformat(val)
                    if d > today:
                        report.add("ledger", BLOCK, f"{cid}: {field} o tuong lai ({val}).",
                                   guidance="Ngay o tuong lai gan nhu luon la dau hieu bia so lieu.")
                except ValueError:
                    report.add("ledger", WARN, f"{cid}: {field}='{val}' khong phai ngay hop le.")

    return by_id


def check_gaps_in_article(doc, by_id: dict[str, dict], report: Report) -> None:
    gaps = {cid: r for cid, r in by_id.items() if (r.get("status") or "").upper() == "GAP"}
    report.metrics["claim GAP"] = len(gaps)
    if not gaps:
        return
    body = normalize(doc.body_text)
    for cid, row in gaps.items():
        claim = (row.get("claim") or "").strip()
        referenced = cid in CLAIM_REF_RE.findall(doc.raw)
        # dau hieu claim GAP van con trong bai: trung >=6 tu lien tiep
        words = normalize(claim).split()
        leaked = referenced or any(
            " ".join(words[i:i + 6]) in body
            for i in range(max(0, len(words) - 5))
            if len(words) >= 6
        )
        if leaked:
            report.add("gap", BLOCK,
                       f"{cid} co status GAP nhung noi dung van xuat hien trong bai.",
                       snippet=claim[:90],
                       guidance="Bo claim, thu hep den muc nguon chiu duoc, hoac chuyen thanh huong dan "
                                "de nguoi doc tu tra cuu. Khong de GAP thanh cau khang dinh.")
        else:
            report.add("gap", INFO, f"{cid}: GAP, da khong xuat hien trong bai.")


def check_refs_resolve(doc, by_id: dict[str, dict], report: Report) -> None:
    refs = set(CLAIM_REF_RE.findall(doc.raw))
    unknown = sorted(r for r in refs if r not in by_id)
    if unknown:
        report.add("refs", BLOCK, "Tham chieu khong co trong ledger: " + ", ".join(unknown),
                   guidance="Moi [Cxx] trong bai phai tro toi mot dong ledger. Luu y tu quy tac "
                            "16: than bai khong nen con ky hieu [Cxx] nao — dan nguon bang cach "
                            "neu ten van ban trong cau, va giu claim_id o ledger.")
    unused = sorted(c for c, r in by_id.items()
                    if c not in refs and (r.get("status") or "").upper() == "VERIFIED")
    if unused:
        report.add("refs", INFO, f"{len(unused)} claim VERIFIED chua duoc dung trong bai: "
                                 + ", ".join(unused[:8]))


def build_evidence_corpus(by_id: dict[str, dict]) -> str:
    parts = []
    for row in by_id.values():
        if (row.get("status") or "").upper() == "GAP":
            continue
        parts.append(row.get("claim", ""))
        parts.append(row.get("supporting_quote", ""))
        parts.append(row.get("source_title", ""))
        parts.append(row.get("published_date", ""))
        parts.append(row.get("effective_date", ""))
        # KHONG dua retrieved_date vao day. Da thu va phai bo: chuoi ngay chua nhieu chu so
        # le, nen mot con so BIA trong bai co the trung mot manh cua ngay va lot luoi. Thu
        # nghiem tren examples/fixture-van-may cho thay "15%" bia dat lot qua chi vi mot
        # retrieved_date co chua "15". Moc du lieu cua bai duoc mien rieng o duoi thay vi
        # noi rong corpus.
    return normalize(" | ".join(parts))


def _num_variants(token: str) -> set[str]:
    """1.500 / 1,500 / 1500 phai duoc coi la cung mot con so."""
    m = NUM_ONLY_RE.search(token)
    if not m:
        return set()
    raw = m.group(0)
    digits = re.sub(r"[.,]", "", raw)
    return {raw, digits, raw.replace(".", ","), raw.replace(",", ".")}


def _self_dates(doc) -> set[str]:
    """Ngay do CHINH BAI khai trong front matter: data_as_of, review_after.

    Day la sieu du lieu cua bai chu khong phai claim, nen khong co dong ledger nao dung
    ra chiu trach nhiem cho chung. Khoi minh bach lai bat buoc phai in moc du lieu ra,
    nen neu khong mien thi bai nao cung dinh mot BLOCK oan.

    Chi mien dung gia tri da khai, o ca dang ISO lan dang ngay/thang/nam.
    """
    out = set()
    for key in ("data_as_of", "review_after"):
        val = str(doc.front_matter.get(key) or "").strip()
        if not val:
            continue
        out.add(val)
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", val)
        if m:
            y, mo, d = m.groups()
            out.update({f"{d}/{mo}/{y}", f"{d}-{mo}-{y}", f"{d}.{mo}.{y}"})
    return out


def check_numbers_covered(doc, by_id: dict[str, dict], report: Report, strict: bool) -> None:
    corpus = build_evidence_corpus(by_id)
    self_dates = _self_dates(doc)
    if not corpus.strip():
        report.add("numbers", BLOCK, "Ledger khong co dong nao dung duoc de doi chieu.")
        return

    prose_blocks = [b for b in doc.blocks if b.kind in ("paragraph", "list", "table", "quote")]
    uncovered: list[tuple[str, int, str]] = []
    checked = 0

    for block in prose_blocks:
        for sentence in split_sentences(block.text):
            if BENIGN_CONTEXT_RE.match(sentence.strip()):
                continue
            for m in NUMERIC_CLAIM_RE.finditer(sentence):
                token = m.group(1).strip()
                checked += 1
                variants = _num_variants(token) | {normalize(token)}
                if any(v and v.lower() in corpus for v in variants):
                    continue
                if any(d in sentence for d in self_dates):
                    continue        # moc du lieu cua chinh bai, xem _self_dates
                uncovered.append((token, block.line, excerpt(sentence, m.start())))

    report.metrics["so lieu trong bai"] = checked
    report.metrics["so lieu khong co cho dua"] = len(uncovered)

    severity = BLOCK if strict else WARN
    seen_tokens = set()
    for token, line, ctx in uncovered:
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        report.add("numbers", severity,
                   f'Con so "{token}" khong doi chieu duoc voi dong nao trong ledger.',
                   line=line, snippet=ctx,
                   guidance="Them dong ledger co trich dan nguyen van cho con so nay, hoac bo con so. "
                            "Day la duong bia dat pho bien nhat.")
        if len(seen_tokens) >= 15:
            report.add("numbers", INFO, f"... va {len(uncovered) - 15} truong hop nua.")
            break


def check_ymyl_block(doc, report: Report) -> None:
    body = normalize(doc.body_text)
    signals = {
        "moc du lieu": r"(cập nhật (tới|đến)|tính đến ngày|số liệu (tới|đến)|dữ liệu (tới|đến))",
        "pham vi ap dung": r"(áp dụng (cho|với|tại)|phạm vi áp dụng|chỉ đúng với|trường hợp)",
        "gioi han / tham van": r"(tùy (từng|theo)|bạn cần hỏi|tham vấn|luật sư|công chứng viên|"
                               r"chuyên viên|liên hệ trực tiếp|khác nhau giữa)",
        "can cu nguon": r"(theo (nghị định|thông tư|luật|quyết định)|căn cứ|nguồn:)",
    }
    missing = [name for name, rx in signals.items() if not re.search(rx, body)]
    report.metrics["tin hieu YMYL"] = f"{len(signals) - len(missing)}/{len(signals)}"
    if missing:
        report.add("ymyl", WARN, "Thieu tin hieu YMYL: " + ", ".join(missing),
                   guidance="Bat dong san luon la YMYL. Bai phai co moc du lieu, pham vi ap dung, "
                            "gioi han va can cu nguon. Xem docs/04-chinh-sach-nguon.md.")


def run(article: str, ledger_path: str, strict: bool = True) -> Report:
    doc = parse_markdown(article)
    report = Report(f"Bang chung va chong bia dat — {article}")
    rows = read_ledger(ledger_path, report)
    if not rows:
        return report
    by_id = check_ledger_rows(rows, report)
    report.metrics["so claim"] = len(by_id)
    report.metrics["claim VERIFIED"] = sum(
        1 for r in by_id.values() if (r.get("status") or "").upper() == "VERIFIED")
    check_refs_resolve(doc, by_id, report)
    check_gaps_in_article(doc, by_id, report)
    check_numbers_covered(doc, by_id, report, strict)
    check_ymyl_block(doc, report)
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Doi chieu ban thao voi evidence ledger.")
    ap.add_argument("article")
    ap.add_argument("--ledger", required=True, help="evidence-ledger.csv")
    ap.add_argument("--lenient", action="store_true",
                    help="Ha con so khong co cho dua tu BLOCK xuong WARN (chi dung khi ra soat so bo)")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    report = run(args.article, args.ledger, strict=not args.lenient)
    print_report(report, show_info=args.all)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
