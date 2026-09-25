# -*- coding: utf-8 -*-
"""Do khoang cach giua bai dang viet va giong that cua blog Muaban.net.

Khac voi `human_voice_check.py` — bo do nay hoi "van co giong may khong" va tra loi
bang mot bo quy tac chung cho moi van ban tieng Viet. Bo do o day hoi mot cau hep hon:
"bai nay co giong nhu bai dang dang tren muaban.net/blog/nha-dat khong".

Moi nguong deu la p10-p90 do duoc tu kho bai that trong `reference/muaban-blog/`,
ghi san o `scripts/lexicon/house_voice.json`. Khong co con so nao do nguoi viet tu nghi.
Muon doi nguong thi them bai vao kho roi chay `house_voice_profile.py`, dung sua tay.

    python scripts/house_voice_check.py work/<slug>/article.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from house_voice_profile import bare_advice_sentences, measure  # noqa: E402
from qa_common import (  # noqa: E402
    BLOCK, WARN, INFO, Report, force_utf8_stdout, load_simple_yaml, normalize,
    parse_markdown, print_report,
)

PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "lexicon", "house_voice.json")

# Chu du an yeu cau: "Nhung loi khuyen, giai dap thac mac can phai bo sung danh tu
# vao" — tuc moi cau khuyen phai lay "ban" lam chu ngu.
#
# Dai p10-p90 khong doi duoc dieu nay: do tren 24 bai that, ty le tren trai tu 0% den
# 100%, san p10 chi 2,7%. Nen moc chan la QUYET DINH CUA CHU DU AN, ghi ro nhu quy tac
# 15 da ghi ba quyet dinh truoc. No ap cho bai cua du an, khong phai nhan xet rang
# bai that viet sai: 8 trong 24 bai that nam duoi moc nay.
ADVICE_SUBJECT_BLOCK = 0.50
# Muc canh bao thi KHONG dat cung: lay dung trung vi cua kho bai that, doc tu ho so
# nen no tu doi khi kho bai doi. "Duoi trung vi bai that" la mot cau noi duoc; con mot
# con so cung do nguoi viet nghi ra thi khong.
ADVICE_SUBJECT_WARN_FALLBACK = 0.60

# Chi so nao dang kiem, va noi gi khi lech. Chi cac chi so thuc su la "giong van";
# do dai bai va so muc thi tuy chu de nen khong kiem.
BANDS = {
    "sentence_words_mean": (
        "Do dai cau trung binh",
        "Blog Muaban.net viet cau dai va deu. Cau qua ngan lam bai nghe nhu ban tin, "
        "khong nhu bai huong dan."),
    "burstiness": (
        "Do gap ghenh cua nhip cau",
        "Nhip cua blog rat deu. Cao hon nguong nghia la bai dang giat cuc: cau rat ngan "
        "chen giua cau rat dai."),
    "short_sentence_ratio": (
        "Ty le cau ngan (<=10 tu)",
        "Day la chi so lech nhieu nhat khi bai bi che 'cung'. Blog gan nhu khong dung cau "
        "cut. Gop cau ngan lien tiep lai thay vi de chung dung roi."),
    "long_sentence_ratio": (
        "Ty le cau dai (>=35 tu)",
        "Blog dung nhieu cau dai co menh de phu. Thap qua nghia la bai dang bi chat vun."),
    "para_words_mean": (
        "Do dai doan trung binh",
        "Doan cua blog thuong 2 cau, 40-65 tu. Doan qua mong lam bai giong danh sach gach dau dong."),
    "para_burstiness": (
        "Bien thien do dai doan",
        "Cac doan khong nen dai bang nhau. Bai that co doan 2 cau xen doan 4 cau; "
        "deu tam tap la dau hieu viet theo khuon may."),
    "connector_per_1000": (
        "Mat do tu noi",
        "Day la chi so do LIEN KET GIUA CAC CAU. Thap hon dai nghia la cac cau dang dung "
        "roi nhau, moi cau mot y, khong co gi noi y truoc voi y sau — dung loi nguoi duyet "
        "goi la 'khong co su lien ket'. Sua bang cach them 'tuy nhien', 'vi vay', 'ngoai ra' "
        "GIUA cac cau, hoac gop hai cau thanh mot cau co menh de phu. Cao hon dai thi bai "
        "nghe nhu chuoi bo sung."),
    "ban_per_1000": (
        "Mat do xung ho 'ban'",
        "Blog goi nguoi doc la 'ban' deu tay nhung khong day dac."),
    "advice_per_1000": (
        "Mat do cau khuyen",
        "Giong Muaban.net la giong huong dan: 'ban nen', 'hay', 'luu y', 'truoc khi'. "
        "Thieu thi bai nghe nhu van ban hanh chinh."),
    "question_in_prose_ratio": (
        "Cau hoi trong than bai",
        "Blog hau nhu khong dat cau hoi tu tu trong van xuoi. Cau hoi chi nam o tieu de "
        "hoac o muc hoi dap."),
    "emdash_per_1000": (
        "Gach ngang dai",
        "Khong bai that nao dung gach ngang dai. Thay bang dau phay, dau hai cham, "
        "hoac tach cau."),
    # --- Bay chi so them vao sau khi chu du an bao giong van "khong giong tieng Viet",
    # --- "cau truc noi nguoc giong tieng nuoc ngoai" va "chua co danh xung nguoi doc".
    "advice_subject_ratio": (
        "Ty le cau khuyen co 'ban' lam chu ngu",
        "Bai that gan loi khuyen vao nguoi doc: 'Truoc khi dat coc, BAN NEN yeu cau...'. "
        "Thap nghia la bai dang ra lenh vo chu ngu: 'Nen hoi...', 'Hay kiem tra...'. "
        "Sua tung cau theo danh sach ben duoi, dung rac them chu 'ban' o cho khac."),
    "bare_advice_per_1000": (
        "Mat do menh lenh vo chu ngu",
        "Cao hon dai nghia la bai dung qua nhieu 'Nen...', 'Hay...', 'Dung...' khong co "
        "chu ngu. Day la chi so tach bai cua agent khoi bai that sach nhat."),
    "minh_per_1000": (
        "Mat do chu 'minh'",
        "Bai that gan nhu khong dung 'minh' de chi nguoi doc. Viet 'co so ban hoc', "
        "'lich hoc cua ban', khong phai 'co so minh hoc'."),
    "viec_per_1000": (
        "Mat do danh tu hoa voi 'viec'",
        "Cao hon dai la dau hieu cu phap dich: dong tu bi bien thanh danh tu. "
        "'Viec xac dinh gia dat can...' -> 'Ban xac dinh gia dat bang...'."),
    "abstract_start_ratio": (
        "Ty le cau mo bang chu ngu tru tuong",
        "Cau mo bang 'Viec...', 'Su...', 'Dieu...', 'Do la...' lam mat nguoi hanh dong. "
        "Dua nguoi doc hoac chu the that len lam chu ngu."),
    "front_clause_ratio": (
        "Ty le cau mo bang menh de phu dai",
        "Cao hon dai nghia la thong tin chinh bi day ve cuoi cau — dung kieu tieng Anh "
        "dich sang. Dua nong cot cau len truoc, menh de phu ve sau."),
    "dem_per_1000": (
        "Mat do 'dieu nay' / 'viec nay'",
        "Bai that gan nhu khong dung. Thay bang ten cua chinh su vat dang noi tới."),
}

# Chi canh bao khi THAP hon dai. Cao hon khong phai loi: goi nguoi doc nhieu hon bai
# that khong lam bai xau di, con dat nguong tran o day thi se phat dung cai dang sua.
LOW_ONLY = ("advice_subject_ratio",)

# Muc dan ve tin dang Muaban.net — 8/12 bai that co, va la quy uoc bat buoc cua du an
# (CLAUDE.md quy tac 15). Dat ap chot, ngay truoc 'Loi ket'.
BRAND_RE = re.compile(r"muaban\.net|mua bán", re.IGNORECASE)
CLOSING_HEADING = "lời kết"


def load_profile(path: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit("Chua co ho so giong nha: %s\n"
                         "Chay truoc: python scripts/house_voice_profile.py" % path)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def check_bands(values: dict, profile: dict, report: Report) -> int:
    """Doi chieu tung chi so voi dai p10-p90 cua kho bai that. Tra ve so chi so lech."""
    metrics = profile["metrics"]
    off = 0
    for key, (label, guidance) in BANDS.items():
        if key not in values or key not in metrics:
            continue
        v, m = values[key], metrics[key]
        lo, hi = m["p10"], m["p90"]
        report.metrics[label] = "%.3f (blog that %.3f-%.3f)" % (v, lo, hi)
        if v < lo:
            off += 1
            report.add("house_voice", WARN,
                       "%s = %.3f, thap hon blog that (%.3f-%.3f)." % (label, v, lo, hi),
                       guidance=guidance)
        elif v > hi and key not in LOW_ONLY:
            off += 1
            report.add("house_voice", WARN,
                       "%s = %.3f, cao hon blog that (%.3f-%.3f)." % (label, v, lo, hi),
                       guidance=guidance)
    return off


def check_budget(off: int, profile: dict, report: Report) -> None:
    """Bao nhieu chi so lech thi la nhieu? Lay chinh bai that lam moc.

    Dai p10-p90 theo dinh nghia da bo ra ngoai khoang 20% gia tri, nen bai that cung
    lech vai chi so. Khong co moc nay thi ba canh bao trong nhu mot bai hong.
    """
    budget = profile.get("deviation_budget") or {}
    ceiling = budget.get("max")
    if ceiling is None:
        return
    report.metrics["so chi so lech"] = "%d (bai that: trung vi %.0f, nhieu nhat %d)" % (
        off, budget.get("median", 0), ceiling)
    if off > ceiling:
        report.add("house_voice", WARN,
                   "Bai lech %d chi so van phong, nhieu hon moi bai that trong kho (toi da %d)."
                   % (off, ceiling),
                   guidance="Day la tin hieu tong: bai dang khong giong bat ky bai nao dang dang. "
                            "Sua cac canh bao chi so o tren truoc, dung sua tung cau roi rac.")


def listing_exempt(article_path: str) -> tuple[bool, str]:
    """Bai co duoc mien muc dan tin dang khong, doc tu brief.yaml canh bai.

    Blog Muaban.net khong chi co bat dong san: chuyen muc "Diem bao" co 140 bai, va mot
    bai ve diem bao dan gian thi khong the gan mot muc "Tim nha dat tren Muaban.net" ma
    khong guong. Nguoi duyet tu choi dung vi the: *"Bai viet nay khong thuoc bat dong
    san nen kho co the cho them heading IX. Tim nha dat va phong tro tren Muaban.net
    vao. Hay xoa di."*

    Mien tru phai KHAI BAO, khong mac dinh: brief ghi `muaban_listing_section: false`
    kem `listing_section_skip_reason`. Khong co brief thi khong duoc mien.
    """
    folder = os.path.dirname(os.path.abspath(article_path))
    path = os.path.join(folder, "brief.yaml")
    if not os.path.isfile(path):
        return False, ""
    brief = load_simple_yaml(path)
    raw = str(brief.get("muaban_listing_section", "")).strip().lower()
    if raw not in ("false", "no", "0", "khong"):
        return False, ""
    return True, str(brief.get("listing_section_skip_reason") or "").strip()


def check_brand_section(doc, report: Report, article_path: str = "") -> None:
    """Muc dan ve tin dang Muaban.net, dat ap chot."""
    h3 = [h for h in doc.headings if h.level == 3]
    if not h3:
        return
    hits = [h for h in h3 if BRAND_RE.search(h.text)]
    exempt, reason = listing_exempt(article_path) if article_path else (False, "")
    if not hits and exempt:
        if reason:
            report.add("house_voice", INFO,
                       "Bai duoc mien muc dan tin dang Muaban.net: " + reason[:150])
        else:
            report.add("house_voice", WARN,
                       "Brief tat muc dan tin dang nhung khong ghi ly do.",
                       guidance="Dien `listing_section_skip_reason` trong brief.yaml. Mien tru phai "
                                "giai trinh duoc voi nguoi duyet, khong duoc lang le.")
        return
    if not hits:
        report.add("house_voice", BLOCK, "Bai khong co muc dan ve tin dang Muaban.net.",
                   guidance="CLAUDE.md quy tac 15: moi bai phai co mot muc ap chot dang "
                            "'Tim <loai hinh> <dia ban> tren Muaban.net', dat ngay truoc 'Loi ket'. "
                            "8/12 bai that trong reference/muaban-blog/ deu co muc nay.")
        return
    tail = [h for h in h3 if CLOSING_HEADING not in normalize(h.text)]
    if tail and tail[-1] is not hits[-1]:
        report.add("house_voice", WARN, "Muc Muaban.net khong phai muc ap chot.",
                   line=hits[-1].line,
                   guidance="Dat no lam muc noi dung cuoi cung, ngay truoc 'Loi ket'.")


def check_advice_subject(doc, values: dict, profile: dict, report: Report) -> None:
    """Moi cau khuyen phai lay 'ban' lam chu ngu (quy tac 17).

    Khong dung dai p10-p90 o day, vi dai do qua rong de doi dieu nay — xem chu thich
    o `ADVICE_SUBJECT_BLOCK`. In ra tung cau vi pham kem so dong: cach sua la doi chu
    ngu cua chinh cau do, khong phai viet lai ca muc.
    """
    ratio = values.get("advice_subject_ratio")
    if ratio is None:
        return
    band = (profile.get("metrics") or {}).get("advice_subject_ratio") or {}
    warn_at = band.get("median", ADVICE_SUBJECT_WARN_FALLBACK)
    bare = bare_advice_sentences(doc)
    report.metrics["cau khuyen thieu danh xung"] = "%d cau" % len(bare)
    if ratio < ADVICE_SUBJECT_BLOCK:
        sev, muc = BLOCK, ADVICE_SUBJECT_BLOCK
    elif ratio < warn_at:
        sev, muc = WARN, warn_at
    else:
        return
    # Danh sach cau di kem chinh canh bao, khong tach thanh cac muc INFO rieng:
    # `print_report` an INFO mac dinh, nen tach ra thi nguoi doc bao cao khong thay
    # duoc cau nao phai sua — tuc mat dung phan huu dung nhat.
    lines = ["  dong %d: %s" % (line, sent[:120]) for line, sent in bare[:8]]
    if len(bare) > 8:
        lines.append("  ... con %d cau nua" % (len(bare) - 8))
    report.add("house_voice", sev,
               "Chi %.0f%% cau khuyen co 'ban' lam chu ngu, duoi muc %.0f%% cua du an "
               "(%d cau thieu danh xung)." % (ratio * 100, muc * 100, len(bare)),
               guidance="CLAUDE.md quy tac 17: moi cau khuyen va moi cau giai dap thac mac "
                        "phai goi nguoi doc. Doi 'Nen hoi chu tro...' thanh 'Ban nen hoi "
                        "chu tro...'. Giu nguyen noi dung, chi them chu ngu.\n"
                        + "\n".join(lines))
    for line, sent in bare:
        report.add("house_voice", INFO, "Cau khuyen khong co danh xung nguoi doc.",
                   line=line, snippet=sent[:150])


def check_sapo(doc, report: Report) -> None:
    """Sapo o H2, va la doan dan chu khong phai tieu de ky thuat."""
    h2 = [h for h in doc.headings if h.level == 2]
    if not h2:
        return
    first = h2[0]
    if normalize(first.text) in ("sapo", "mo bai", "mở bài", "tom tat", "tóm tắt"):
        report.add("house_voice", WARN,
                   'Tieu de H2 dang la "%s" — do la ten ky thuat, khong phai cau cho nguoi doc.'
                   % first.text, line=first.line,
                   guidance="Bai that dat ngay cau dan dau tien vao the H2. Viet mot cau "
                            "gioi thieu doc duoc, dung de nguyen chu 'Sapo'.")


def run(path: str, profile_path: str | None = None) -> Report:
    report = Report(name="house_voice")
    profile = load_profile(profile_path or PROFILE_PATH)
    report.metrics["kho bai mau"] = "%d bai" % profile.get("corpus_size", 0)

    doc = parse_markdown(path)
    values = measure(path)
    if not values:
        report.add("house_voice", INFO, "Bai qua ngan de do van phong.")
        return report

    off = check_bands(values, profile, report)
    check_budget(off, profile, report)
    check_advice_subject(doc, values, profile, report)
    check_brand_section(doc, report, path)
    check_sapo(doc, report)
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("article")
    ap.add_argument("--profile", default=None)
    args = ap.parse_args()
    report = run(args.article, args.profile)
    print_report(report)
    return 1 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
