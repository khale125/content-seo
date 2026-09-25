# -*- coding: utf-8 -*-
"""Do van phong cua cac bai that tren blog Muaban.net va ghi ra mot ho so so.

Vi sao ton tai: "giong nha" truoc day chi duoc mo ta bang loi trong tai lieu, nen moi
nguoi hieu mot kieu va may khong kiem duoc. Script nay doc kho bai that trong
`reference/muaban-blog/`, do muoi may chi so van phong, roi ghi dai gia tri quan sat
duoc ra `scripts/lexicon/house_voice.json`.

Nguong KHONG do nguoi viet nghi ra. Chung la p10-p90 cua chinh cac bai dang dang.
Muon doi nguong thi them bai vao kho (`corpus_fetch.py`) roi chay lai script nay,
dung sua tay file JSON.

    python scripts/house_voice_profile.py            # do lai, ghi de file JSON
    python scripts/house_voice_profile.py --show     # chi in bang, khong ghi

## Hai pham vi do, dung lan nhau se ra so sai

- **Chi so hinh dang** (do dai cau, do dai doan, nhip) do tren DOAN VAN xuoi. Danh sach
  gach dau dong bi loai, vi mot dong danh sach khong phai mot doan va se keo moi so ve 0.
- **Chi so tu ngu** (xung ho, cau khuyen, danh tu hoa, cu phap) do tren DOAN VAN CONG
  DANH SACH. Phan lon cau khuyen cua bai huong dan nam trong bullet; bo bullet thi
  `ban_per_1000` va `advice_per_1000` khong nhin thay chung, va do la loi da co that:
  mot bai gan nhu phi ngoi van dat band.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa_common import (  # noqa: E402
    force_utf8_stdout, normalize, parse_markdown, split_sentences, stdev, word_count,
)

CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "reference", "muaban-blog")
PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "lexicon", "house_voice.json")

# Tu noi hay dung o dau doan. Blog that dung rat nhieu, nen day la chi so DUONG,
# khong phai loi — xem docs/12-giong-nha-muaban.md.
CONNECTORS = ("bên cạnh đó", "ngoài ra", "hơn nữa", "đồng thời", "tuy nhiên", "do đó",
              "vì vậy", "chính vì vậy", "mặt khác", "thêm vào đó", "như vậy", "cụ thể",
              "theo đó", "trong khi đó", "nhờ đó", "vì thế")

# --- Cau khuyen: dem theo CAU, va phan biet ai la chu ngu ------------------------
#
# Ban cu dem chuoi con tren ca than bai va da dem sai theo bon cach: `"nên "` khop
# trong "trở nên" va "cho nên"; `"bạn nên"` bi dem hai lan vi no cung chua `"nên "`;
# `"trước khi"` khop moi menh de thoi gian; va `"bạn"` khong he la mot phan tu, nen
# mot bai hoan toan phi ngoi van dat band. Ba bo do duoi day thay cho no.

# Loi khuyen co NGUOI DOC lam chu ngu. Day la khuon cua bai that:
# "Truoc khi dat coc, ban nen yeu cau..." / "Ngoai tien thue, ban can tinh them..."
READER_ADVICE_RE = re.compile(
    r"\bbạn\s+(?:chỉ\s+|cũng\s+|vẫn\s+|nên\s+)?"
    r"(?:nên|cần|hãy|phải|đừng|nhớ|lưu ý|tránh|ưu tiên|có thể|đừng quên)\b")
IF_READER_RE = re.compile(r"\bnếu\s+(?:như\s+)?bạn\b")

# Loi khuyen VO CHU NGU: "Nen hoi...", "Hay kiem tra...", "Luu y...".
#
# Hai nhom vi tri, va chung KHONG giong nhau — day la cho da phai thu hep mot lan:
#
# - Dau cau: nhan ca "nen", "can", "phai". "Nen hoi chu tro..." la loi khuyen.
# - Sau dau phay: CHI nhan "hay", "dung", "nho", "luu y", "tranh", "uu tien",
#   "khong nen". Khong nhan "nen" va "can", vi trong tieng Viet ", nen ..." phan lon
#   la LIEN TU chi ket qua ("Muc phat coc tuy tung thoa thuan, nen voi giao dich gia
#   tri lon thi cong chung vien la noi dang hoi") chu khong phai loi khuyen. Ban dau
#   bo do bat ca hai, va no cham dung hai cau nhu vay trong fixture-dat-chuan.
#
# Bo sot mot vai cau kieu ", can kiem tra..." thi chi la khong duoc danh dau; bat oan
# thi lam nguoi viet mat tin vao danh sach may in ra, nen chon ben chinh xac.
BARE_ADVICE_RE = re.compile(
    r"(?:^\s*(?:nên|hãy|đừng|nhớ|lưu ý|tránh|ưu tiên|không nên|cần|phải)\b"
    r"|[,;:]\s+(?:hãy|đừng|nhớ|lưu ý|tránh|ưu tiên|không nên)\b)")

# Chu ngu la nguoi khac, khong phai nguoi doc.
OTHER_SUBJ_RE = re.compile(
    r"\b(mình|người thuê|người mua|người bán|người ở|sinh viên|chủ trọ|chủ nhà|"
    r"hai bên|bên thuê|bên cho thuê|bên mua|bên bán|người dân|chúng ta|chúng tôi)\b")

MINH_RE = re.compile(r"\bmình\b")

# --- Dau hieu cu phap dich ------------------------------------------------------
#
# Chu du an goi loi nay la "cau truc noi nguoc giong tieng nuoc ngoai". Truoc day
# khong mot chi so nao cua du an cham tới cu phap: ca 11 chi so cu chi do do dai va
# tan so tu. Nam chi so duoi day lap cho trong do.

VIEC_RE = re.compile(r"\bviệc\b")
SU_RE = re.compile(r"\bsự\b")
# Chu ngu tru tuong dau cau — "Viec xac dinh...", "Dieu nay cho thay...".
ABSTRACT_START_RE = re.compile(r"^\s*(việc|sự|điều|đây là|đó là|nó)\b", re.I)
DEM_RE = re.compile(r"\b(điều này|điều đó|điều quan trọng là|việc này|việc đó)\b")
# Bi dong hanh chinh khong co tac nhan. "duoc" thu huong ("duoc giam gia") la tieng
# Viet binh thuong va bai that dung nhieu, nen chi dem nhom dong tu hanh chinh.
PASSIVE_ADMIN_RE = re.compile(
    r"\b(?:được|bị)\s+(?:thực hiện|quy định|ghi nhận|coi là|xem là|gọi là|sử dụng|"
    r"áp dụng|xác định|công nhận|đăng ký|quy đổi|nhắc đến|phân loại|ban hành|niêm yết|"
    r"tính toán|đánh giá|kiểm tra|xem xét|thẩm định|phê duyệt|cấp phép)\b")

VOICE_METRICS = (
    "sentence_words_mean", "burstiness", "short_sentence_ratio", "long_sentence_ratio",
    "para_words_mean", "para_burstiness", "connector_per_1000", "ban_per_1000",
    "advice_per_1000", "question_in_prose_ratio", "emdash_per_1000",
    # Bay chi so duoi day them vao sau khi chu du an bao giong van "khong giong tieng
    # Viet" va "chua co danh xung cua nguoi doc". Xem docs/13-cu-phap-tieng-viet.md.
    "advice_subject_ratio", "bare_advice_per_1000", "minh_per_1000",
    "viec_per_1000", "abstract_start_ratio", "front_clause_ratio", "dem_per_1000",
)
# `bold_ratio` bi do nhung KHONG kiem: bo rut than bai xoa the <strong> nam trong doan
# van, nen so 0 do duoc la tao tac cua cong cu chu khong phai su that ve blog. Doi chieu
# HTML tho thi bai that co in dam trong van xuoi, chi la rat thua. `emdash_per_1000` thi
# giu lai vi dau gach ngang la ky tu van ban, khong bi bo rut lam mat — dem tren HTML tho
# cua ca kho cho ket qua dung bang 0.
#
# `passive_admin_per_1000` va `no_subject_ratio` cung do ma khong kiem, vi do xong thi
# thay chung KHONG phan biet duoc: bai that dung bi dong hanh chinh nhieu hon bai cua
# agent (cac bai phap ly len tới 4,5/1.000 tu), va "nó" lam chu ngu thi 11/12 bai that
# bang 0 y nhu bai agent. Giu lai de theo doi, nhung dat chung vao BANDS se chi sinh ra
# canh bao oan.

CAPTION_RE = re.compile(r"^\s*\[CAPTION\]", re.I)
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


# Dong "Xem them: <tieu de bai khac>" la lien ket dieu huong cua toa soan, khong phai
# van xuoi cua bai. Bai that dung no nhieu (1-5 dong moi bai trong kho), va tieu de bai
# dich thuong ket bang dau hoi — de no lot vao phep do thi chi so "cau hoi trong than
# bai" bi day len oan. Loai o CA kho lan bai dang viet, roi do lai toan kho.
SEE_ALSO_RE = re.compile(r"^\s*(\*\*)?\s*xem thêm\s*:?", re.I)
IMAGE_LINE_RE = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
ITALIC_LINE_RE = re.compile(r"^\s*(\*[^*\s].*[^*\s]\*|_[^_\s].*[^_\s]_)\s*$")


def is_figure_caption(doc, block) -> bool:
    """Khoi nay la dong chu thich `*...*` nam ngay duoi mot dong anh `![...](...)`.

    Kho bai that luu anh bang dong `[CAPTION] ...` va khong co dong anh nao, nen phep
    do tren kho da BO chu thich. Bai dang viet dung khuon Markdown, va khong bo dong
    chu thich thi bai minh bi do KEM chu thich con bai that thi khong — 6 dong chu
    thich ngan da keo do dai doan trung binh cua bai 002 xuong duoi dai bai that.

    Phai doc DONG GOC qua `doc.lines`: `parse_markdown` go dinh dang truoc khi tao
    khoi, nen `block.text` da mat dau `*`, con dong anh thi khong thanh khoi nao ca.
    Kho bai that khong co dong nao khop, nen nguong da do khong doi (153/153 chi so).
    """
    lines = getattr(doc, "lines", None)
    ln = getattr(block, "line", 0)
    if not lines or not 0 < ln <= len(lines):
        return False
    if not ITALIC_LINE_RE.match(lines[ln - 1]):
        return False
    i = ln - 2
    while i >= 0 and not lines[i].strip():
        i -= 1
    return i >= 0 and bool(IMAGE_LINE_RE.match(lines[i]))


def prose_blocks(doc):
    """Doan van xuoi that: bo caption anh, bo bang, bo danh sach.

    Dung cho cac chi so HINH DANG (do dai cau, do dai doan, nhip).
    """
    out = []
    for b in doc.blocks:
        if b.kind != "paragraph":
            continue
        if is_figure_caption(doc, b):
            continue
        if CAPTION_RE.match(b.text):
            continue
        if b.text.startswith("|") or b.text.startswith("<!--"):
            continue
        if SEE_ALSO_RE.match(b.text):
            continue
        out.append(b)
    return out


def lexical_blocks(doc):
    """Doan van CONG danh sach gach dau dong. Dung cho cac chi so TU NGU.

    Phan lon cau khuyen cua bai huong dan nam trong bullet, nen bo bullet la bo dung
    cho can do nhat.
    """
    out = list(prose_blocks(doc))
    for b in doc.blocks:
        if b.kind == "list" and not CAPTION_RE.match(b.text):
            out.append(b)
    return out


def classify_advice(sentences: list[str]) -> tuple[int, int, int]:
    """Dem cau khuyen theo chu ngu. Tra ve (nguoi doc, vo chu ngu, chu ngu khac).

    Mot cau chi duoc dem mot lan, va thu tu xet la A -> C -> B.
    """
    a = b = c = 0
    for s in sentences:
        n = normalize(s)
        reader = READER_ADVICE_RE.search(n) or (
            IF_READER_RE.search(n) and BARE_ADVICE_RE.search(n))
        if reader:
            a += 1
            continue
        bare = BARE_ADVICE_RE.search(n)
        if not bare:
            continue
        if OTHER_SUBJ_RE.search(n) or "bạn" in n:
            c += 1
        else:
            b += 1
    return a, b, c


def bare_advice_sentences(doc) -> list[tuple[int, str]]:
    """Cac cau khuyen khong co danh xung nguoi doc, kem so dong.

    `house_voice_check.py` in thang danh sach nay ra, vi cach sua la sua tung cau —
    them "ban" lam chu ngu — chu khong phai viet lai ca bai.
    """
    out = []
    for b in lexical_blocks(doc):
        for s in split_sentences(b.text):
            if word_count(s) < 2:
                continue
            n = normalize(s)
            if READER_ADVICE_RE.search(n) or (IF_READER_RE.search(n)
                                              and BARE_ADVICE_RE.search(n)):
                continue
            if not BARE_ADVICE_RE.search(n):
                continue
            if OTHER_SUBJ_RE.search(n) or "bạn" in n:
                continue
            out.append((b.line, s.strip()))
    return out


def measure(path: str) -> dict:
    doc = parse_markdown(path)
    paras = prose_blocks(doc)
    prose = "\n".join(b.text for b in paras)
    sents = [s for s in split_sentences(prose) if word_count(s) >= 2]
    if len(sents) < 10 or len(paras) < 4:
        return {}

    lens = [word_count(s) for s in sents]
    mean = sum(lens) / len(lens)

    para_words = [word_count(b.text) for b in paras]
    para_sents = [max(1, len([s for s in split_sentences(b.text) if word_count(s) >= 2]))
                  for b in paras]
    pw_mean = sum(para_words) / len(para_words)

    # Pham vi tu ngu: doan van cong danh sach.
    lex = lexical_blocks(doc)
    lex_text = "\n".join(b.text for b in lex)
    lex_norm = normalize(lex_text)
    lex_sents = [s for s in split_sentences(lex_text) if word_count(s) >= 2]
    lex_words = word_count(lex_text) or 1

    def per_1000(pattern: re.Pattern) -> float:
        return round(len(pattern.findall(lex_norm)) * 1000 / lex_words, 2)

    n_conn = sum(1 for b in paras
                 if any(normalize(b.text)[:22].startswith(c) for c in CONNECTORS))
    a, b_cnt, c_cnt = classify_advice(lex_sents)
    n_advice = a + b_cnt + c_cnt

    # Cau mo bang menh de phu dai: dau phay dau tien nam sau tu thu 8 tro len.
    front = 0
    for s in lex_sents:
        head, sep, _ = s.partition(",")
        if sep and word_count(head) >= 8:
            front += 1

    h3 = [h for h in doc.headings if h.level == 3]
    h4 = [h for h in doc.headings if h.level == 4]

    return {
        "sentence_words_mean": round(mean, 2),
        "burstiness": round(stdev(lens) / mean, 3) if mean else 0.0,
        "short_sentence_ratio": round(sum(1 for n in lens if n <= 10) / len(lens), 3),
        "long_sentence_ratio": round(sum(1 for n in lens if n >= 35) / len(lens), 3),
        "para_words_mean": round(pw_mean, 2),
        "para_sentences_mean": round(sum(para_sents) / len(para_sents), 2),
        "para_burstiness": round(stdev(para_words) / pw_mean, 3) if pw_mean else 0.0,
        "one_sentence_para_ratio": round(sum(1 for n in para_sents if n == 1) / len(para_sents), 3),
        "ban_per_1000": round(len(re.findall(r"\bbạn\b", lex_norm)) * 1000 / lex_words, 2),
        "connector_open_ratio": round(n_conn / len(paras), 3),
        "connector_per_1000": round(
            sum(len(re.findall(re.escape(c), lex_norm)) for c in CONNECTORS)
            * 1000 / lex_words, 2),
        "advice_per_1000": round(n_advice * 1000 / lex_words, 2),
        "advice_subject_ratio": round(a / (a + b_cnt), 3) if (a + b_cnt) else 0.0,
        "bare_advice_per_1000": round(b_cnt * 1000 / lex_words, 2),
        "minh_per_1000": per_1000(MINH_RE),
        "viec_per_1000": per_1000(VIEC_RE),
        "su_per_1000": per_1000(SU_RE),
        "abstract_start_ratio": round(
            sum(1 for s in lex_sents if ABSTRACT_START_RE.match(s)) / len(lex_sents), 3),
        "front_clause_ratio": round(front / len(lex_sents), 3),
        "dem_per_1000": per_1000(DEM_RE),
        "passive_admin_per_1000": per_1000(PASSIVE_ADMIN_RE),
        "question_in_prose_ratio": round(sum(1 for s in sents if s.rstrip().endswith("?")) / len(sents), 3),
        "digit_sentence_ratio": round(sum(1 for s in sents if re.search(r"\d", s)) / len(sents), 3),
        "bold_ratio": round(sum(word_count(m) for m in BOLD_RE.findall(prose)) / lex_words, 3),
        "emdash_per_1000": round(lex_text.count("—") * 1000 / lex_words, 2),
        "body_words": lex_words,
        "advice_sentences": n_advice,
        "h3_sections": len(h3),
        "h4_per_h3": round(len(h4) / len(h3), 2) if h3 else 0.0,
    }


def pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    vs = sorted(values)
    i = (len(vs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(vs) - 1)
    return round(vs[lo] + (vs[hi] - vs[lo]) * (i - lo), 3)


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=CORPUS_DIR)
    ap.add_argument("--out", default=PROFILE_PATH)
    ap.add_argument("--show", action="store_true", help="chi in, khong ghi file")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.corpus, "*.md")))
    rows = [(os.path.basename(f), m) for f in files if (m := measure(f))]
    if len(rows) < 5:
        print("Kho bai qua nho (%d bai do duoc). Can it nhat 5." % len(rows))
        return 2

    keys = list(rows[0][1].keys())
    profile = {
        "_note": "Sinh tu dong boi scripts/house_voice_profile.py. Dung sua tay. "
                 "Doi nguong bang cach them bai vao reference/muaban-blog/ roi chay lai.",
        "corpus_size": len(rows),
        "corpus": [r[0] for r in rows],
        "metrics": {},
    }
    print("Do %d bai trong %s\n" % (len(rows), args.corpus))
    print("%-26s %8s %8s %8s %8s" % ("chi so", "p10", "trung vi", "p90", "bien do"))
    for k in keys:
        vals = [r[1][k] for r in rows]
        profile["metrics"][k] = {
            "min": pct(vals, 0.0), "p10": pct(vals, 0.10), "median": pct(vals, 0.5),
            "p90": pct(vals, 0.90), "max": pct(vals, 1.0),
        }
        m = profile["metrics"][k]
        print("%-26s %8.3f %8.3f %8.3f   %.3f-%.3f" %
              (k, m["p10"], m["median"], m["p90"], m["min"], m["max"]))

    # Ngan sach lech: chinh bai that cung khong nam tron trong p10-p90 cua ca kho.
    # Dem xem moi bai that lech may chi so, roi lay do lam moc "binh thuong".
    # Khong co moc nay thi nguoi viet khong biet 3 canh bao la nhieu hay it.
    devs = []
    for _, row in rows:
        n = 0
        for k in VOICE_METRICS:
            m = profile["metrics"].get(k)
            if m and not (m["p10"] <= row[k] <= m["p90"]):
                n += 1
        devs.append(n)
    profile["deviation_budget"] = {
        "checked_metrics": list(VOICE_METRICS),
        "median": pct([float(d) for d in devs], 0.5),
        "p90": pct([float(d) for d in devs], 0.90),
        "max": max(devs),
        "per_article": devs,
    }
    print()
    print("Bai that lech trung vi %.0f chi so, nhieu nhat %d/%d."
          % (profile["deviation_budget"]["median"], max(devs), len(VOICE_METRICS)))

    if not args.show:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(profile, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("\nDa ghi %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
