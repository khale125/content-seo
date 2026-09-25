"""Tong hop outline tu top 5 doi thu tren Google.

Bon quy tac (theo yeu cau cua chu du an):

  1. Outline phai duoc TONG HOP tu bai cua top 5 dang xep hang.
  2. Heading doi thu co thi outline cua minh CUNG PHAI CO.
     Mac dinh chan BLOCK khi thieu. Muon bo mot chu de thi phai KHAI BAO kem ly do
     trong muc "## Chủ đề đã cân nhắc và không đưa vào" cua outline — bo im lang
     khong duoc chap nhan, vi nguoi duyet can nhin thay quyet dinh do.
  3. Phai co it nhat mot muc doi thu KHONG co. Khong co thi bai chi la ban sao.
  4. Heading phai viet ro y, va KHONG duoc trung nguyen van heading cua doi thu.
     Cung chu de thi duoc; cung cau chu la dao van.

Chay:
  python scripts/serp_outline.py analyze work/<slug>/competitors.json
  python scripts/serp_outline.py check   work/<slug>/outline.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from qa_common import (
    BLOCK, WARN, INFO, Report, content_tokens, force_utf8_stdout,
    normalize, parse_markdown, print_report, query_coverage,
)

MERGE_SIMILARITY = 0.34      # gop hai heading vao cung mot chu de
MATCH_SIMILARITY = 0.34      # muc cua minh co nhan chu de do khong
PLAGIARISM_HARD = 0.85       # gan nhu trung nguyen van -> dao van
MIN_COMPETITORS = 3
TOP_N = 5                    # "top 5 doi thu" — ket qua thu 6 tro di khong tinh vao muc san
MIN_HEADING_TOKENS = 3       # heading duoi nguong nay la cum danh tu, chua ro y
DECLINE_HEADING = "chủ đề đã cân nhắc và không đưa vào"


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def flatten(text: str) -> str:
    """Chuan hoa de so trung nguyen van: bo dau cau va khoang trang thua."""
    return re.sub(r"[^\w\s]", " ", normalize(text)).strip()


def load_competitors(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def validate(data: dict) -> list[str]:
    errs = []
    comps = [c for c in (data.get("competitors") or []) if in_top(c)]
    if len(comps) < MIN_COMPETITORS:
        errs.append(f"Chi co {len(comps)} doi thu, toi thieu {MIN_COMPETITORS}. "
                    "Doc them ket qua o dau SERP.")
    for i, c in enumerate(comps, start=1):
        if not str(c.get("url") or "").lower().startswith("https://"):
            errs.append(f"Doi thu #{i}: thieu url HTTPS da mo duoc that.")
        if not (c.get("headings") or []):
            errs.append(f"Doi thu #{i}: chua ghi heading nao. "
                        "Mo that trang do va chep danh sach heading.")
    if not str(data.get("captured_on") or "").strip():
        errs.append("Thieu captured_on (ngay doc SERP) — SERP doi theo thoi gian.")
    return errs


def in_top(c: dict) -> bool:
    try:
        return int(c.get("rank", 99)) <= TOP_N
    except (TypeError, ValueError):
        return False


def build_topics(data: dict) -> list[dict]:
    """Chi gom heading cua doi thu TRONG TOP 5.

    Ket qua thu 6 tro di van duoc ghi lai de tham khao, nhung khong tao ra muc san:
    mot trang xep duoi top 5 khong phai bang chung ve thu Google dang thuong.
    """
    items = []
    for c in data.get("competitors", []):
        if not in_top(c):
            continue
        rank = c.get("rank")
        for h in c.get("headings", []):
            text = str(h).strip()
            if text:
                items.append((rank, text, set(content_tokens(text))))

    topics: list[dict] = []
    for rank, text, toks in items:
        if not toks:
            continue
        best, best_sim = None, 0.0
        for t in topics:
            sim = jaccard(toks, t["tokens"])
            if sim > best_sim:
                best, best_sim = t, sim
        if best is not None and best_sim >= MERGE_SIMILARITY:
            best["members"].append((rank, text))
            best["ranks"].add(rank)
            best["tokens"] |= toks
        else:
            topics.append({"label": text, "members": [(rank, text)],
                           "ranks": {rank}, "tokens": set(toks)})

    for t in topics:
        t["n"] = len(t["ranks"])
    topics.sort(key=lambda t: (-t["n"], min(t["ranks"])))
    return topics


def read_outline(outline_path: str) -> dict:
    """Muc du kien (H3 duoi '## Sườn bài') + phan khai bao chu de da loai."""
    doc = parse_markdown(outline_path)

    skeleton, skeleton_end = 0, 10 ** 9
    decline, decline_end = 0, 10 ** 9
    for h in doc.headings:
        if h.level == 2 and "sườn bài" in normalize(h.text):
            skeleton, skeleton_end = h.line, 10 ** 9
        elif skeleton and skeleton_end == 10 ** 9 and h.level == 2 and h.line > skeleton:
            skeleton_end = h.line
        if h.level == 2 and DECLINE_HEADING in normalize(h.text):
            decline, decline_end = h.line, 10 ** 9
        elif decline and decline_end == 10 ** 9 and h.level == 2 and h.line > decline:
            decline_end = h.line

    heads = [h for h in doc.headings if h.level == 3 and skeleton < h.line < skeleton_end] \
        if skeleton else [h for h in doc.headings if h.level == 3]
    sections = [{"text": re.sub(r"^H[23]\s*\d+[.)]?\s*", "", h.text).strip(),
                 "line": h.line,
                 "tokens": set(content_tokens(h.text))} for h in heads]

    # Khai bao bo phai la TUNG DONG BANG rieng biet, moi dong mot chu de kem ly do.
    # Quet ca khoi van ban se nuot nham nhung chu de chi duoc nhac ngang qua.
    declined_items: list[str] = []
    if decline:
        stop = min(decline_end, len(doc.lines))
        for raw in doc.lines[decline:stop]:
            line = raw.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            topic, reason = cells[0], cells[-1]
            if not topic or set(topic) <= set("-: "):
                continue
            if "chủ đề" in normalize(topic):
                continue                      # dong tieu de bang
            if not reason or set(reason) <= set("-: "):
                continue                      # phai co ly do
            declined_items.append(topic)

    return {"sections": sections, "declined_items": declined_items,
            "has_decline_block": bool(decline)}


def analyze(data: dict, report: Report) -> list[dict]:
    topics = build_topics(data)
    n_comp = len([c for c in data.get("competitors", []) if in_top(c)])
    outside = len([c for c in data.get("competitors", []) if not in_top(c)])
    report.metrics["truy van"] = data.get("primary_query", "")
    report.metrics[f"doi thu trong top {TOP_N}"] = n_comp
    if outside:
        report.metrics["ghi nhan ngoai top (khong tinh)"] = outside
    report.metrics["ngay doc SERP"] = data.get("captured_on", "")
    report.metrics["chu de top dang phuc vu"] = len(topics)
    types = [c.get("type", "") for c in data.get("competitors", []) if in_top(c) and c.get("type")]
    if types:
        report.metrics["loai trang o top"] = ", ".join(sorted(set(types)))
    return topics


def print_topics(topics: list[dict], n_comp: int) -> None:
    print()
    print("CHU DE TOP DANG PHUC VU — outline cua minh phai co DU, hoac khai bao ly do bo")
    print("-" * 80)
    for t in topics:
        ranks = ",".join(str(r) for r in sorted(t["ranks"]))
        print(f"  [{t['n']}/{n_comp}]  {t['label'][:62]}")
        print(f"           o ket qua: {ranks}")
        for rank, text in t["members"][1:3]:
            print(f"           #{rank}: {text[:64]}")
    print()
    print("Day la DANH SACH CAU HOI phai tra loi. Viet lai bang cau chu cua minh —")
    print("cung chu de thi duoc, cung cau chu la dao van.")


def check_outline(outline_path: str, data: dict, report: Report) -> None:
    topics = build_topics(data)
    n_comp = len([c for c in data.get("competitors", []) if in_top(c)])
    parsed = read_outline(outline_path)
    sections = parsed["sections"]

    if not sections:
        report.add("serp", BLOCK, "Khong doc duoc muc nao trong outline.")
        return

    declined_items = [(item, set(content_tokens(item))) for item in parsed["declined_items"]]

    def covered(topic) -> bool:
        for s in sections:
            if max(jaccard(s["tokens"], topic["tokens"]),
                   query_coverage(topic["label"], s["text"])) >= MATCH_SIMILARITY:
                return True
        return False

    def is_declined(topic) -> bool:
        for item, toks in declined_items:
            if max(jaccard(topic["tokens"], toks),
                   query_coverage(topic["label"], item)) >= MATCH_SIMILARITY:
                return True
        return False

    missing, declined = [], []
    for t in topics:
        if covered(t):
            continue
        (declined if is_declined(t) else missing).append(t)

    report.metrics["chu de top da phu"] = f"{len(topics) - len(missing) - len(declined)}/{len(topics)}"
    report.metrics["chu de khai bao bo"] = len(declined)

    # --- Quy tac 2 ---
    if missing:
        report.add("serp", BLOCK,
                   f"{len(missing)}/{len(topics)} chu de doi thu co ma outline khong co, "
                   "va cung khong khai bao ly do bo.",
                   snippet=" | ".join(f"[{t['n']}/{n_comp}] {t['label'][:42]}" for t in missing[:6]),
                   guidance="Doi thu co thi minh phai co. Them muc tra loi, HOAC khai bao vao muc "
                            f'"## Chủ đề đã cân nhắc và không đưa vào" kem ly do cu the. '
                            "Bo im lang khong duoc chap nhan — nguoi duyet can nhin thay quyet dinh. "
                            "KHONG chep cau chu cua ho, chi lay cau hoi can tra loi.")
    if declined:
        report.add("serp", INFO,
                   f"{len(declined)} chu de da khai bao bo co ly do: "
                   + " | ".join(t["label"][:40] for t in declined[:5]))

    # --- Quy tac 3 ---
    unique = []
    for s in sections:
        best = 0.0
        for t in topics:
            best = max(best, jaccard(s["tokens"], t["tokens"]),
                       query_coverage(t["label"], s["text"]))
        if best < MATCH_SIMILARITY:
            unique.append(s)

    report.metrics["muc top khong co"] = len(unique)
    if unique:
        report.add("serp", INFO,
                   "Diem khac biet: " + " | ".join(s["text"][:46] for s in unique[:4]))
    else:
        report.add("serp", BLOCK,
                   "Outline khong co muc nao ma doi thu khong co.",
                   guidance="Phu du chu de cua top ma khong them gi thi bai chi la ban sao — khong du "
                            "ly do de Google xep tren ho. Them du lieu rieng, vi du tinh duoc, nhom "
                            "nguoi doc chua ai phuc vu, hoac phan quyet dinh thay vi tra cuu.")

    # --- Quy tac 4 ---
    comp_headings = [(c.get("rank"), str(h).strip())
                     for c in data.get("competitors", []) if in_top(c)
                     for h in c.get("headings", [])]
    for s in sections:
        sflat = flatten(s["text"])
        if not sflat:
            continue
        for rank, h in comp_headings:
            hflat = flatten(h)
            if not hflat:
                continue
            if sflat == hflat:
                report.add("plagiarism", BLOCK,
                           f'Heading trung NGUYEN VAN voi ket qua #{rank}.',
                           line=s["line"], snippet=f'"{s["text"]}"',
                           guidance="Cung chu de thi duoc, cung cau chu la dao van. Viet lai thanh "
                                    "cau hoi that cua nguoi doc, bang cach dien dat cua minh.")
                break
            if jaccard(set(content_tokens(s["text"])), set(content_tokens(h))) >= PLAGIARISM_HARD:
                report.add("plagiarism", WARN,
                           f'Heading gan trung heading cua ket qua #{rank}.',
                           line=s["line"],
                           snippet=f'cua minh: "{s["text"]}"  |  cua ho: "{h[:50]}"',
                           guidance="Doi cach dien dat: chuyen thanh cau hoi, them dieu kien, "
                                    "hoac neu goc nhin cua minh.")
                break

        # "Lời kết" la ten co dinh do format he Blog Muaban.net quy dinh; keo dai
        # no ra cho du token la lam sai format de qua mot canh bao.
        if len(s["tokens"]) < MIN_HEADING_TOKENS and "lời kết" not in normalize(s["text"]):
            report.add("clarity", WARN,
                       f'Heading "{s["text"]}" qua ngan, chua ro y.',
                       line=s["line"],
                       guidance="Heading phai noi ro nguoi doc nhan duoc gi. "
                                '"Tiền sử dụng đất" la cum danh tu; '
                                '"Tiền sử dụng đất tính theo mấy bậc" moi la mot cau hoi.')

    # --- So luong heading so voi top 3 (theo file quy chuan on-page) ---
    top3 = sorted([c for c in data.get("competitors", []) if in_top(c)],
                  key=lambda c: int(c.get("rank", 99)))[:3]
    if top3:
        counts = [len(c.get("headings", [])) for c in top3]
        bench = max(counts)
        report.metrics["so heading top 3"] = ", ".join(
            f"#{c.get('rank')}={len(c.get('headings', []))}" for c in top3)
        report.metrics["so muc cua minh"] = len(sections)
        if len(sections) < bench:
            report.add("serp", WARN,
                       f"Outline co {len(sections)} muc, it hon top 3 (nhieu nhat {bench}).",
                       guidance="File quy chuan yeu cau so luong heading ngang ngua hoac hon top 3. "
                                "Kiem lai con chu de nao cua ho chua co muc nhan, hoac tach muc dai "
                                "thanh heading con. KHONG them muc rong chi de du so.")

    # --- Canh bao lech format ---
    types = [str(c.get("type", "")).lower() for c in data.get("competitors", []) if in_top(c)]
    listy = sum(1 for t in types if "danh sach" in t or "cong cu" in t or "tin dang" in t)
    if listy >= max(3, n_comp * 0.6):
        report.add("serp", BLOCK,
                   f"{listy}/{n_comp} ket qua dau la trang danh sach hoac cong cu, khong phai bai viet.",
                   guidance="Viet blog de chen vao SERP dang nay la chon sai format. "
                            "Dat url_decision = SKIP va de xuat loai trang dung.")


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Tong hop outline tu top 5 doi thu.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("analyze", help="Doc competitors.json, in ra chu de top dang phuc vu")
    p.add_argument("competitors")

    p = sub.add_parser("check", help="Outline da phu du chu de cua top chua")
    p.add_argument("outline")
    p.add_argument("--competitors", default=None)

    args = ap.parse_args()

    if args.cmd == "analyze":
        data = load_competitors(args.competitors)
        errs = validate(data)
        if errs:
            print("DU LIEU DOI THU CHUA DAT:", file=sys.stderr)
            for e in errs:
                print("  - " + e, file=sys.stderr)
            return 2
        report = Report(f"SERP top — {data.get('primary_query','')}")
        topics = analyze(data, report)
        print_report(report, show_info=True)
        print_topics(topics, len([c for c in data.get("competitors", []) if in_top(c)]))
        return 0

    comp = args.competitors
    if not comp:
        candidate = os.path.join(os.path.dirname(os.path.abspath(args.outline)), "competitors.json")
        comp = candidate if os.path.exists(candidate) else None
    if not comp:
        print("Khong tim thay competitors.json canh outline. "
              "Copy tu templates/competitors.json va doc top 5 truoc.", file=sys.stderr)
        return 2

    data = load_competitors(comp)
    errs = validate(data)
    if errs:
        print("DU LIEU DOI THU CHUA DAT:", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        return 2

    report = Report(f"Outline vs top SERP — {os.path.basename(args.outline)}")
    analyze(data, report)
    check_outline(args.outline, data, report)
    print_report(report, show_info=True)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
