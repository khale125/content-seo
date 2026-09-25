# -*- coding: utf-8 -*-
"""Tai bai that tu blog Muaban.net ve `reference/muaban-blog/` lam kho chuan giong van.

Kho nay la moc do cua `house_voice_profile.py`, nen no phai dung lai duoc: truoc day
bo rut bai chi nam trong thu muc tam cua mot phien lam viec, va khi can them bai thi
khong con gi de chay. File nay la ban duoc dua vao du an.

    python scripts/corpus_fetch.py https://muaban.net/blog/<slug>-<id>/
    python scripts/corpus_fetch.py --list urls.txt
    python scripts/corpus_fetch.py --category 3      # quet 3 trang dau category nha-dat

Hai dieu quan trong ve cach rut:

1. **Giu dung cap heading goc.** Blog dat sapo o `<h2>`, muc chinh o `<h3>`, muc con o
   `<h4>`. Khong duoc dung WebFetch hay bo chuyen doi nao tu "chuan hoa" cap heading —
   da mot lan bi lech cap va bao cao sai rang blog khac format sheet noi bo.
2. **Bo widget tin rao vat.** Trang bai co chen khoi tin dang (`lsst-*`), va neu khong bo
   thi ca khoi do bi tinh la mot cau dai 600 tu, lam moi chi so nhip cau sai het.

Con mot gioi han da biet: `<strong>` nam giua doan van bi bo cung the, nen chi so
`bold_ratio` do tu kho luon bang 0. Do la tao tac cua cong cu, khong phai su that ve
blog, nen `house_voice_check.py` khong kiem chi so do.
"""
from __future__ import annotations

import argparse
import html
import io
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa_common import force_utf8_stdout  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_DIR = os.path.join(ROOT, "reference", "muaban-blog")
CATEGORY = "https://muaban.net/blog/nha-dat/"
UA = "Mozilla/5.0 (compatible; content-seo/1.0; +muaban.net)"

BLOCK_RE = re.compile(r"(?is)<(h[1-6]|p|li|figcaption)\b[^>]*>(.*?)</\1>")
JUNK_CLASS = re.compile(r"lsst-|items-api|item-api|ez-toc|adsbygoogle|td-a-rec", re.I)
ARTICLE_RE = re.compile(r'href="(https://muaban\.net/blog/([a-z0-9\-]+-\d+))/?"')

# Bai ngoai chu de nha dat cung xuat hien tren trang category (khoi bai lien quan).
OFF_TOPIC = re.compile(
    r"viec-lam|phong-van|cma-la-gi|lai-xe|xe-may|o-to|xe-4-cho|ket-cau-xe|buom-bay|"
    r"ngay-tot|quang-cao|crack|sua-may-giat", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def balanced_cut(h: str, start: int) -> int:
    """Vi tri ket thuc cua the <div> mo tai `start`."""
    depth = 1
    for m in re.finditer(r"<(/?)div\b", h[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.end()
    return len(h)


def drop_junk(frag: str) -> str:
    while True:
        found = None
        for m in re.finditer(r'<div\b[^>]*class="([^"]*)"[^>]*>', frag):
            if JUNK_CLASS.search(m.group(1)):
                found = m
                break
        if not found:
            return frag
        frag = frag[:found.start()] + frag[balanced_cut(frag, found.end()):]


def container(h: str) -> str | None:
    m = re.search(r'<div class="td-post-content[^"]*"[^>]*>', h)
    if not m:
        return None
    return h[m.end():balanced_cut(h, m.end()) - len("</div>")]


def text_of(inner: str) -> str:
    t = re.sub(r"(?is)<br\s*/?>", " ", inner)
    t = re.sub(r"(?is)<[^>]+>", "", t)
    return re.sub(r"[ \s]+", " ", html.unescape(t)).strip()


def convert(frag: str) -> str:
    frag = re.sub(r"(?is)<(script|style|noscript|iframe|svg)\b.*?</\1>", " ", frag)
    frag = drop_junk(frag)
    out = []
    for m in BLOCK_RE.finditer(frag):
        tag, inner = m.group(1).lower(), m.group(2)
        txt = text_of(inner)
        if not txt or txt.lower() in ("mục lục", "nội dung chính"):
            continue
        if tag == "li":
            # Dong muc luc: mot the <a> tro toi fragment trong cung trang.
            if re.search(r'(?is)<a[^>]+href="#', inner) and len(re.findall(r"(?is)<a\b", inner)) == 1:
                continue
            out.append("- " + txt)
        elif tag == "figcaption":
            out.append("[CAPTION] " + txt)
        elif tag.startswith("h"):
            out.append("#" * int(tag[1]) + " " + txt)
        else:
            strong = bool(re.search(r"(?is)<(strong|b)\b", inner))
            out.append(("**%s**" % txt) if strong and len(txt) < 120 else txt)
    return "\n\n".join(out)


def slug_of(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def save(url: str, h: str) -> str | None:
    frag = container(h)
    if not frag:
        print("  !! khong thay than bai:", url)
        return None
    md = convert(frag)
    title = re.search(r"(?is)<title>(.*?)</title>", h)
    canon = re.search(r'(?is)<link rel="canonical" href="([^"]+)"', h)
    head = ""
    if title:
        head += "# " + html.unescape(title.group(1)).strip() + "\n\n"
    head += "<!-- " + (canon.group(1) if canon else url) + " -->\n\n"
    dst = os.path.join(CORPUS_DIR, slug_of(url) + ".md")
    io.open(dst, "w", encoding="utf-8", newline="\n").write(head + md + "\n")
    hs = re.findall(r"(?m)^(#+) ", md)
    print("  %-56s %5d tu  h2=%d h3=%d h4=%d" % (
        os.path.basename(dst), len(md.split()),
        hs.count("##"), hs.count("###"), hs.count("####")))
    return dst


def category_urls(pages: int) -> list[str]:
    found: list[str] = []
    for p in range(1, pages + 1):
        url = CATEGORY if p == 1 else "%spage/%d/" % (CATEGORY, p)
        for m in ARTICLE_RE.finditer(fetch(url)):
            u, slug = m.group(1) + "/", m.group(2)
            if OFF_TOPIC.search(slug) or u in found:
                continue
            found.append(u)
        time.sleep(1)
    return found


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--list", help="file chua mot URL moi dong")
    ap.add_argument("--category", type=int, metavar="N",
                    help="quet N trang dau cua category nha-dat, chi in URL con thieu")
    args = ap.parse_args()

    if args.category:
        have = {os.path.splitext(f)[0] for f in os.listdir(CORPUS_DIR) if f.endswith(".md")}
        for u in category_urls(args.category):
            print("%s %s" % ("co " if slug_of(u) in have else "MOI", u))
        return 0

    urls = list(args.urls)
    if args.list:
        urls += [ln.strip() for ln in io.open(args.list, encoding="utf-8") if ln.strip()]
    if not urls:
        ap.error("can it nhat mot URL, hoac --list, hoac --category")

    os.makedirs(CORPUS_DIR, exist_ok=True)
    ok = 0
    for u in urls:
        try:
            if save(u, fetch(u)):
                ok += 1
        except Exception as exc:                                  # noqa: BLE001
            print("  !! %s: %s" % (u, exc))
        time.sleep(1)
    print("da luu %d/%d bai vao %s" % (ok, len(urls), os.path.relpath(CORPUS_DIR, ROOT)))
    print("Chay tiep: python scripts/house_voice_profile.py   (do lai nguong)")
    return 0 if ok == len(urls) else 1


if __name__ == "__main__":
    raise SystemExit(main())
