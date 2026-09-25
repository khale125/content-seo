"""Kiem tra SEO on-page cho ban thao Markdown.

Kiem: title, meta description, slug, cau truc heading, doan mo dau, mat do
truy van chinh, do phu thuc the, lien ket noi bo/ngoai, anchor, anh va alt, schema,
va HTML trang tri con sot trong ban thao.

Chay:
  python scripts/onpage_check.py work/<slug>/article.md --brief work/<slug>/brief.yaml
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys

from qa_common import (
    BLOCK, WARN, INFO, Report, MD_IMAGE_RE, MD_LINK_RE, HTML_LINK_RE,
    compile_pattern, content_tokens, force_utf8_stdout, load_lexicon,
    load_simple_yaml, normalize, parse_markdown, print_report, query_coverage,
    split_sentences, strip_diacritics, strip_inline_markdown, word_count,
)

BOLD_RE = re.compile(r"(\*\*|__)(.+?)\1", re.S)

TITLE_MIN, TITLE_MAX = 40, 65
TITLE_IDEAL = (50, 60)
META_MIN, META_MAX = 120, 165
SAPO_MAX_WORDS = 90
MAX_KEYWORD_DENSITY = 0.025
MIN_INTERNAL_LINKS = 1
MAX_LINKS_PER_1000 = 12
MIN_QUERY_HEADING_COVERAGE = 0.6   # mot H2 phai "nhan" cau hoi chinh
MIN_QUESTION_COVERAGE = 0.6        # moi cau hoi trong brief phai duoc tra loi

# --- Nguong theo file quy chuan on-page cua du an (docs/10-quy-chuan-onpage.md) ---
MAX_SECTION_WORDS = 230            # moi sub-heading toi da 230 chu
TITLE_KEYWORD_POSITION = 0.5       # tu khoa nen nam trong nua dau title
OPENING_WORDS = 100                # tu khoa chinh phai co trong 100 chu dau
TOC_MIN_WORDS = 1200               # bai dai hon nguong nay nen co muc luc

# Format he Blog Muaban.net (CLAUDE.md quy tac 14). Dinh nghia lai o day thay vi
# import tu outline_check: hai script chay doc lap, khong phu thuoc nhau.
CLOSING_HEADING = "lời kết"
ROMAN_RE = re.compile(r"^[IVXLC]+\s*[.)]")
ARABIC_RE = re.compile(r"^\d{1,2}\s*[.)]")
SPECIAL_CHARS = set("[]!#@$^*{}<>|~`")
VI_DIACRITICS = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
CTA_HINTS = ("xem ", "tra ", "tìm hiểu", "kiểm tra", "tính thử", "tải ", "đăng ",
             "liên hệ", "cập nhật", "so sánh", "hướng dẫn", "bạn cần", "trước khi",
             # Dong tu dan dau meta, do tu 24 bai that: 17/24 meta mo bang mot trong
             # nhung cum nay. File quy chuan goi day la "kha nang keu goi hanh dong".
             "khám phá", "bỏ túi", "tổng hợp", "tham khảo", "chia sẻ", "bật mí")

# Tu khoa chinh phai nam trong meta, va nam SOM. Do tren 24 bai that:
# 21/24 meta chua >=80% tu dac trung cua title, va CA 21 bai deu dat no trong 60 ky
# tu dau — vi tri som nhat co trung vi 9, xa nhat 25.
#
# Vi sao can chot nay: truoc do `check_meta` chi dem ky tu, dem cum keu goi va so
# xem meta co lap lai title khong. Mot cau meta khong he nhac tới bai viet noi ve
# cai gi van di qua sach. Da xay ra that: bai 001 tung co meta "UEH co toi 10 co so
# nam rai khap TPHCM nen hai chu gan truong moi nguoi mot nghia..." — khong chua cum
# "thue tro", doc len khong biet bai noi gi, va nguoi duyet tu choi dung vi the.
META_TITLE_PREFIX_MAX = 45   # cao hon muc cao nhat do duoc tren 24 bai that (43)
META_KEYWORD_HEAD = 60
META_KEYWORD_RATIO = 0.8
META_STOPWORDS = {"va", "cua", "o", "cho", "tai", "de", "voi", "tu", "cac", "nhung",
                  "mot", "la", "ve", "theo", "khi", "ngay", "gan", "tren", "trong"}
# Mac dinh khi lexicon khong co khoa tuong ung. Danh sach that nam o
# `scripts/lexicon/ai_phrases.json` (`commercial_url_hints`, `competitor_hosts`) —
# do la du lieu, khong phai logic.
COMMERCIAL_HINTS = ("affiliate", "/shop", "/san-pham", "/product", "/gio-hang",
                    "shopee.", "lazada.", "tiki.")
# Do slug cua 24 bai that: 5 den 13 tu, trung vi 7. Nguong cu la "3-6 tu" va no bat
# oan 23/24 bai — ke ca bai cung cum cua chinh blog
# (`kinh-nghiem-thue-tro-gan-truong-dai-hoc-su-pham-ky-thuat-tphcm`, 13 tu). Day la
# dung loai nguong ma quy tac 16 noi phai dem lai tren bai that truoc khi tin.
SLUG_WORDS_MIN, SLUG_WORDS_MAX = 5, 13
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INTERNAL_HOST_DEFAULT = "muaban.net"

# --- Ky thuat SEO (tab "Ki thuat SEO" cua file quy chuan, doc 2026-09-23) ---
# Do JSON-LD tren 24 bai that: BlogPosting, BreadcrumbList va ImageObject co o CA
# 24/24 bai; FAQPage chi 9/24 va dung bai co muc hoi dap that; khong bai nao co
# VideoObject, va khong bai nao co schema cho muc luc — nen "schema TOC" trong sheet
# khong ap dung (format he Blog Muaban.net cung da bo muc luc, quy tac 14).
SCHEMA_HOUSE = ("BlogPosting", "BreadcrumbList", "ImageObject")
FAQ_HEADING_RE = re.compile(r"(câu hỏi|hỏi đáp|thường gặp|faq)", re.I)
VIDEO_RE = re.compile(r"(?i)(youtube\.com|youtu\.be|vimeo\.com|<video|<iframe)")
# Sheet muc 12 doi content sach CSS inline. Bai that KHONG dat chuan do — trung vi 67
# thuoc tinh style= va 101 the <span> moi bai, do trinh soan WordPress sinh ra — nen
# do la khau CMS. Phan thuoc pham vi du an: article.md la Markdown thuan, khong tu
# mang the trang tri vao.
INLINE_HTML_RE = re.compile(r'(?i)<\s*(span|font|center|u|b|i|small|big)\b|\sstyle\s*=\s*"')
# Trang dinh nghia duoc phep link out (sheet muc 11 goi la "link out dinh nghia")
# nhung KHONG duoc lam nguon cho claim — docs/04 khong nhan trang tong hop.
DEFINITION_HOSTS = ("wikipedia.org",)
# Khoi cuoi bai. Dung de biet mot link ngoai dang nam trong than bai hay bi don het
# xuong duoi. Trung voi moc chan trong human_voice_check.
TRANSPARENCY_RE = re.compile(r"(nguồn và (phạm vi|giới hạn)|căn cứ|minh bạch|tham khảo)", re.I)

# Do anh co chu thich tren 24 bai that: 6-10 anh moi bai (p10-p90), trung vi 8, cao
# nhat 19, va chi MOT bai khong co anh nao. Moi anh deu co alt — 0/1377 the <img>
# trong than bai co alt rong. Chu thich dai 7-20 tu, trung vi 12,5.
IMAGES_MIN, IMAGES_MAX = 6, 10
CAPTION_WORDS_MIN, CAPTION_WORDS_MAX = 7, 20


def _get(brief: dict, *keys, default=None):
    for k in keys:
        if k in brief and brief[k] not in ("", [], None):
            return brief[k]
    return default


def collect_links(doc):
    """Tra ve list (anchor, url, line, is_image)."""
    out = []
    for lineno, line in enumerate(doc.lines, start=1):
        for m in MD_IMAGE_RE.finditer(line):
            out.append((m.group(1), m.group(2), lineno, True))
        stripped = MD_IMAGE_RE.sub(" ", line)
        for m in MD_LINK_RE.finditer(stripped):
            out.append((m.group(1), m.group(2), lineno, False))
        for m in HTML_LINK_RE.finditer(line):
            out.append((re.sub(r"<[^>]+>", "", m.group(2)), m.group(1), lineno, False))
    return out


def check_title_language(title: str, meta: str, lex, report: Report) -> None:
    """Sao ngu va cau hua hen trong title/meta khong di qua human_voice_check
    (chung nam trong front matter, khong phai than bai) nen kiem rieng o day."""
    watched = {"guarantees": BLOCK, "hype_marketing": WARN, "re_cliches": WARN}
    for cat in lex["categories"]:
        if cat["id"] not in watched:
            continue
        for pattern in cat["patterns"]:
            rx = compile_pattern(pattern)
            for field_name, value in (("title", title), ("meta", meta)):
                if not value:
                    continue
                m = rx.search(value)
                if m:
                    report.add(f"{field_name}_language", watched[cat["id"]],
                               f'{cat["label"]} trong {field_name}: "{m.group(0)}"',
                               guidance=cat.get("guidance", ""))


def check_title(title: str, primary: str, report: Report) -> None:
    if not title:
        report.add("title", BLOCK, "Thieu title.",
                   guidance="Khai bao `title` trong front matter cua article.md hoac trong seo-fields.yaml.")
        return
    n = len(title)
    report.metrics["title"] = f'"{title}" ({n} ky tu)'
    if n < TITLE_MIN:
        report.add("title", WARN, f"Title {n} ky tu, ngan hon {TITLE_MIN}.",
                   guidance="Them yeu to phan biet: dia ban, con so, pham vi.")
    elif n > TITLE_MAX:
        report.add("title", WARN, f"Title {n} ky tu, se bi cat tren di dong (nguong ~{TITLE_MAX}).",
                   guidance=f"Dua y chinh vao {TITLE_IDEAL[1]} ky tu dau.")
    if primary:
        occurrences = normalize(title).count(normalize(primary))
        if occurrences == 0:
            # Truy van dai kieu hoi thoai gan nhu khong khop nguyen cum trong title;
            # do do phu tu thay vi doi khop, giong cach check_density lam.
            cov = query_coverage(primary, title)
            if cov < MIN_QUERY_HEADING_COVERAGE:
                report.add("title", WARN,
                           f"Title chi phu {cov:.0%} tu cua truy van chinh.",
                           guidance="Dua cac tu chinh cua truy van vao nua dau title, viet tu nhien. "
                                    "Khong can khop nguyen cum.")
        elif occurrences > 1:
            report.add("title", BLOCK, "Truy van chinh lap lai trong title.",
                       guidance="Lap tu khoa trong title la nhoi tu khoa. Viet lai thanh mot cum tu nhien.")
    if title.count("|") + title.count("-") >= 3:
        report.add("title", WARN, "Title co nhieu dau phan tach, de thanh chuoi tu khoa.",
                   guidance="Toi da mot dau phan tach.")


def check_meta(meta: str, title: str, report: Report) -> None:
    if not meta:
        report.add("meta", WARN, "Thieu meta description.",
                   guidance="140-160 ky tu, noi ket qua nguoi doc nhan duoc.")
        return
    n = len(meta)
    report.metrics["meta description"] = f"{n} ky tu"
    if n < META_MIN:
        report.add("meta", WARN, f"Meta {n} ky tu, ngan hon {META_MIN}.")
    elif n > META_MAX:
        report.add("meta", WARN, f"Meta {n} ky tu, se bi cat (nguong ~{META_MAX}).")
    # Nguong cu la 30 ky tu dau, va no bat oan 6/24 bai that. Ly do: khuon cua blog
    # la meta MO DAU bang chinh cum tu khoa — tuc bang dung phan dau cua title — roi
    # moi re sang noi dung khac ("Kinh nghiem thue phong tro Quan 11 *chi tiet tu cach
    # chon khu vuc...*"). Do doan dau trung nhau tren 24 bai that: trung vi 0, cao nhat
    # 43 ky tu. Nen nguong dat tren muc cao nhat do; duoi no la lap tu khoa, tren no
    # moi la chep lai title.
    if title:
        same = 0
        for a, b in zip(normalize(title), normalize(meta)):
            if a != b:
                break
            same += 1
        if same > META_TITLE_PREFIX_MAX:
            report.add("meta", WARN,
                       "Meta chep lai %d ky tu dau cua title." % same,
                       guidance="Lap lai cum tu khoa o dau meta la dung khuon nha (6/24 bai that "
                                "lam vay, trung toi da 43 ky tu). Nhung chep dai hon the thi meta "
                                "khong con bo sung gi: sau cum tu khoa phai re sang nhung thu bai "
                                "tra loi.")


def check_slug(slug: str, report: Report) -> None:
    if not slug:
        report.add("slug", WARN, "Thieu slug.")
        return
    report.metrics["slug"] = slug
    if not SLUG_RE.match(slug):
        report.add("slug", BLOCK, f"Slug khong hop le: '{slug}'.",
                   guidance="Chi chu thuong khong dau, so va dau gach noi.")
        return
    parts = slug.split("-")
    if len(parts) > SLUG_WORDS_MAX:
        report.add("slug", WARN,
                   f"Slug {len(parts)} tu, dai hon moi slug that ({SLUG_WORDS_MAX} tu).",
                   guidance="File quy chuan noi URL phai ngan nhat co the ma van bao ham toan y, "
                            "va canh bao rang URL qua ngan chi chua keyword chinh cung la con dao "
                            "hai luoi. Rut bot tu thua, dung cat cum ghep.")
    elif len(parts) < SLUG_WORDS_MIN:
        report.add("slug", WARN,
                   f"Slug {len(parts)} tu, ngan hon moi slug that ({SLUG_WORDS_MIN} tu).",
                   guidance="Slug qua ngan thi khong bao ham duoc y cua bai.")
    if re.search(r"-20\d{2}$", slug):
        report.add("slug", WARN, "Slug chua nam.",
                   guidance="Bai duoc cap nhat hang nam thi slug co nam se bi cu hoac phai doi URL.")


def check_headings(doc, primary: str, report: Report) -> None:
    headings = doc.headings
    if not headings:
        report.add("heading", BLOCK, "Bai khong co heading nao.")
        return
    h1s = [h for h in headings if h.level == 1]
    report.metrics["so heading"] = f"H1={len(h1s)}, tong={len(headings)}"

    if len(h1s) > 1:
        report.add("heading", BLOCK, f"Co {len(h1s)} the H1.", line=h1s[1].line,
                   guidance="Chi mot H1 duy nhat la tieu de bai.")

    prev = h1s[0].level if h1s else headings[0].level
    for h in headings:
        if h.level > prev + 1:
            report.add("heading", WARN, f"Nhay cap H{prev} -> H{h.level}.", line=h.line,
                       snippet=h.text, guidance="Khong bo qua cap heading.")
        prev = h.level

    subs = [h for h in headings if h.level >= 2]
    if primary and subs:
        pn = normalize(primary)
        stuffed = [h for h in subs if pn in normalize(h.text)]
        if len(stuffed) > max(1, len(subs) * 0.4):
            # Truoc day day la BLOCK. Blog Muaban.net that su lap cum tu khoa chinh o
            # 5-6 heading trong cung mot bai, va chu du an da chon lay giong blog lam
            # chuan (CLAUDE.md quy tac 15), nen no khong con chan bai.
            # Ha xuong INFO chu khong xoa han: nhoi tu khoa van la rui ro chinh sach
            # Google (quy tac 6), nguoi duyet can nhin thay con so nay.
            report.add("heading", INFO,
                       f"{len(stuffed)}/{len(subs)} heading chua nguyen truy van chinh.",
                       line=stuffed[0].line,
                       guidance="Blog that cung lap tu khoa o nhieu heading nen day khong con la "
                                "loi chan. Van nen kiem lai tung heading co dung la cau hoi that "
                                "cua nguoi doc khong. Xem docs/06-chinh-sach-google.md.")

    # Heading trung nhau
    seen: dict[str, int] = {}
    for h in subs:
        key = normalize(h.text)
        if key in seen:
            report.add("heading", WARN, f'Heading trung: "{h.text}".', line=h.line,
                       guidance=f"Da xuat hien o dong {seen[key]}. Gop hai muc hoac viet lai.")
        seen[key] = h.line


def check_focus(doc, primary: str, questions, report: Report) -> None:
    """Bai co dung trong tam khong.

    Hai loi nguoc nhau deu lam hong bai:
      - Nhoi truy van vao moi heading  -> check_headings() chan (BLOCK).
      - KHONG heading nao nhan cau hoi chinh -> chan o day.
    Ne loi thu nhat qua tay se roi thang vao loi thu hai: bai doc thi hay nhung
    khong tra loi dung cau nguoi ta go vao o tim kiem.
    """
    subs = [h for h in doc.headings if h.level >= 2]
    if not primary or not subs:
        return

    # Format he Blog Muaban.net (quy tac 14) dat sapo o H2 va cac muc chinh o H3.
    # Neu van do "muc dau tien" bang H2 thi moi bai dung format nay deu bi canh
    # bao oan, vi H2 dau luon la sapo. Bai co muc chinh danh so La Ma o H3 thi
    # "muc dau tien" phai tinh tu H3.
    house = [h for h in doc.headings if h.level == 3 and ROMAN_RE.match(h.text.strip())]
    first = house[0] if house else subs[0]

    scored = [(query_coverage(primary, h.text), h) for h in subs]
    best_cov, best_h = max(scored, key=lambda x: x[0])
    report.metrics["heading nhan cau hoi chinh"] = (
        f"{best_cov:.0%} — \"{best_h.text[:46]}\"" if best_cov else "khong co")

    if best_cov < MIN_QUERY_HEADING_COVERAGE:
        missing = [t for t in dict.fromkeys(content_tokens(primary))
                   if t not in set(content_tokens(" ".join(h.text for h in subs)))]
        report.add("focus", BLOCK,
                   f"Khong heading nao nhan cau hoi chinh (cao nhat {best_cov:.0%}).",
                   line=subs[0].line,
                   snippet=f'truy van: "{primary}"',
                   guidance="Dat DUNG MOT H2 tra loi thang truy van chinh, viet thanh cau hoi that "
                            "cua nguoi doc, va dat no LEN DAU. Cac H2 con lai khong lap lai truy van. "
                            + (f"Tu con thieu o moi heading: {', '.join(missing[:8])}. " if missing else "")
                            + "Xem docs/02-chuan-outline.md muc 'Mot H2 phai nhan cau hoi chinh'.")
        return

    first_cov = query_coverage(primary, first.text)
    if first_cov < MIN_QUERY_HEADING_COVERAGE:
        report.add("focus", WARN,
                   f'Muc dau tien khong nhan cau hoi chinh; muc nhan no la "{best_h.text[:50]}" '
                   f"(dong {best_h.line}).",
                   line=first.line,
                   guidance="Tra loi truoc, giai thich sau. Dua muc tra loi thang truy van len dau, "
                            "phan dan dat va dieu kien dua xuong duoi.")

    if questions:
        body = doc.body_text
        weak = [q for q in questions if str(q).strip()
                and query_coverage(str(q), body) < MIN_QUESTION_COVERAGE]
        report.metrics["cau hoi brief duoc tra loi"] = f"{len(questions) - len(weak)}/{len(questions)}"
        if weak:
            report.add("focus", WARN,
                       f"{len(weak)} cau hoi trong brief chua thay duoc tra loi trong bai.",
                       snippet=" | ".join(str(q)[:52] for q in weak[:3]),
                       guidance="Tra loi cho du, hoac bo cau hoi do khoi brief neu no khong con "
                                "thuoc pham vi bai. Dung de brief hua mot dang va bai giao mot dang.")


def has_diacritics(text: str) -> bool:
    return any(c in VI_DIACRITICS for c in text.lower())


def check_title_standard(title: str, slug: str, h1: str, primary: str, report: Report) -> None:
    """Cac tieu chuan title/H1 lay tu file quy chuan on-page cua du an."""
    if not title:
        return

    if primary:
        pos = normalize(title).find(normalize(primary))
        if pos < 0:
            toks = content_tokens(primary)
            positions = [normalize(title).find(t) for t in toks]
            positions = [p for p in positions if p >= 0]
            pos = min(positions) if positions else -1
        if pos >= 0 and len(title) and pos / len(title) > TITLE_KEYWORD_POSITION:
            report.add("title", WARN,
                       f"Tu khoa chinh nam o {pos / len(title):.0%} chieu dai title.",
                       guidance="Tu khoa cang gan ben trai cang tot. Dua cum tu khoa len dau title.")

    if not has_diacritics(title):
        report.add("title", WARN, "Title khong co dau tieng Viet.",
                   guidance="Toan bo title phai co dau.")

    bad = sorted(set(title) & SPECIAL_CHARS)
    if bad:
        report.add("title", WARN, "Title chua ky tu dac biet: " + " ".join(bad),
                   guidance="Bo cac ky tu [ ] ! # @ $ khoi title.")

    if slug:
        t = re.sub(r"[^a-z0-9]+", "-", strip_diacritics(title).lower()).strip("-")
        if t == slug:
            report.add("title", WARN, "Title trung 100% voi URL.",
                       guidance="Tu khoa o title khong nen giong chinh xac URL. "
                                "Them yeu to phan biet vao title, giu slug ngan.")

    if h1 and title:
        if normalize(h1) == normalize(title):
            report.add("heading", WARN, "H1 trung nguyen van Title.",
                       guidance="H1 nen dung bien the dai hon hoac goc nhin khac, "
                                "khong lap y het title.")
    if h1 and slug:
        h = re.sub(r"[^a-z0-9]+", "-", strip_diacritics(h1).lower()).strip("-")
        if h == slug:
            report.add("heading", WARN, "H1 trung nguyen van URL.")
    if h1:
        bad = sorted(set(h1) & SPECIAL_CHARS)
        if bad:
            report.add("heading", WARN, "H1 chua ky tu dac biet: " + " ".join(bad))

    # H1 phai bam search intent cua truy van chinh, khong chi khac Title. Nguoi duyet
    # tu choi mot bai voi ly do: *"Title va meta description, h1 cung phai bam sat theo
    # search intent cua tu khoa chinh"*. Bai do co Title va meta deu mo bang "... la diem
    # gi?" trong khi H1 lai la "... dan gian noi gi va vi sao chung bay vao" — cung chu
    # de nhung khong phai cau nguoi doc go.
    if primary and h1 and query_coverage(primary, h1) < 0.6:
        report.add("heading", WARN, "H1 khong bam truy van chinh.",
                   guidance=f"H1 phai chua y nguoi doc di tim, o day la \"{primary}\". Van giu H1 "
                            "khac Title de hai the khong trung nhau.")

def check_section_length(doc, report: Report) -> None:
    """Moi sub-heading toi da 230 chu (theo file quy chuan)."""
    subs = [h for h in doc.headings if h.level >= 2]
    if not subs:
        return
    long_ones = []
    for i, h in enumerate(subs):
        stop = subs[i + 1].line if i + 1 < len(subs) else len(doc.lines) + 1
        body = " ".join(doc.lines[h.line:stop - 1])
        n = word_count(strip_inline_markdown(body))
        if n > MAX_SECTION_WORDS:
            long_ones.append((h, n))
    report.metrics["muc dai nhat"] = (
        f"{max((n for _, n in long_ones), default=0)} tu" if long_ones else f"<= {MAX_SECTION_WORDS} tu")
    for h, n in long_ones[:5]:
        report.add("section_length", WARN,
                   f'Muc "{h.text[:44]}" dai {n} tu, vuot {MAX_SECTION_WORDS}.',
                   line=h.line,
                   guidance=f"File quy chuan dat moi sub-heading toi da {MAX_SECTION_WORDS} chu. "
                            "Tach them heading con, hoac cat bot.")


def check_keyword_positions(doc, primary: str, report: Report) -> None:
    """Tu khoa chinh o 100 chu dau, co in dam, va o doan ket."""
    if not primary:
        return
    paragraphs = [b for b in doc.blocks if b.kind in ("paragraph", "list")]
    if not paragraphs:
        return

    opening, count = [], 0
    for b in paragraphs:
        opening.append(b.text)
        count += word_count(b.text)
        if count >= OPENING_WORDS:
            break
    opening_text = " ".join(opening)
    cov = query_coverage(primary, opening_text)
    report.metrics[f"tu khoa trong {OPENING_WORDS} chu dau"] = f"{cov:.0%}"
    if cov < MIN_QUERY_HEADING_COVERAGE:
        report.add("keyword_position", WARN,
                   f"Tu khoa chinh chi phu {cov:.0%} trong {OPENING_WORDS} chu dau.",
                   guidance="File quy chuan yeu cau tu khoa chinh xuat hien trong 100 chu dau. "
                            "Chen tu nhien, khong duoc lam mat mach lac cua doan.")

    bold_spans = [m.group(2) for m in BOLD_RE.finditer(doc.raw)]
    bolded = any(query_coverage(primary, b) >= MIN_QUERY_HEADING_COVERAGE for b in bold_spans)
    if not bolded:
        report.add("keyword_position", WARN,
                   "Tu khoa chinh chua duoc in dam o dau.",
                   guidance="File quy chuan yeu cau in dam tu khoa chinh (dung <strong>, khong dung <b>). "
                            "In dam mot lan o cho co nghia nhat, khong in dam moi lan xuat hien.")

    # "Doan ket bai" = muc cuoi cua THAN BAI, khong tinh khoi nguon/can cu o phu luc.
    APPENDIX = ("nguồn", "căn cứ", "tham khảo", "tài liệu", "phụ lục")
    body_headings = [h for h in doc.headings if h.level >= 2
                     and not any(a in normalize(h.text) for a in APPENDIX)]
    if body_headings:
        last_line = body_headings[-1].line
        stop_lines = [h.line for h in doc.headings
                      if h.level >= 2 and h.line > last_line]
        stop = min(stop_lines) if stop_lines else len(doc.lines) + 1
        tail = " ".join(b.text for b in paragraphs if last_line < b.line < stop)
    else:
        tail = " ".join(b.text for b in paragraphs[-3:])
    tail_cov = query_coverage(primary, tail)
    if tail_cov < MIN_QUERY_HEADING_COVERAGE:
        report.add("keyword_position", WARN,
                   f"Doan ket bai chua nhac tu khoa chinh (phu {tail_cov:.0%}).",
                   guidance="File quy chuan yeu cau doan ket chua tu khoa chinh. "
                            "Viet tu nhien trong cau chot viec nguoi doc lam tiep.")

    if re.search(r"<b>|<bold>", doc.raw, re.I):
        report.add("keyword_position", WARN, "Dung the <b> hoac <bold> de in dam.",
                   guidance="File quy chuan yeu cau dung <strong>.")


def check_overoptimized_headings(doc, primary: str, report: Report) -> None:
    """Cum tu khoa chinh xuat hien nguyen van o tu 2 sub-heading tro len."""
    if not primary:
        return
    pn = normalize(primary)
    hits = [h for h in doc.headings if h.level >= 2 and pn in normalize(h.text)]
    if len(hits) >= 2:
        report.add("heading", INFO,
                   f"{len(hits)} sub-heading chua nguyen van cum tu khoa chinh.",
                   line=hits[1].line,
                   guidance="Dung MOT muc nhan cau hoi chinh. Cac muc con lai dung tu khoa phu va "
                            "semantic. Xem docs/10-quy-chuan-onpage.md muc B3.")


def check_house_format(doc, report: Report) -> None:
    """Format he Blog Muaban.net tren BAI VIET (CLAUDE.md quy tac 14).

    outline_check.py kiem o outline; ham nay kiem bai giu dung cau truc do.
    Muc WARN: day la quy uoc trinh bay cua toa soan, khong phai rang buoc noi dung.

    Khong doi tieu de cua H2 sapo phai la chu "Sapo" — chi doi co mot H2 dung
    truoc toan bo muc chinh, de toa soan tu do dat ten doc duoc cho nguoi doc.
    """
    h2 = [h for h in doc.headings if h.level == 2]
    h3 = [h for h in doc.headings if h.level == 3]
    h4 = [h for h in doc.headings if h.level == 4]

    if not h3:
        report.add("house_format", WARN,
                   "Bai khong co muc chinh nao o cap H3.",
                   guidance="He Blog Muaban.net dat sapo o H2 va cac muc chinh o H3 danh so La Ma. "
                            "Xem docs/02 muc 'Format outline cua he Blog Muaban.net'.")
        return

    if not h2 or h2[0].line > h3[0].line:
        report.add("house_format", WARN, "Khong co muc H2 (sapo) dung truoc cac muc chinh.",
                   line=h3[0].line,
                   guidance="Sapo dat o H2, cac muc chinh o H3. Day la diem khac giua he Blog "
                            "Muaban.net va he Mogi.vn trong cung sheet format.")

    body = [h for h in h3 if CLOSING_HEADING not in normalize(h.text)]
    unnumbered = [h for h in body if not ROMAN_RE.match(h.text.strip())]
    if body and unnumbered:
        report.add("house_format", WARN,
                   f"{len(unnumbered)}/{len(body)} muc chinh chua danh so La Ma (I., II., III.).",
                   line=unnumbered[0].line,
                   guidance="Vi du: '### I. <tieu de muc>'.")

    bad_subs = [h for h in h4 if not ARABIC_RE.match(h.text.strip())]
    if bad_subs:
        report.add("house_format", WARN,
                   f"{len(bad_subs)}/{len(h4)} muc con chua danh so A Rap (1., 2.).",
                   line=bad_subs[0].line, guidance="Vi du: '#### 1. <tieu de>'.")

    if not any(CLOSING_HEADING in normalize(h.text) for h in h3):
        report.add("house_format", WARN, "Bai khong co muc 'Lời kết'.",
                   guidance="He Blog Muaban.net bat buoc ket bai bang 'Lời kết': mong muon nguoi "
                            "viet + MOT keu goi hanh dong. Khong phai phan tom tat lai bai.")


def check_toc_and_captions(doc, report: Report) -> None:
    words = word_count(doc.body_text)
    raw_low = normalize(doc.raw)
    has_toc = any(k in raw_low for k in ("mục lục", "nội dung chính", "[toc]", "table of content"))
    # Format he Blog Muaban.net (quy tac 14) khong co muc luc: cac muc chinh danh
    # so La Ma da lam nhiem vu do. docs/10 muc A6 doi TOC cho bai dai, nhung do la
    # khuyen nghi (WARN) con quy tac 14 la bat buoc — nen format nha thang.
    house = any(h.level == 3 and ROMAN_RE.match(h.text.strip()) for h in doc.headings)
    if words > TOC_MIN_WORDS and not has_toc and not house:
        report.add("toc", WARN,
                   f"Bai {words} tu nhung khong co muc luc.",
                   guidance=f"File quy chuan yeu cau bai dai co TOC. Them muc luc o dau bai, "
                            "anchor nhay dung heading.")

    images = [l for l in collect_links(doc) if l[3]]
    if images:
        captioned = 0

        # Khuon cua du an (docs/14 muc A4, skill seo-writer-bds) dat MOT DONG TRONG giua
        # anh va chu thich in nghieng. Truoc day ham nay chi nhin dung dong ke ben, nen
        # bao "6/6 anh khong co caption" tren chinh bai viet dung khuon — lo ra lan dau
        # tien bai 002 co anh that. Bo qua dong trong, toi da hai dong.
        def near(lineno: int, step: int) -> str:
            i = lineno - 1 + step
            for _ in range(3):
                if not 0 <= i < len(doc.lines):
                    return ""
                if doc.lines[i].strip():
                    return doc.lines[i]
                i += step
            return ""

        # Chi nhin XUONG khi bo qua dong trong: nhin len se vo phai chu thich cua anh
        # dung truoc, hoac mot doan van co chu in dam, roi tinh nham la co caption.
        # Dong ke ben phia tren thi van nhan nhu cu, de bai cu khong doi ket qua.
        whole_italic = re.compile(r"^\s*(\*[^*\s].*[^*\s]\*|_[^_\s].*[^_\s]_|>.+)\s*$")
        for _, _, lineno, _ in images:
            nxt = near(lineno, +1)
            prv = doc.lines[lineno - 2] if lineno >= 2 else ""
            if whole_italic.match(nxt) or \
                    re.search(r"(\*.+\*|_.+_|^\s*>|caption|chú thích)", prv, re.I) or \
                    re.search(r"(caption|chú thích)", nxt, re.I):
                captioned += 1
        report.metrics["anh co caption"] = f"{captioned}/{len(images)}"
        if captioned < len(images):
            report.add("images", WARN,
                       f"{len(images) - captioned}/{len(images)} anh khong co caption.",
                       guidance="File quy chuan yeu cau moi anh co caption mo ta phu hop bai viet.")


def check_meta_keyword(meta: str, primary: str, report: Report) -> None:
    """Meta phai nhac truy van chinh, va nhac som. Xem chu thich o META_KEYWORD_HEAD.

    So sanh sau khi bo dau va bo hu tu, nen meta khong buoc phai chep nguyen van cum
    tu khoa — dung nhu file quy chuan noi: "khong nhat thiet phai chen chinh xac
    keyword". Chi doi bai co nhac tới chu de bang chinh chu nguoi doc se go.
    """
    if not meta or not primary:
        return
    want = [w for w in re.findall(r"[^\W_]+", strip_diacritics(normalize(primary)), re.UNICODE)
            if w not in META_STOPWORDS]
    if not want:
        return
    flat = strip_diacritics(normalize(meta))
    hits = [w for w in want if w in flat]
    ratio = len(hits) / len(want)
    report.metrics["tu khoa trong meta"] = "%d/%d tu" % (len(hits), len(want))
    if ratio < META_KEYWORD_RATIO:
        missing = [w for w in want if w not in flat]
        report.add("meta", WARN,
                   "Meta khong nhac truy van chinh (thieu: %s)." % ", ".join(missing[:6]),
                   guidance="21/24 bai that dat gan nguyen cum tu khoa vao meta. Nguoi doc "
                            "quet trang ket qua bang chinh chu ho vua go; meta khong co cum "
                            "do thi khong ai biet bai noi gi. Khuon cua blog: <dong tu dan> + "
                            "<cum tu khoa> + ':' + <3-5 thu bai tra loi> + <loi ich>.")
        return
    pos = min(flat.find(w) for w in hits)
    if pos > META_KEYWORD_HEAD:
        report.add("meta", WARN,
                   "Truy van chinh xuat hien o ky tu %d cua meta, muon hon bai that." % pos,
                   guidance="Ca 21 bai that co tu khoa trong meta deu dat no trong %d ky tu dau "
                            "(trung vi ky tu thu 9). Dua cum tu khoa len ngay dau cau."
                            % META_KEYWORD_HEAD)


def check_meta_cta(meta: str, report: Report) -> None:
    if not meta:
        return
    if not any(h in normalize(meta) for h in CTA_HINTS):
        report.add("meta", WARN, "Meta description khong co cau keu goi hanh dong.",
                   guidance="File quy chuan yeu cau meta co kha nang keu goi hanh dong. "
                            "Noi nguoi doc lam duoc gi sau khi doc.")


# Lien ket toi mot BAI KHAC tren blog di theo khuon rieng cua toa soan: mot dong dung
# mot minh, mo dau bang "Xem them:" in dam, anchor la TIEU DE bai dich, dat giua hai
# muc. Chu du an gui anh chup bai dang dang de lam mau. Truoc do toi dan lien ket kieu
# khac hai lan va bi tu choi ca hai: mot lan viet thanh cau van chen giua muc, mot lan
# dung han mot muc lac de de nuoi lien ket.
SEE_ALSO_LINE_RE = re.compile(r"^\s*(\*\*)?\s*xem thêm\s*:?", re.I)


def check_see_also_format(doc, internal_host: str, report: Report) -> None:
    """Lien ket toi bai khac tren blog phai nam tren mot dong "Xem them:" rieng."""
    for anchor_text, url, lineno, is_img in collect_links(doc):
        if is_img:
            continue
        low = url.lower()
        if internal_host not in low or "/blog/" not in low:
            continue
        line = doc.lines[lineno - 1] if 0 < lineno <= len(doc.lines) else ""
        if SEE_ALSO_LINE_RE.match(line):
            continue
        report.add("links", WARN,
                   f'Lien ket toi bai khac khong theo khuon "Xem them": {url[:60]}',
                   line=lineno,
                   guidance='Dat no tren mot dong rieng giua hai muc, dang '
                            '`**Xem thêm:** [<tieu de bai dich>](<url>)`. Khong viet thanh cau van '
                            "chen giua muc, va khong dung them mot muc moi chi de chua lien ket.")


def check_outlink_quality(doc, lex, internal_host: str, report: Report) -> None:
    """Sheet muc 11: khong link out toi trang affiliate, trang ban hang, trang doi thu."""
    hints = tuple(lex.get("commercial_url_hints") or COMMERCIAL_HINTS)
    rivals = tuple(lex.get("competitor_hosts") or ())
    for anchor, url, lineno, is_img in collect_links(doc):
        if is_img or not url.lower().startswith("http"):
            continue
        if internal_host in url.lower():
            continue
        low = url.lower()
        if any(h in low for h in rivals):
            report.add("links", WARN, f"Lien ket ngoai tro toi san tin dang doi thu: {url[:60]}",
                       line=lineno,
                       guidance="File quy chuan cam outlink toi trang doi thu, tru bai dinh nghia ma "
                                "ho dang xep hang cao. Thay bang nguon goc hoac bo link.")
        elif any(h in low for h in hints):
            report.add("links", WARN,
                       f"Lien ket ngoai tro toi trang thuong mai hoac ban hang: {url[:60]}",
                       line=lineno,
                       guidance="File quy chuan cam outlink toi trang affiliate, trang ban hang va "
                                "trang dich vu. Neu day la lien ket tai tro thi nguoi dang bai phai "
                                'gan rel="sponsored nofollow" — bai that lam dung nhu vay.')


# Sapo KHONG mang ngay cap nhat. Do tren 24 bai that: 0/24 sapo co ngay hay cum
# "cap nhat" — WordPress da hien ngay sua cho moi bai, nen viet lai trong sapo vua
# thua vua lam cau mo bai cut y. Nguoi duyet tu choi mot bai dung vi cho nay.
SAPO_DATE_RE = re.compile(r"(cập nhật (tới|đến|ngày)|\d{1,2}/\d{1,2}/20\d\d)", re.I)
# Sapo cua bai that ket bang mot loi moi doc tiep. Cac cum nay nam trong
# house_voice_allowed, tuc da duoc chu du an giu lai co y (quy tac 15).
SAPO_CTA_RE = re.compile(
    r"(mời bạn|cùng (theo dõi|tìm hiểu|khám phá)|bài viết (dưới đây|sau đây)|"
    r"theo dõi bài viết|ngay sau đây)", re.I)


def check_sapo(doc, primary: str, report: Report) -> None:
    first = next((b for b in doc.blocks if b.kind == "paragraph"), None)
    if not first:
        report.add("sapo", WARN, "Khong tim thay doan mo dau.")
        return
    n_words = word_count(first.text)
    n_sent = len(split_sentences(first.text))
    report.metrics["sapo"] = f"{n_sent} cau / {n_words} tu"
    if SAPO_DATE_RE.search(first.text) or SAPO_DATE_RE.search(
            next((h.text for h in doc.headings if h.level == 2), "")):
        report.add("sapo", WARN, "Sapo co ngay cap nhat.", line=first.line,
                   guidance="0/24 sapo cua bai that co ngay. WordPress da hien ngay sua bai, nen "
                            "moc du lieu chi can nam o khoi minh bach cuoi bai. Bo cum 'cap nhat "
                            "toi ...' khoi sapo.")
    # Loi moi doc tiep nam o DONG SAPO H2 voi 13/24 bai that, khong phai o doan van.
    # Lan dau ham nay chi soi doan dau va bat oan ca bai mau cua chinh du an.
    sapo_h2 = next((h.text for h in doc.headings if h.level == 2), "")
    sapo_all = first.text + " " + sapo_h2
    # Cau moi doc tiep phai keo nguoi doc bang CHINH thu ho di tim. Nguoi duyet tu choi
    # mot bai vi CTA moi doc "de biet nen lam gi voi con chuon chuon dang bay trong
    # phong", trong khi truy van la "chuon chuon bay vao nha la diem gi": *"Keu goi xem
    # bai viet de biet duoc chuon chuon bay vao nha la diem gi chu, day moi la search
    # intent nguoi dung muon tim"*. Day la quyet dinh bien tap cua chu du an, khong phai
    # so do tu kho bai that.
    if primary and SAPO_CTA_RE.search(sapo_all):
        cta = next((sen for sen in split_sentences(sapo_all) if SAPO_CTA_RE.search(sen)), "")
        if cta and query_coverage(primary, cta) < 0.6:
            report.add("sapo", WARN, "Cau moi doc tiep khong nhac truy van chinh.",
                       line=first.line,
                       guidance="CTA phai keo nguoi doc bang chinh cau ho vua go, vi du 'de biet "
                                f"{primary} la gi'. Moi doc mot y phu la lech search intent.")
    if not SAPO_CTA_RE.search(sapo_all):
        report.add("sapo", WARN, "Sapo khong moi nguoi doc di tiep.", line=first.line,
                   guidance="Bai that ket sapo bang mot loi moi doc tiep, vi du 'Moi ban cung theo "
                            "doi bai viet duoi day cua Muaban.net de ...'. Cau do cho nguoi doc biet "
                            "phan sau tra loi gi.")
    if n_words > SAPO_MAX_WORDS:
        report.add("sapo", WARN, f"Sapo {n_words} tu, dai hon {SAPO_MAX_WORDS}.", line=first.line,
                   guidance="2-4 cau tra loi thang truy van chinh. Phan con lai dua xuong duoi.")
    if n_sent > 5:
        report.add("sapo", WARN, f"Sapo {n_sent} cau.", line=first.line)
    if primary and normalize(primary) not in normalize(first.text):
        report.add("sapo", INFO, "Sapo khong nhac truy van chinh.",
                   line=first.line,
                   guidance="Khong bat buoc, nhung sapo nen tra loi dung cau hoi nguoi doc go vao.")


def check_density(doc, primary: str, entities, report: Report) -> None:
    body = normalize(doc.body_text)
    total = max(word_count(doc.body_text), 1)
    if primary:
        pn = normalize(primary)
        tokens = [t for t in pn.split() if len(t) > 1]
        hits = body.count(pn)
        density = hits * len(tokens) / total
        report.metrics["mat do truy van chinh"] = f"{hits} lan ({density:.1%})"

        if density > MAX_KEYWORD_DENSITY:
            report.add("density", WARN,
                       f"Truy van chinh chiem {density:.1%} so tu ({hits} lan).",
                       guidance="Khong dat muc tieu mat do. Ty le cao thuong la dau hieu viet guong; "
                                "thay bang dai tu, tu dong nghia hoac viet lai cau.")
        elif hits == 0:
            # Truy van dai kieu hoi thoai gan nhu khong bao gio khop nguyen van, va ep
            # no vao bai chinh la viet guong. Voi truy van tu 4 tu tro len, do do phu
            # cua tung tu thay vi doi khop cum.
            if len(tokens) >= 4:
                covered = [t for t in tokens if t in body]
                ratio = len(covered) / len(tokens)
                report.metrics["do phu tu cua truy van"] = f"{len(covered)}/{len(tokens)}"
                if ratio < 0.7:
                    missing = [t for t in tokens if t not in body]
                    report.add("density", WARN,
                               "Bai khong nhac phan lon cac tu trong truy van chinh: "
                               + ", ".join(missing),
                               guidance="Khong can khop nguyen van cum truy van dai. Nhung neu bai "
                                        "thieu han cac tu chinh thi co the dang tra loi lech cau hoi.")
            else:
                report.add("density", WARN,
                           "Truy van chinh khong xuat hien lan nao trong than bai.",
                           guidance="Truy van ngan nen xuat hien it nhat mot lan mot cach tu nhien.")

    if entities:
        missing = [e for e in entities if normalize(e) not in body]
        report.metrics["thuc the phu"] = f"{len(entities) - len(missing)}/{len(entities)}"
        if missing:
            report.add("entities", WARN,
                       f"{len(missing)} thuc the trong brief khong xuat hien: " + ", ".join(missing[:6]),
                       guidance="Thuc the quan trong hon lap tu khoa. Neu thuc the khong con lien quan "
                                "thi cap nhat brief, dung bo qua.")


def check_links(doc, lex, internal_host: str, report: Report) -> None:
    links = collect_links(doc)
    anchors = [l for l in links if not l[3]]
    images = [l for l in links if l[3]]
    total_words = max(word_count(doc.body_text), 1)

    internal = [l for l in anchors if internal_host in l[1].lower() or l[1].startswith("/")]
    external = [l for l in anchors if l not in internal and l[1].lower().startswith("http")]
    report.metrics["lien ket"] = f"noi bo={len(internal)}, ngoai={len(external)}, anh={len(images)}"

    if len(internal) < MIN_INTERNAL_LINKS:
        report.add("links", BLOCK,
                   f"Chi co {len(internal)} lien ket noi bo, toi thieu {MIN_INTERNAL_LINKS}.",
                   guidance=f"Them it nhat mot lien ket toi danh muc/tin dang {internal_host} "
                            "dung dia ban va loai hinh.")
    if not external:
        report.add("links", WARN, "Khong co lien ket toi nguon ngoai.",
                   guidance="Bai co du lieu phai dan it nhat mot nguon goc. Dan nguon la dieu kien "
                            "de bai dang tin, khong phai mat traffic.")

    per_1000 = len(anchors) / total_words * 1000
    if per_1000 > MAX_LINKS_PER_1000:
        report.add("links", WARN, f"{len(anchors)} lien ket ({per_1000:.0f}/1000 tu).",
                   guidance="Nhoi lien ket lam loang trang. 3-8 lien ket noi bo cho bai 1200-1800 tu.")

    generic = set(normalize(a) for a in lex.get("generic_anchors", []))
    for anchor, url, lineno, _ in anchors:
        a = normalize(anchor).strip(" .,:")
        if not a:
            report.add("links", BLOCK, f"Lien ket khong co anchor: {url}", line=lineno)
        elif a in generic:
            report.add("links", WARN, f'Anchor chung chung: "{anchor}"', line=lineno,
                       guidance="Anchor phai mo ta dich den, vi du 'tin dang ban can ho tai Binh Tan'.")
        elif a.startswith("http"):
            report.add("links", WARN, "Anchor la URL tho.", line=lineno,
                       guidance="Thay bang cum tu mo ta noi dung trang dich.")
        if url.lower().startswith("http://"):
            report.add("links", BLOCK, f"Lien ket khong phai HTTPS: {url}", line=lineno)
        if "?" in url and re.search(r"(utm_|fbclid|gclid)", url):
            report.add("links", WARN, f"URL con tham so theo doi: {url}", line=lineno)


def check_images(doc, primary: str, report: Report) -> None:
    images = [l for l in collect_links(doc) if l[3]]
    if not images:
        report.add("images", WARN, "Bai khong co anh nao.",
                   guidance=f"23/24 bai that co anh, thuong {IMAGES_MIN}-{IMAGES_MAX} anh "
                            "moi bai (trung vi 8) — khoang mot anh cho moi muc La Ma. Lap "
                            "image plan trong outline, tim anh theo docs/14, roi ghi "
                            "image-manifest.csv. Bieu do hay so do tu dung tu du lieu co "
                            "nguon co gia tri hon anh stock minh hoa.")
        return
    report.metrics["so anh"] = str(len(images))
    if len(images) < IMAGES_MIN:
        report.add("images", INFO,
                   f"Bai co {len(images)} anh, it hon dai cua bai that "
                   f"({IMAGES_MIN}-{IMAGES_MAX}).")
    pn = normalize(primary) if primary else ""
    for alt, src, lineno, _ in images:
        if not alt.strip():
            report.add("images", WARN, f"Anh thieu alt: {src}", line=lineno,
                       guidance="Mo ta noi dung anh cho nguoi khong nhin thay. Anh trang tri thuan "
                                'tuy thi de alt rong co y ("").')
            continue
        if pn and normalize(alt).count(pn) >= 2:
            report.add("images", BLOCK, f'Alt nhoi tu khoa: "{alt}"', line=lineno,
                       guidance="Alt la mo ta anh, khong phai cho dat tu khoa.")
        if word_count(alt) > 20:
            report.add("images", WARN, f"Alt qua dai ({word_count(alt)} tu).", line=lineno)
        fname = src.rsplit("/", 1)[-1]
        if fname and not re.match(r"^[a-z0-9._-]+$", fname):
            report.add("images", WARN, f"Ten file anh nen khong dau, chu thuong: {fname}", line=lineno)


def declared_schema(fm: dict) -> list[str]:
    out: list[str] = []
    for key in ("schema", "schema_extra", "schema_types"):
        val = fm.get(key)
        if isinstance(val, (list, tuple)):
            out.extend(str(x) for x in val)
        elif val:
            out.extend(re.split(r"[,;/+]", str(val)))
    return [x.strip().strip("\"'") for x in out if x.strip()]


def check_schema(doc, report: Report) -> None:
    """Sheet muc 13. Luat trung tam: khai bao gi trong schema thi bai phai that su co.

    Vi sao truoc do khong co ham nay: `docs/10` muc A8 liet ke day du bo schema cho bai
    blog tu 2026-09-15, nhung khong dong code nao doc truong `schema`. Bai 001 khai
    `Article` (blog that dung `BlogPosting`) va van qua sach — dung loai lo hong da xay
    ra voi meta description.
    """
    types = declared_schema(doc.front_matter)
    report.metrics["schema"] = ", ".join(types) if types else "khong khai"
    has_faq = any(FAQ_HEADING_RE.search(h.text) for h in doc.headings)
    has_image = any(link[3] for link in collect_links(doc))
    has_video = bool(VIDEO_RE.search(doc.raw))

    if not types:
        report.add("schema", WARN, "Front matter khong khai schema nao.",
                   guidance="24/24 bai that khai BlogPosting + BreadcrumbList + ImageObject. "
                            "Dien truong `schema` va `schema_extra` de nguoi dang bai gan dung bo.")
        return

    low = [t.lower() for t in types]
    if "blogposting" not in low:
        if "article" in low:
            report.add("schema", WARN, "Khai `Article` thay vi `BlogPosting`.",
                       guidance="Ca 24 bai tren blog dung BlogPosting lam mainEntityOfPage. "
                                "Doi lai cho khop template dang bai.")
        else:
            report.add("schema", WARN, "Thieu `BlogPosting` — loai schema chinh cua bai blog.")
    if "breadcrumblist" not in low:
        report.add("schema", WARN, "Thieu `BreadcrumbList` (24/24 bai that co).")
    if has_image and "imageobject" not in low:
        report.add("schema", WARN, "Bai co anh nhung khong khai `ImageObject` cho anh dai dien.")
    if has_faq and "faqpage" not in low:
        report.add("schema", WARN, "Bai co muc hoi dap nhung khong khai `FAQPage`.",
                   guidance="9/24 bai that co muc hoi dap, va ca 9 deu khai FAQPage.")

    # Ve con lai cua luat, va la ve nghiem hon: khai bao mot thu bai khong co la noi sai
    # ve chinh bai viet, cung huong voi quy tac 1.
    if "faqpage" in low and not has_faq:
        report.add("schema", BLOCK, "Khai `FAQPage` nhung bai khong co muc hoi dap hien thi.",
                   guidance="Bo khai bao, hoac viet muc hoi dap that. Schema phai khop thu nguoi "
                            "doc thay tren trang.")
    if "imageobject" in low and not has_image:
        report.add("schema", BLOCK, "Khai `ImageObject` nhung bai khong co anh nao.",
                   guidance="Them anh dai dien kem mot dong trong image-manifest.csv, hoac bo khai bao.")
    if "videoobject" in low and not has_video:
        report.add("schema", BLOCK, "Khai `VideoObject` nhung bai khong nhung video nao.")


def check_inline_html(doc, report: Report) -> None:
    """Sheet muc 12: lam sach code, content nam trong the <p>, khong CSS inline."""
    bad = [(n, line.strip()[:60]) for n, line in enumerate(doc.lines, start=1)
           if INLINE_HTML_RE.search(line)]
    if not bad:
        return
    report.add("html", WARN, f"{len(bad)} dong co the HTML trang tri hoac CSS inline.",
               line=bad[0][0],
               guidance="Giu Markdown thuan de khi len CMS content nam gon trong the <p>. "
                        "Dong: " + "; ".join(f"{n}: {t}" for n, t in bad[:5]))


def external_links(doc, internal_host: str):
    return [(anchor, url, line) for anchor, url, line, is_img in collect_links(doc)
            if not is_img and url.lower().startswith("http")
            and internal_host not in url.lower()]


def check_outlink_authority(doc, ledger_path: str | None, internal_host: str,
                            report: Report) -> None:
    """Sheet muc 11: chi link out toi nguon uy tin, khong link trang ban hang hay doi thu.

    Sheet do "uy tin" bang DR >= 20 cua Ahrefs. Du an khong co so do, va bia mot con so
    DR la vi pham quy tac 1, nen thay bang mot tieu chi do duoc: mien ngoai phai co mat
    trong `evidence-ledger.csv`, tuc da di qua thu tu uu tien nguon o docs/04.
    """
    ext = external_links(doc, internal_host)
    if not ext:
        return
    if not ledger_path or not os.path.isfile(ledger_path):
        report.add("links", INFO, "Khong co ledger nen khong doi chieu duoc mien link ngoai.")
        return

    hosts: set[str] = set()
    wiki_rows: list[tuple[str, str]] = []
    try:
        with open(ledger_path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                url = (row.get("source_url") or "").strip()
                if not url.lower().startswith("http") or url.count("/") < 2:
                    continue
                host = url.split("/")[2].lower().replace("www.", "")
                hosts.add(host)
                if any(host.endswith(d) for d in DEFINITION_HOSTS):
                    wiki_rows.append(((row.get("claim_id") or "?").strip(), host))
    except OSError as exc:
        report.add("links", INFO, f"Khong doc duoc ledger: {exc}")
        return

    for cid, host in wiki_rows:
        report.add("links", WARN, f"Ledger {cid} lay {host} lam nguon cho claim.",
                   guidance="docs/04 khong nhan trang tong hop lam nguon. Wikipedia chi duoc dung "
                            "lam link out dinh nghia; claim phai tro ve van ban goc.")

    for _anchor, url, lineno in ext:
        if url.count("/") < 2:
            continue
        host = url.split("/")[2].lower().replace("www.", "")
        if host in hosts or any(host.endswith(d) for d in DEFINITION_HOSTS):
            continue
        report.add("links", WARN, f"Mien link ngoai khong co trong ledger: {host}", line=lineno,
                   guidance="File quy chuan chi cho link out toi nguon uy tin. Du an do dieu do bang "
                            "ledger: them dong ledger cho nguon nay, hoac bo link.")


def check_outlink_placement(doc, internal_host: str, report: Report) -> None:
    """Sheet muc 11 doi HAI loai link out, khong phai mot.

    "Link out dinh nghia" nam ngay trong cau dang noi ve khai niem, anchor la tu khoa
    semantic; "link out tham khao" nam o cuoi bai. Do 20 link ngoai cua 8 bai that co
    link: vi tri tuong doi trong than bai trai tu 0,06 den 0,94, trung vi 0,45 — ho dat
    trong ruot bai chu khong don het xuong duoi.
    """
    ext = external_links(doc, internal_host)
    if not ext:
        return
    limit = next((h.line for h in doc.headings if TRANSPARENCY_RE.search(h.text)), None)
    if limit is None:
        return
    if all(line >= limit for _, _, line in ext):
        report.add("links", WARN,
                   "Moi lien ket ngoai deu nam trong khoi cuoi bai; than bai khong co link out nao.",
                   line=limit,
                   guidance="Dat mot link out dinh nghia ngay trong cau dang nhac ten van ban hoac "
                            "khai niem do, anchor la tu khoa semantic. Khoi cuoi bai giu nguyen vai "
                            "tro danh sach tham khao.")


def check_image_manifest(doc, article_path: str, report: Report) -> None:
    """Moi anh trong bai phai co mot dong trong `image-manifest.csv`, va dong do phai
    da CLEARED ban quyen.

    Vi sao la BLOCK chu khong phai WARN: dung mot tam anh chua ro quyen la rui ro phap
    ly that cho toa soan, va no khong the sua sau khi bai da dang. Quy tac nay da nam
    trong `docs/05` va `docs/07` tu dau nhung khong co cho nao doc file manifest —
    cung loai lo hong da xay ra voi meta va voi schema.
    """
    images = [l for l in collect_links(doc) if l[3]]
    folder = os.path.dirname(os.path.abspath(article_path))
    path = os.path.join(folder, "image-manifest.csv")

    if not images:
        if os.path.isfile(path):
            report.add("images", INFO, "Co image-manifest.csv nhung bai chua chen anh nao.")
        return
    if not os.path.isfile(path):
        report.add("images", BLOCK, f"Bai co {len(images)} anh nhung thieu image-manifest.csv.",
                   guidance="Copy templates/image-manifest.csv va dien mot dong cho moi anh: "
                            "nguon, tac gia, giay phep, ngay lay, alt, caption, rights_status.")
        return

    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if (r.get("file_name") or "").strip()]
    except OSError as exc:
        report.add("images", BLOCK, f"Khong doc duoc image-manifest.csv: {exc}")
        return

    by_name = {(r.get("file_name") or "").strip().lower(): r for r in rows}
    for _alt, src, lineno, _ in images:
        name = src.rsplit("/", 1)[-1].strip().lower()
        row = by_name.get(name)
        if not row:
            report.add("images", BLOCK, f"Anh khong co dong trong manifest: {name}",
                       line=lineno,
                       guidance="Moi anh phai truy duoc ve nguon va giay phep.")
            continue
        status = (row.get("rights_status") or "").strip().upper()
        if status != "CLEARED":
            report.add("images", BLOCK,
                       f"Anh {name} co rights_status = '{status or 'trong'}', chua CLEARED.",
                       line=lineno,
                       guidance="Chua ro quyen thi bo anh, thay bang anh tu dung, hoac xin "
                                "phep xong roi moi dat CLEARED.")
        for col in ("source_url", "license", "alt_text", "caption"):
            if not (row.get(col) or "").strip():
                report.add("images", WARN, f"Anh {name} thieu cot '{col}' trong manifest.",
                           line=lineno)

        # Anh lay tu internet: giay phep phai cho dung thuong mai va cho thay doi kich
        # thuoc, va neu la CC BY / BY-SA thi phai du thong tin de ghi cong. Hai dieu nay
        # khong the "giai trinh" duoc — dung sai la vi pham giay phep cua anh, nen BLOCK.
        # Anh tu dung va anh cua Muaban.net khong co source_url ben ngoai, nen bo qua.
        src = (row.get("source_url") or "").strip().lower()
        if src.startswith("http") and "muaban.net" not in src:
            from image_search import classify_license, needs_attribution
            group, why = classify_license(row.get("license") or "")
            if group is None:
                report.add("images", BLOCK, f"Anh {name}: giay phep khong dung duoc ({why}).",
                           line=lineno,
                           guidance="Blog la trang thuong mai va WordPress tu cat anh thanh "
                                    "nhieu co. Chi nhan CC0, Public Domain, CC BY, CC BY-SA.")
            elif needs_attribution(group):
                missing = [c for c in ("creator", "license_url")
                           if not (row.get(c) or "").strip()]
                if missing:
                    report.add("images", BLOCK,
                               f"Anh {name} la {row.get('license')} nhung thieu "
                               f"{', '.join(missing)} de ghi cong.",
                               line=lineno,
                               guidance="CC BY bat buoc ghi tac gia, nguon va giay phep. "
                                        "wp_draft.py in dong ghi cong tu chinh cac cot nay.")
        cap_words = word_count((row.get("caption") or "").strip())
        if cap_words and not (CAPTION_WORDS_MIN <= cap_words <= CAPTION_WORDS_MAX):
            report.add("images", INFO,
                       f"Chu thich anh {name} dai {cap_words} tu, ngoai dai bai that "
                       f"({CAPTION_WORDS_MIN}-{CAPTION_WORDS_MAX}).", line=lineno)


def run(article: str, brief_path: str | None = None, seo_path: str | None = None,
        lexicon_path: str | None = None, ledger_path: str | None = None) -> Report:
    doc = parse_markdown(article)
    lex = load_lexicon(lexicon_path)
    brief = load_simple_yaml(brief_path) if brief_path else {}
    seo = load_simple_yaml(seo_path) if seo_path else {}

    fm = doc.front_matter
    title = str(_get(seo, "title") or _get(fm, "title") or "")
    meta = str(_get(seo, "meta_description", "description") or _get(fm, "meta_description", "description") or "")
    slug = str(_get(seo, "slug") or _get(fm, "slug") or "")
    primary = str(_get(brief, "primary_query") or _get(fm, "primary_query") or "")
    entities = _get(brief, "entities", default=[]) or []
    if isinstance(entities, str):
        entities = [entities]
    questions = _get(brief, "questions_to_answer", default=[]) or []
    if isinstance(questions, str):
        questions = [questions]
    internal_host = str(_get(brief, "internal_host", default=INTERNAL_HOST_DEFAULT))

    report = Report(f"SEO on-page — {article}")
    if primary:
        report.metrics["truy van chinh"] = primary
    h1 = next((h.text for h in doc.headings if h.level == 1), "")
    check_title_language(title, meta, lex, report)
    check_title(title, primary, report)
    check_title_standard(title, slug, h1, primary, report)
    check_meta(meta, title, report)
    check_meta_cta(meta, report)
    check_meta_keyword(meta, primary, report)
    check_slug(slug, report)
    check_headings(doc, primary, report)
    check_overoptimized_headings(doc, primary, report)
    check_section_length(doc, report)
    check_focus(doc, primary, questions, report)
    check_keyword_positions(doc, primary, report)
    check_sapo(doc, primary, report)
    check_density(doc, primary, entities, report)
    check_links(doc, lex, internal_host, report)
    check_outlink_quality(doc, lex, internal_host, report)
    check_outlink_authority(doc, ledger_path, internal_host, report)
    check_outlink_placement(doc, internal_host, report)
    check_see_also_format(doc, internal_host, report)
    check_images(doc, primary, report)
    check_image_manifest(doc, article, report)
    check_toc_and_captions(doc, report)
    check_house_format(doc, report)
    check_schema(doc, report)
    check_inline_html(doc, report)
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Kiem tra SEO on-page cho ban thao Markdown.")
    ap.add_argument("article")
    ap.add_argument("--brief", default=None, help="brief.yaml (truy van chinh, thuc the)")
    ap.add_argument("--seo", default=None, help="seo-fields.yaml (title, meta, slug)")
    ap.add_argument("--lexicon", default=None)
    ap.add_argument("--ledger", default=None,
                    help="evidence-ledger.csv de doi chieu mien link ngoai; "
                         "khong truyen thi tu tim cung thu muc voi bai")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    ledger = args.ledger
    if not ledger:
        sibling = os.path.join(os.path.dirname(os.path.abspath(args.article)),
                               "evidence-ledger.csv")
        ledger = sibling if os.path.isfile(sibling) else None
    report = run(args.article, args.brief, args.seo, args.lexicon, ledger)
    print_report(report, show_info=args.all)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
