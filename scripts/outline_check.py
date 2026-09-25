"""Kiem outline TRUOC khi dua len cong duyet.

Bat loi o cho no phat sinh. Sua mot heading trong outline ton mot phut;
phat hien cung loi do sau khi da viet 1.500 chu ton ca buoi.

Kiem:
  1. Co DUNG MOT muc nhan cau hoi chinh, va muc do dung dau (tra loi truoc).
  2. Khong nhoi truy van vao nhieu muc.
  3. Moi cau hoi trong brief deu co muc nhan.
  3b. Moi muc chinh mang tu khoa chinh hoac tu khoa phu.
  4. Moi muc khai bao source_ids, hoac la muc huong dan thao tac.
  5. Khong co muc "Ket luan" tom tat lai bai.
  6. Co uoc luong do dai, va no duoc suy ra tu noi dung.

Chay:
  python scripts/outline_check.py work/<slug>/outline.md --brief work/<slug>/brief.yaml
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from qa_common import (
    BLOCK, WARN, INFO, Report, content_tokens, force_utf8_stdout,
    load_simple_yaml, normalize, parse_markdown, print_report, query_coverage,
    strip_diacritics,
)

MIN_QUERY_HEADING_COVERAGE = 0.6
MIN_QUESTION_COVERAGE = 0.6
MAX_STUFFED_RATIO = 0.4

SKELETON_HEADING = "sườn bài"
SOURCE_IDS_RE = re.compile(r"source_ids?\s*:?\s*\**\s*(.+)", re.IGNORECASE)
CLAIM_RE = re.compile(r"C\d{1,3}")
HOWTO_HINTS = ("checklist", "việc cần làm", "việc bạn nên làm", "bước tiếp theo",
               "tự kiểm", "hướng dẫn", "thao tác", "cách tra", "tra ở đâu")
# "Lời kết" KHONG nam trong nhom nay: format outline cua he Blog Muaban.net bat
# buoc phai co no. Ba tu con lai van la phan ket tom tat lai bai — thu docs/02 cam.
CONCLUSION_HINTS = ("kết luận", "tổng kết", "tóm lại")

# --------------------------------------------------------------------------
# Format outline cua he Blog Muaban.net / Vieclam.net
#
# Nguon: sheet "Format Outline hệ Blog", dong Muaban.net va Vieclam.net.
# Dac diem rieng cua he nay, khac dong Mogi.vn trong cung sheet:
#   - Sapo de o muc H2, khong phai doan van tran
#   - Cac muc chinh danh so La Ma (I., II., III.), muc con danh so A Rap (1., 2.)
#   - Bat buoc co dong lien he nguoi len outline, de CTV hoi lai duoc
#   - Bat buoc ket bai bang "Lời kết" co keu goi hanh dong
# --------------------------------------------------------------------------

OUTLINE_OWNER_RE = re.compile(
    r"Mọi thắc mắc liên hệ người lên outline\s*[:\-]?\s*(.*)", re.IGNORECASE)
CLOSING_HEADING = "lời kết"
# Sheet mo dau bang dung hai dong nay, truoc ca dong lien he. Chung la thu CTV
# doc dau tien de biet bai ten gi.
TITLE_LINE_RE = re.compile(r"^\s*Title\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
H1_LINE_RE = re.compile(r"^\s*H1\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
CTA_HINTS = ("bình luận", "chia sẻ", "xem thêm", "để lại", "theo dõi", "liên hệ")
ROMAN_RE = re.compile(r"^[IVXLC]+\s*[.)]")
ARABIC_RE = re.compile(r"^\d{1,2}\s*[.)]")
SAPO_HEADING = "sapo"


def extract_sections(doc) -> list[dict]:
    """Cac muc du kien cua BAI nam duoi '## Sườn bài', moi muc la mot H3.

    Neu outline khong theo mau, lui ve dung toan bo H3.
    """
    skeleton_line = 0
    end_line = 10 ** 9
    for h in doc.headings:
        if h.level == 2 and SKELETON_HEADING in normalize(h.text):
            skeleton_line = h.line
        elif skeleton_line and h.level == 2 and h.line > skeleton_line:
            end_line = h.line
            break

    if skeleton_line:
        heads = [h for h in doc.headings
                 if h.level == 3 and skeleton_line < h.line < end_line]
    else:
        heads = [h for h in doc.headings if h.level == 3]

    sections = []
    for i, h in enumerate(heads):
        stop = heads[i + 1].line if i + 1 < len(heads) else end_line
        body = "\n".join(doc.lines[h.line:min(stop, len(doc.lines)) - 1])
        ids = []
        for m in SOURCE_IDS_RE.finditer(body):
            ids += CLAIM_RE.findall(m.group(1))
        sections.append({
            # Bo tien to danh so (H3, I., 1.) truoc khi doi chieu truy van, neu
            # khong thi "I. Chi phi chuyen dat..." khong khop voi truy van chinh.
            "heading": re.sub(r"^(?:H[234]\s*)?(?:[IVXLC]+|\d{1,2})\s*[.)]\s*", "",
                              re.sub(r"^H[23]\s*", "", h.text)).strip(),
            "raw_heading": h.text,
            "line": h.line,
            "body": body,
            "source_ids": ids,
        })
    return sections


def check_query_ownership(sections, primary: str, report: Report) -> None:
    if not primary:
        report.add("focus", WARN, "brief.yaml chua co primary_query, khong kiem duoc trong tam.")
        return
    if not sections:
        report.add("focus", BLOCK, "Khong tim thay muc nao trong 'Sườn bài'.",
                   guidance="Moi muc du kien cua bai viet mot dong '### <tieu de muc>' duoi "
                            "'## Sườn bài'.")
        return

    scored = [(query_coverage(primary, s["heading"]), s) for s in sections]
    best_cov, best = max(scored, key=lambda x: x[0])
    owners = [s for cov, s in scored if cov >= MIN_QUERY_HEADING_COVERAGE]

    report.metrics["truy van chinh"] = primary
    report.metrics["muc nhan cau hoi chinh"] = (
        f'{best_cov:.0%} — "{best["heading"][:46]}"' if best_cov else "KHONG CO")

    if not owners:
        have = set(content_tokens(" ".join(s["heading"] for s in sections)))
        missing = [t for t in dict.fromkeys(content_tokens(primary)) if t not in have]
        report.add("focus", BLOCK,
                   f"Khong muc nao nhan cau hoi chinh (cao nhat {best_cov:.0%}).",
                   line=sections[0]["line"], snippet=f'truy van: "{primary}"',
                   guidance="Dat DUNG MOT muc tra loi thang truy van chinh, viet thanh cau hoi that "
                            "cua nguoi doc, va dat len DAU. "
                            + (f"Tu chua xuat hien o muc nao: {', '.join(missing[:8])}. "
                               if missing else "")
                            + "Xem docs/02-chuan-outline.md muc 'Mot muc phai nhan cau hoi chinh'.")
        return

    if len(owners) > max(1, len(sections) * MAX_STUFFED_RATIO):
        report.add("focus", BLOCK,
                   f"{len(owners)}/{len(sections)} muc cung nhan truy van chinh.",
                   line=owners[1]["line"],
                   guidance="Dung MOT muc nhan cau hoi chinh. Cac muc con lai phuc vu cau hoi "
                            "tiep theo, khong lap lai truy van.")

    if scored[0][0] < MIN_QUERY_HEADING_COVERAGE:
        report.add("focus", WARN,
                   f'Muc dau tien khong nhan cau hoi chinh; muc nhan no la "{best["heading"][:46]}" '
                   f"(dong {best['line']}).",
                   line=sections[0]["line"],
                   guidance="Tra loi truoc, giai thich sau. Dua muc tra loi thang truy van len dau.")


def check_question_coverage(sections, questions, report: Report) -> None:
    questions = [str(q).strip() for q in (questions or []) if str(q).strip()]
    if not questions:
        report.add("focus", INFO, "brief.yaml chua liet ke questions_to_answer.")
        return
    surface = " \n ".join(s["heading"] + " " + s["body"] for s in sections)
    weak = [q for q in questions if query_coverage(q, surface) < MIN_QUESTION_COVERAGE]
    report.metrics["cau hoi brief co muc nhan"] = f"{len(questions) - len(weak)}/{len(questions)}"
    if weak:
        report.add("focus", WARN,
                   f"{len(weak)}/{len(questions)} cau hoi trong brief chua thay muc nao nhan.",
                   snippet=" | ".join(q[:52] for q in weak[:4]),
                   guidance="Them muc tra loi, hoac bo cau hoi do khoi brief neu no khong con thuoc "
                            "pham vi bai. Dung de brief hua mot dang va outline giao mot dang.")


def check_evidence_declared(sections, report: Report) -> None:
    orphans = []
    for s in sections:
        if s["source_ids"]:
            continue
        low = normalize(s["heading"] + " " + s["body"][:400])
        if any(h in low for h in HOWTO_HINTS):
            continue
        # "Lời kết" la muc bat buoc cua format he Blog Muaban.net va co y khong
        # mang claim vat chat — doi source_ids o day la doi thu no khong duoc
        # phep co. Xem docs/02 muc "Format outline cua he Blog Muaban.net".
        if CLOSING_HEADING in normalize(s["heading"]):
            continue
        orphans.append(s)
    report.metrics["muc co source_ids"] = f"{len(sections) - len(orphans)}/{len(sections)}"
    for s in orphans:
        report.add("evidence", WARN,
                   f'Muc "{s["heading"][:50]}" khong khai bao source_ids.',
                   line=s["line"],
                   guidance="Muc khong co bang chung do va cung khong phai huong dan thao tac thi "
                            "CAT. Xem docs/02-chuan-outline.md.")


def check_house_format(doc, sections, report: Report) -> None:
    """Format outline cua he Blog Muaban.net. Muc WARN, khong phai BLOCK.

    Day la quy uoc trinh bay cua toa soan, khong phai rang buoc noi dung. Bai co
    the dung ve chat ma lech format; nguoc lai thi khong. Nen format sai la canh
    bao de sua, khong phai cong chan.
    """
    raw = doc.raw

    for label, pattern in (("Title:", TITLE_LINE_RE), ("H1:", H1_LINE_RE)):
        m = pattern.search(raw)
        if not m:
            report.add("format", WARN, f"Thieu dong '{label}' o dau outline.",
                       guidance="Format he Blog Muaban.net mo dau bang Title: roi H1:. "
                                "Day la thu CTV doc dau tien.")
        elif not m.group(1).strip().strip('"<>'):
            report.add("format", WARN, f"Dong '{label}' chua dien noi dung.")

    m = OUTLINE_OWNER_RE.search(raw)
    if not m:
        report.add("format", WARN, "Thieu dong 'Mọi thắc mắc liên hệ người lên outline ...'.",
                   guidance="CTV can biet hoi ai khi outline khong ro. Ghi ten that cua nguoi "
                            "len outline; khong bia ten nguoi khong co that.")
    elif not m.group(1).strip().strip('"<>'):
        report.add("format", WARN, "Dong lien he nguoi len outline chua dien ten.",
                   guidance="De trong thi CTV khong biet hoi ai.")

    if not any(h.level == 2 and SAPO_HEADING in normalize(h.text) for h in doc.headings):
        report.add("format", WARN, "Sapo khong nam o muc H2.",
                   guidance="He Blog Muaban.net de sapo o H2 (khac Mogi.vn de sapo dang doan van).")

    body = [s for s in sections if CLOSING_HEADING not in normalize(s["heading"])]
    unnumbered = [s for s in body if not ROMAN_RE.match(s["raw_heading"].strip())]
    if body and unnumbered:
        report.add("format", WARN,
                   f"{len(unnumbered)}/{len(body)} muc chinh chua danh so La Ma (I., II., III.).",
                   line=unnumbered[0]["line"],
                   guidance="Heading he Blog Muaban.net co danh so. Vi du: '### I. <tieu de muc>'.")

    subs = [h for h in doc.headings if h.level == 4]
    bad_subs = [h for h in subs if not ARABIC_RE.match(h.text.strip())]
    if bad_subs:
        report.add("format", WARN,
                   f"{len(bad_subs)}/{len(subs)} muc con chua danh so A Rap (1., 2.).",
                   line=bad_subs[0].line,
                   guidance="Muc con cua he Blog Muaban.net danh so A Rap. Vi du: '#### 1. <tieu de>'.")

    closing = [s for s in sections if CLOSING_HEADING in normalize(s["heading"])]
    if not closing:
        report.add("format", WARN, "Outline khong co muc 'Lời kết'.",
                   guidance="He Blog Muaban.net bat buoc ket bai bang 'Lời kết'. Day KHONG phai "
                            "phan tom tat lai bai: no noi mong muon cua nguoi viet va keu goi "
                            "hanh dong cu the.")
    else:
        last = closing[-1]
        if sections and sections[-1]["line"] != last["line"]:
            report.add("format", WARN, "'Lời kết' khong phai muc cuoi cung.",
                       line=last["line"],
                       guidance="Loi ket dung cuoi bai. Muc nam sau no se bi doc sau khi da ket.")
        if not any(c in normalize(last["body"]) for c in CTA_HINTS):
            report.add("format", WARN, "'Lời kết' khong co keu goi hanh dong.",
                       line=last["line"],
                       guidance="Format he Blog yeu cau CTA: moi binh luan, chia se, hoac xem them "
                                "tai Muaban.net. Khong hua hen ket qua (xem CLAUDE.md quy tac 4).")


def check_shape(doc, sections, report: Report) -> None:
    for s in sections:
        low = normalize(s["heading"])
        if any(h in low for h in CONCLUSION_HINTS):
            report.add("shape", WARN,
                       f'Muc "{s["heading"][:50]}" la phan ket tom tat lai bai.',
                       line=s["line"],
                       guidance="Nguoi doc vua doc xong, khong can doc lai. Thay bang checklist "
                                "hoac buoc tiep theo cu the.")

    raw = doc.raw
    if not re.search(r"(Ước lượng độ dài|ước lượng độ dài)", raw):
        report.add("shape", WARN, "Outline khong ghi uoc luong do dai.",
                   guidance="Uoc luong suy ra tu so cau hoi va luong du lieu co that, khong dat truoc.")
    if re.search(r"\bFAQ\b", raw) and not re.search(
            r"(quan sát|Mọi người cũng hỏi|diễn đàn|khách hàng|nguồn câu hỏi)", raw):
        report.add("shape", WARN, "Co muc FAQ nhung khong ghi quan sat duoc cau hoi o dau.",
                   guidance="FAQ chi them khi co cau hoi that. Khong tu nghi ra cau hoi de co them muc.")

    has_internal = bool(re.search(r"\|\s*internal\s*\|", raw, re.I))
    has_external = bool(re.search(r"\|\s*external\s*\|", raw, re.I))
    if not has_internal:
        report.add("links", WARN, "Link map chua co dong internal nao.")
    if not has_external:
        report.add("links", WARN, "Link map chua co dong external nao.")


def check_heading_keywords(sections, primary: str, brief: dict, report: Report) -> None:
    """Moi muc chinh phai mang tu khoa chinh hoac tu khoa phu.

    Sinh ra tu mot lan bi tu choi that o cong duyet outline, ngay 24/09/2026. Nguoi
    duyet viet: *"Cac heading dang khong theo rule cua file onpage, khi khong co tu
    khoa chinh, tu khoa phu trong heading. Ngoai ra cac heading cung phai giong nhu
    doi thu, khong tu tao cac heading vo nghia nhu hien tai."*

    Chuyen da xay ra: de ne cong `check_query_ownership` — chi MOT muc duoc nhan truy
    van chinh — agent cat het tu khoa ra khoi cac tieu de con lai, va de ra nhung
    tieu de kieu "Vi sao chung tim toi noi ban o": khong noi voi ai ca, va ca nguoi
    doc lan Google deu khong biet muc do noi ve con gi.

    Hai cong nay phai di cung nhau, khong cai nao duoc hy sinh cai nao: dung MOT muc
    chua nguyen van cum tu khoa chinh, nhung MOI muc deu phai mang mot phan cum do
    hoac mot tu khoa phu. Tu khoa phu lay tu `entities` va `same_page_variants` cua
    brief, nen brief cang day thi kiem cang chat.
    """
    if not primary:
        return
    vocab = set(content_tokens(primary))
    # KHONG lay tu `questions_to_answer`: cau hoi mang theo ca tu de hoi ("vi sao",
    # "the nao", "bao nhieu"), va mot tieu de rong nhu "Vi sao chung tim toi noi ban o"
    # se khop nho may chu do — dung lan da thu va thay kiem khong bat duoc gi.
    for key in ("entities", "same_page_variants"):
        val = brief.get(key) or []
        if isinstance(val, str):
            val = [val]
        for item in val:
            vocab |= set(content_tokens(str(item)))
    # Tu de hoi va tu chung khong dinh danh duoc chu de, nen khong tinh la tu khoa.
    generic = {"gi", "sao", "vi", "la", "co", "khong", "nao", "khi", "bao", "nhieu",
               "the", "nhu", "cho", "cua", "voi", "tai", "gan", "moi", "hay"}
    vocab = {t for t in vocab if len(t) > 2 and strip_diacritics(t) not in generic}
    if not vocab:
        return

    bare = []
    for sec in sections:
        head = sec["heading"]
        if CLOSING_HEADING in normalize(head):
            continue                    # "Loi ket" la muc bat buoc cua format he Blog
        if any(t in set(content_tokens(head)) for t in vocab):
            continue
        bare.append(sec)

    report.metrics["muc mang tu khoa"] = f"{len(sections) - len(bare)}/{len(sections)}"
    for sec in bare:
        report.add("heading", WARN,
                   f'Muc "{sec["heading"][:52]}" khong mang tu khoa chinh hay tu khoa phu.',
                   line=sec["line"],
                   guidance="Quy chuan on-page cua du an (docs/10 muc A2, B3): tieu de muc phai "
                            "cho biet muc do noi ve cai gi. Dat tu khoa phu hoac mot phan cum tu "
                            "khoa chinh vao tieu de. Van giu dung MOT muc chua nguyen van cum tu "
                            "khoa chinh — hai dieu nay khong mau thuan.")


def run(outline_path: str, brief_path: str | None = None) -> Report:
    doc = parse_markdown(outline_path)
    brief = load_simple_yaml(brief_path) if brief_path and os.path.exists(brief_path) else {}
    primary = str(brief.get("primary_query") or "")
    questions = brief.get("questions_to_answer") or []
    if isinstance(questions, str):
        questions = [questions]

    report = Report(f"Outline — {outline_path}")
    sections = extract_sections(doc)
    report.metrics["so muc du kien"] = len(sections)

    check_query_ownership(sections, primary, report)
    check_heading_keywords(sections, primary, brief, report)
    check_question_coverage(sections, questions, report)
    check_evidence_declared(sections, report)
    check_house_format(doc, sections, report)
    check_shape(doc, sections, report)
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Kiem trong tam cua outline truoc khi dua len duyet.")
    ap.add_argument("outline")
    ap.add_argument("--brief", default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    brief = args.brief
    if not brief:
        candidate = os.path.join(os.path.dirname(os.path.abspath(args.outline)), "brief.yaml")
        brief = candidate if os.path.exists(candidate) else None

    report = run(args.outline, brief)
    print_report(report, show_info=args.all)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    if report.blocked:
        print("Sua het BLOCK truoc khi dua outline len cong duyet.")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
