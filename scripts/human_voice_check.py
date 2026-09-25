"""Do do "nguoi that" cua ban thao tieng Viet.

Ba nhom kiem tra:
  1. Sao ngu / cau hua hen / dau vet sinh tu dong  -> tra ve tu dien lexicon.
  2. Nhip van (burstiness): do lech do dai cau, do dai doan, do dai danh sach.
  3. Chat luong noi dung: mat do so lieu, muc do co lap truong, dinh dang.
  4. Cau truc (thich ung tu blader/humanizer, MIT): tuong phan rong trai dai hai cau,
     cau chot lap lai, danh sach nhan in dam, mui ten trang tri.

Chay:  python scripts/human_voice_check.py work/<slug>/article.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

from qa_common import (
    BLOCK, WARN, INFO, Report, CLAIM_REF_RE,
    compile_pattern, excerpt, force_utf8_stdout, load_lexicon,
    normalize, parse_markdown, print_report, split_sentences, stdev, word_count,
)

# Nguong mac dinh. Doi qua --config neu bai co dac thu rieng.
MIN_BURSTINESS = 0.38        # stdev / mean do dai cau
MIN_SHORT_SENTENCE_RATIO = 0.12   # ty le cau <= 10 tu
MAX_LONG_SENTENCE_RATIO = 0.22    # ty le cau >= 35 tu
MIN_DIGIT_SENTENCE_RATIO = 0.12   # ty le cau chua so
MIN_STANCE_PER_1000 = 3.0         # so dau hieu lap truong tren 1000 tu
# Nguong nay chi con la san toi thieu. Chu so huu that cua "mat do loi khuyen" da
# chuyen sang `house_voice_check.py`: no do `advice_per_1000` theo CAU (khong phai theo
# chuoi con, vi cach cu dem "nen " trong "tro nen"), doi chieu voi dai 3,5-12,3 do tu
# 24 bai that, va do them `advice_subject_ratio` — cai quyet dinh loi khuyen co goi
# nguoi doc hay khong. Dung nang nguong o day len nua, se thanh hai bo do cung mot thu
# voi hai con so khac nhau.
MAX_EMDASH_PER_1000 = 6.0
MAX_BOLD_RATIO = 0.10             # ty le tu duoc in dam
MAX_SAME_OPENER = 7               # so lan mot cach mo cau duoc lap lai
# Nguong cu la 3, lay tu huong dan viet lach tieng Anh. Do 12 bai that tren blog thi
# bai nao cung lap cach mo cau tu 4 den 7 lan, tuc CA 12/12 deu se bi canh bao oan.
# Tieng Viet lap 'Ban nen...', 'Ngoai ra...' o dau cau la binh thuong va lam van deu
# nhip; ep doi cach vao cau moi lan chi lam van go. Nguong dat bang muc cao nhat do duoc.

CITATION_HINT_RE = re.compile(
    r"(https?://|\[C\d{1,3}\]|theo\s+(Nghi dinh|Nghị định|Thông tư|Thong tu|Luật|Luat|Quyết định|"
    r"Quyet dinh|Tổng cục|Tong cuc|Bộ |Bo |UBND|Ngân hàng Nhà nước|Ngan hang Nha nuoc))",
    re.IGNORECASE,
)
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⬀-⯿]"
)
BOLD_RE = re.compile(r"(\*\*|__)(.+?)\1", re.S)
TRIAD_RE = re.compile(r"\b(\w+),\s*(\w+)\s+và\s+(\w+)\b", re.UNICODE)


def check_lexicon(doc, lex, report: Report) -> None:
    text_lines = doc.lines
    for cat in lex["categories"]:
        severity = cat.get("severity", WARN)
        max_allowed = cat.get("max_allowed", 0)
        exempt_cited = cat.get("exempt_if_sentence_has_citation", False)
        hits: list[tuple[int, str, str]] = []

        for pattern in cat["patterns"]:
            rx = compile_pattern(pattern)
            for lineno, line in enumerate(text_lines, start=1):
                if not line.strip() or line.lstrip().startswith("<!--"):
                    continue
                for m in rx.finditer(line):
                    if exempt_cited and CITATION_HINT_RE.search(line):
                        continue
                    hits.append((lineno, m.group(0), excerpt(line.strip(), m.start())))

        if not hits:
            continue

        hits.sort()
        over = len(hits) - max_allowed
        if over <= 0:
            report.add(cat["id"], INFO,
                       f"{cat['label']}: {len(hits)} lan (trong nguong {max_allowed}).")
            continue

        # Bao cao tung vi tri, toi da 8 dong de khong tran man hinh.
        report.add(cat["id"], severity,
                   f"{cat['label']}: {len(hits)} lan, vuot nguong {max_allowed}.",
                   line=hits[0][0], guidance=cat.get("guidance", ""))
        for lineno, matched, ctx in hits[:8]:
            report.add(cat["id"], INFO, f'"{matched}"', line=lineno, snippet=ctx)
        if len(hits) > 8:
            report.add(cat["id"], INFO, f"... va {len(hits) - 8} lan nua.")


def check_rhythm(doc, report: Report) -> None:
    # Bo dong chu thich anh: nguong MAX_SAME_OPENER do tren kho bai that, noi chu
    # thich chi con la dong `[CAPTION]` va khong bao gio thanh "cau mo bang ...".
    # Dung chung ham voi house_voice_profile de hai may kiem khong lech nhau ve sau.
    from house_voice_profile import is_figure_caption
    prose_blocks = [b for b in doc.blocks if b.kind in ("paragraph", "quote")
                    and not is_figure_caption(doc, b)]
    prose = "\n".join(b.text for b in prose_blocks)
    sentences = [s for s in split_sentences(prose) if word_count(s) >= 2]

    if len(sentences) < 6:
        report.add("rhythm", INFO, "Bai qua ngan de do nhip cau.")
        return

    lengths = [word_count(s) for s in sentences]
    mean = sum(lengths) / len(lengths)
    sd = stdev(lengths)
    burst = sd / mean if mean else 0.0

    short_ratio = sum(1 for n in lengths if n <= 10) / len(lengths)
    long_ratio = sum(1 for n in lengths if n >= 35) / len(lengths)

    report.metrics["so cau"] = len(sentences)
    report.metrics["do dai cau TB"] = f"{mean:.1f} tu"
    report.metrics["burstiness"] = f"{burst:.2f} (nguong >= {MIN_BURSTINESS})"
    report.metrics["ty le cau ngan"] = f"{short_ratio:.0%}"

    # Nhip cau KHONG con kiem o day. Ba nguong cu (burstiness >= 0.38, cau ngan >= 12%,
    # cau dai <= 22%) duoc dat theo ly thuyet "van nguoi that" noi chung, va chung
    # NGUOC voi giong that cua blog Muaban.net: do 12 bai dang dang thi trung vi
    # burstiness chi 0.33 va ty le cau ngan chi 2.8%. Giu ca hai bo do se khien bai
    # nhan hai loi khuyen trai nguoc nhau — do chinh la thu da lam bai 001 bi che
    # "cung". Tu nay `house_voice_check.py` so huu phan nhip cau, doi chieu voi dai
    # do duoc tu kho bai that. Cac chi so ben duoi van in ra de tham khao.
    report.metrics["ty le cau dai"] = f"{long_ratio:.0%}"

    # Do dai doan
    para_lengths = [word_count(b.text) for b in prose_blocks if word_count(b.text) > 0]
    if len(para_lengths) >= 4:
        p_mean = sum(para_lengths) / len(para_lengths)
        p_burst = stdev(para_lengths) / p_mean if p_mean else 0
        report.metrics["do dai doan TB"] = f"{p_mean:.0f} tu"
        # Nhip DOAN cung da chuyen sang house_voice_check (chi so para_burstiness).
        # Nguong cu 0.30 dat theo ly thuyet, trong khi bai that co bien thien nho nhat
        # la 0.277 — tuc mot bai Muaban.net thuc su cung bi canh bao oan o day.

    # Do dai danh sach
    list_sizes = [len(b.items) for b in doc.blocks if b.kind == "list" and b.items]
    if len(list_sizes) >= 3:
        report.metrics["so danh sach"] = f"{len(list_sizes)} (kich thuoc: {list_sizes})"
        if len(set(list_sizes)) == 1:
            report.add("rhythm", WARN,
                       f"Tat ca {len(list_sizes)} danh sach deu co dung {list_sizes[0]} muc.",
                       guidance="Day la dau vet may ro nhat. Cho so luong muc khac nhau theo "
                                "noi dung that, dung ep du ba gach dau dong.")

    # Cach mo cau lap lai
    openers = Counter()
    for s in sentences:
        words = re.findall(r"[^\W_]+", s, re.UNICODE)[:2]
        if len(words) == 2:
            openers[normalize(" ".join(words))] += 1
    for opener, n in openers.most_common(3):
        if n > MAX_SAME_OPENER:
            report.add("rhythm", WARN,
                       f'{n} cau cung mo bang "{opener}...".',
                       guidance="Doi cach vao cau, hoac xoa han tu noi o dau cau.")

    # Mo doan bang tu noi
    connectors = {"bên cạnh đó", "ngoài ra", "hơn nữa", "đồng thời", "tuy nhiên",
                  "do đó", "vì vậy", "chính vì vậy", "mặt khác", "thêm vào đó"}
    starts = 0
    for b in prose_blocks:
        head = normalize(b.text)[:20]
        if any(head.startswith(c) for c in connectors):
            starts += 1
    if prose_blocks and starts / len(prose_blocks) > 0.35:
        report.add("rhythm", WARN,
                   f"{starts}/{len(prose_blocks)} doan mo dau bang tu noi.",
                   guidance="Chi rieng viec MO DAU DOAN bang tu noi moi dang giam, vi no lam "
                            "cac doan nghe nhu mot chuoi bo sung. Tu noi GIUA cac cau thi giu "
                            "nguyen — do la thu tao lien ket cho van tieng Viet. Cach sua dung "
                            "la mo doan bang chu the cua doan, con cum noi thi chuyen vao giua cau.")


def check_substance(doc, lex, report: Report) -> None:
    prose = "\n".join(b.text for b in doc.blocks if b.kind in ("paragraph", "list", "quote"))
    sentences = split_sentences(prose)
    words = word_count(prose)
    report.metrics["so tu (than bai)"] = words

    if not sentences or words < 50:
        report.add("substance", WARN, "Ban thao qua ngan de danh gia noi dung.")
        return

    # Mat do so lieu: van chung chung thi gan nhu khong co so.
    with_digits = sum(1 for s in sentences if re.search(r"\d", s))
    ratio = with_digits / len(sentences)
    report.metrics["cau co so lieu"] = f"{ratio:.0%}"
    if ratio < MIN_DIGIT_SENTENCE_RATIO:
        report.add("substance", WARN,
                   f"Chi {ratio:.0%} cau co con so cu the.",
                   guidance="Van nghe nhu may thuong la van khong biet gi cu the. Quay lai "
                            "evidence ledger va bo sung so lieu co nguon, dung viet chung chung hon.")

    # Lap truong
    stance_hits = sum(len(compile_pattern(m).findall(prose)) for m in lex.get("stance_markers", []))
    per_1000 = stance_hits / words * 1000
    report.metrics["dau hieu lap truong/1000 tu"] = f"{per_1000:.1f}"
    if per_1000 < MIN_STANCE_PER_1000:
        report.add("substance", WARN,
                   f"Bai gan nhu khong dua ra khuyen nghi ({per_1000:.1f}/1000 tu).",
                   guidance="Moi muc lon nen co it nhat mot cau noi ro nen lam gi, khong nen lam gi, "
                            "hoac can than cho nao.")

    # Thua nhan gioi han (tin hieu Trust)
    hedge_hits = sum(len(compile_pattern(m).findall(prose)) for m in lex.get("hedge_markers", []))
    if hedge_hits == 0:
        report.add("substance", WARN,
                   "Bai khong neu pham vi ap dung hay gioi han nao.",
                   guidance="Bat dong san la YMYL. Noi ro dieu kien ap dung, moc du lieu va cho "
                            "nao tuy dia phuong/ngan hang de nguoi doc khong ap dung sai.")

    # Bo ba tinh tu
    triads = TRIAD_RE.findall(prose)
    if len(triads) >= 3:
        report.add("substance", WARN,
                   f"{len(triads)} bo ba kieu 'A, B va C'.",
                   snippet=", ".join(" ".join(t) for t in triads[:3]),
                   guidance="Liet ke ba thanh phan lap lai la nhip may. Giu lai cai dung nhat.")


def check_formatting(doc, report: Report) -> None:
    raw = doc.raw
    words = max(word_count(doc.body_text), 1)

    emdash = raw.count("—")
    per_1000 = emdash / words * 1000
    if per_1000 > MAX_EMDASH_PER_1000:
        report.add("format", WARN,
                   f"{emdash} dau gach ngang dai ({per_1000:.1f}/1000 tu).",
                   guidance="Thay phan lon bang dau phay, dau hai cham hoac tach cau.")

    bold_words = sum(word_count(m.group(2)) for m in BOLD_RE.finditer(raw))
    bold_ratio = bold_words / words
    if bold_ratio > MAX_BOLD_RATIO:
        report.add("format", WARN,
                   f"{bold_ratio:.0%} so tu duoc in dam.",
                   guidance="In dam de nguoi doc luot bat y, khong phai de nhan manh moi thu. "
                            "Bôi dam ca cau thi khong con tac dung.")

    emojis = EMOJI_RE.findall(raw)
    if emojis:
        report.add("format", WARN, f"Co {len(emojis)} emoji trong bai.",
                   guidance="Khong dung emoji trong noi dung bat dong san.")

    # Lap lai tieu de o cau dau than bai
    h1 = next((h for h in doc.headings if h.level == 1), None)
    first_para = next((b for b in doc.blocks if b.kind == "paragraph"), None)
    if h1 and first_para:
        h1n, pn = normalize(h1.text), normalize(first_para.text)
        overlap = set(h1n.split()) & set(pn.split()[:20])
        if len(overlap) >= max(3, len(h1n.split()) * 0.7):
            report.add("format", WARN,
                       "Cau mo dau lap lai gan nguyen tieu de.",
                       line=first_para.line,
                       guidance="Sapo phai them thong tin, khong dien giai lai tieu de.")

    # Ket bai. KHONG kiem cac cum "hy vong...", "tren day la...", "qua bai viet..." nua:
    # chung da duoc go khoi `closing_boilerplate` va chuyen sang `house_voice_allowed`
    # theo quyet dinh cua chu du an (CLAUDE.md quy tac 15), vi do tren kho bai that thay
    # chinh toa soan dung chung o doan ket. Truoc day chung con bi hard-code o day, nam
    # NGOAI lexicon, nen viec go kia khong co tac dung: agent chay may kiem, thay canh
    # bao "Ket bai dong hop", roi xoa dung doan ket co mat do "ban" cao nhat bai — tuc
    # lam nguoc ca quy tac 15 va quy tac 17.
    #
    # Cai con dang kiem la doan ket khong noi voi ai: ket bai phai goi nguoi doc.
    # Doan ket la doan cuoi cua THAN BAI, khong phai doan cuoi cua file: sau than bai
    # con khoi minh bach ("Nguon va pham vi", "Can cu") va khoi do viet o the vo ngoi
    # la dung. Lay moc la tieu de dau tien cua khoi minh bach.
    stop = re.compile(r"(nguồn và (phạm vi|giới hạn)|căn cứ|minh bạch)", re.I)
    limit = next((h.line for h in doc.headings if stop.search(h.text)), None)
    body = [b for b in doc.blocks
            if b.kind in ("paragraph", "list") and (limit is None or b.line < limit)]
    tail_blocks = body[-2:]
    if tail_blocks and not any(re.search(r"\bbạn\b", b.text, re.I) for b in tail_blocks):
        report.add("format", WARN, "Doan ket khong goi nguoi doc.",
                   line=tail_blocks[-1].line, snippet=excerpt(tail_blocks[-1].text, 0),
                   guidance="Ket bai cua blog noi thang voi nguoi doc: 'Hy vong ... se giup "
                            "BAN chon duoc noi o phu hop'. Ket bang mot cau vo ngoi la dau "
                            "hieu bai dang tu noi ve chinh no.")


# --------------------------------------------------------------------------
# Kiem cau truc — thich ung tu Humanizer (blader/humanizer, MIT) va Wikipedia
# "Signs of AI writing". Day la nhung the loai lexicon khong bat duoc, vi chung
# trai dai qua nhieu cau hoac nam o hinh dang cua doan chu khong o tu ngu.
# --------------------------------------------------------------------------

NEGATION_RE = re.compile(r"(không phải|không có nghĩa|chẳng phải|đâu phải)", re.IGNORECASE)
AFFIRM_START_RE = re.compile(
    r"^(mà\s|nó\s+(là|chính là)|đó\s+(là|mới là)|đây\s+(là|mới là)|"
    r"điều\s+(đó|này)\s+có nghĩa|thực\s+(ra|chất)|thay vào đó)",
    re.IGNORECASE,
)
RAW_LIST_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
LABELED_ITEM_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+(\*\*|__)[^*_]{1,60}?[:：]\1"       # - **Nhan:** noi dung
    r"|^\s*(?:[-*+]|\d+[.)])\s+(\*\*|__)[^*_]{1,60}?\2\s*[:：]"   # - **Nhan**: noi dung
)
LABEL_TEXT_RE = re.compile(
    r"^\s*(?:[-*+]|\d+[.)])\s+(?:\*\*|__)([^*_]{1,60}?)[:：]?(?:\*\*|__)\s*[:：]?")
# Nhan cua khoi minh bach YMYL — bat buoc theo docs/04, khong phai trang tri.
YMYL_LABEL_RE = re.compile(
    r"(phạm vi|mốc dữ liệu|dữ liệu cập nhật|cập nhật tới|giới hạn|khuyến nghị|"
    r"tham vấn|căn cứ|nguồn|hiệu lực|áp dụng)", re.IGNORECASE)
ARROW_RE = re.compile(r"[→➜➤⇒»]")

MIN_CLOSER_OVERLAP = 0.5      # ty le tu trung voi doan truoc de coi la nhac lai
MAX_CLOSER_WORDS = 14         # doan mot cau dai hon thi thuong la noi dung that
MIN_LABELED_RUN = 3           # so muc lien tiep truoc khi coi la danh sach theo khuon


def check_split_contrast(doc, report: Report) -> None:
    """Tuong phan rong trai dai hai cau: 'Dieu nay khong co nghia la X. Do la Y.'"""
    hits = 0
    for b in doc.blocks:
        if b.kind != "paragraph":
            continue
        sents = split_sentences(b.text)
        for first, second in zip(sents, sents[1:]):
            if NEGATION_RE.search(first) and AFFIRM_START_RE.match(second.strip()):
                hits += 1
                if hits <= 3:
                    report.add("hollow_contrast", WARN,
                               "Tuong phan rong trai dai hai cau.",
                               line=doc.line_of(first[:40]) or b.line,
                               snippet=excerpt(f"{first} {second}", 0),
                               guidance="Nua phu dinh neu ra thu khong ai noi, de nua khang dinh "
                                        "nghe to hon. Noi thang dieu can noi.")
    if hits:
        report.metrics["tuong phan rong (2 cau)"] = hits


def check_repeated_closers(doc, report: Report) -> None:
    """Doan mot cau chi nhac lai doan truoc, hoac cung mot cau chot lap nhieu lan."""
    paras = [b for b in doc.blocks if b.kind == "paragraph"]
    seen = Counter()

    for idx, b in enumerate(paras):
        if len(split_sentences(b.text)) != 1 or word_count(b.text) > MAX_CLOSER_WORDS:
            continue
        norm = normalize(b.text)
        seen[norm] += 1
        if idx == 0:
            continue
        prev = set(normalize(paras[idx - 1].text).split())
        cur = set(norm.split())
        if cur and len(cur & prev) / len(cur) >= MIN_CLOSER_OVERLAP:
            report.add("closer", WARN,
                       "Doan mot cau chi nhac lai doan ngay truoc.",
                       line=b.line, snippet=excerpt(b.text, 0),
                       guidance="Mot cau ngan chi duoc giu khi no mang du kien moi. "
                                "Nhac lai thi cat.")

    for text, n in seen.items():
        if n >= 2:
            report.add("closer", WARN,
                       f"Cung mot cau chot lap lai {n} lan.",
                       snippet=text[:80],
                       guidance="Cau chot giong nhau sau nhieu muc la nhip may, khong phai nhan manh.")


def check_bold_labeled_list(doc, report: Report) -> None:
    """Moi gach dau dong deu mo bang mot nhan in dam va dau hai cham.

    Mien tru khoi minh bach YMYL (moc du lieu, pham vi, gioi han, tham van, can cu).
    Khoi do BAT BUOC phai co theo docs/04 va duoc evidence_check.py do; nhan in dam o
    day mang thong tin that, khong phai trang tri.
    """
    state = {"total": 0, "labeled": 0, "ymyl": 0, "line": 0}

    def flush() -> None:
        total, labeled, ymyl = state["total"], state["labeled"], state["ymyl"]
        if total < MIN_LABELED_RUN or labeled / total < 0.8:
            return
        if ymyl >= 2 or (total and ymyl / total >= 0.5):
            return
        report.add("format", WARN,
                   f"Danh sach {total} muc deu mo bang nhan in dam.",
                   line=state["line"],
                   guidance="Nhan in dam lap lai o moi muc la trang tri theo khuon. Bo in dam, "
                            "hoac viet thanh doan van khi nhan khong mang thong tin rieng. "
                            "Khoi minh bach YMYL duoc mien tru.")

    def reset() -> None:
        state.update(total=0, labeled=0, ymyl=0, line=0)

    for n, line in enumerate(doc.lines, start=1):
        if RAW_LIST_RE.match(line):
            if state["total"] == 0:
                state["line"] = n
            state["total"] += 1
            if LABELED_ITEM_RE.match(line):
                state["labeled"] += 1
                label = LABEL_TEXT_RE.match(line)
                if label and YMYL_LABEL_RE.search(label.group(1)):
                    state["ymyl"] += 1
        elif line.strip():
            flush()
            reset()
    flush()


def check_decoration(doc, report: Report) -> None:
    """Mui ten dung lam trang tri trong tieu de hoac dau muc."""
    arrows = ARROW_RE.findall(doc.body_text)
    if len(arrows) >= 3:
        report.add("format", WARN, f"Co {len(arrows)} mui ten trang tri trong bai.",
                   guidance="Mui ten thay cho dong tu la trang tri. Viet ro quan he bang chu.")


def check_claim_refs(doc, report: Report) -> None:
    refs = CLAIM_REF_RE.findall(doc.raw)
    report.metrics["tham chieu claim [Cxx]"] = len(set(refs))
    # Bai doc cho nguoi Viet doc thi khong chen ky hieu [Cxx] vao than bai (quy tac 16).
    # Truy xuat nguon nam o evidence-ledger.csv va khoi "Can cu" cuoi bai.
    if refs:
        report.add("claim_refs", WARN,
                   f"Than bai con {len(refs)} ky hieu [Cxx].",
                   guidance="Bo het ky hieu khoi cau van. Dan nguon theo cach bai that lam: "
                            "neu ten van ban ngay trong cau, vi du 'Theo diem c khoan 2 Dieu 10 "
                            "Nghi quyet 254/2025/QH15, ...'. Cot claim_id giu o ledger.")
        return
    if not refs:
        report.add("claim_refs", INFO,
                   "Ban thao khong danh dau [Cxx] nao.",
                   guidance="Danh dau claim trong ban thao giup evidence_check.py doi chieu chinh xac hon.")


def run(path: str, lexicon_path: str | None = None) -> Report:
    doc = parse_markdown(path)
    lex = load_lexicon(lexicon_path)
    report = Report(f"Giong van nguoi that — {path}")
    check_lexicon(doc, lex, report)
    check_rhythm(doc, report)
    check_substance(doc, lex, report)
    check_formatting(doc, report)
    check_split_contrast(doc, report)
    check_repeated_closers(doc, report)
    check_bold_labeled_list(doc, report)
    check_decoration(doc, report)
    check_claim_refs(doc, report)
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Kiem tra giong van nguoi that cho ban thao tieng Viet.")
    ap.add_argument("article", help="Duong dan file .md cua bai viet")
    ap.add_argument("--lexicon", default=None, help="Duong dan lexicon JSON tuy chon")
    ap.add_argument("--all", action="store_true", help="Hien ca dong INFO")
    args = ap.parse_args()

    report = run(args.article, args.lexicon)
    print_report(report, show_info=args.all)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
