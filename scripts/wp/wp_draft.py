"""Tao BAN NHAP tren WordPress cua blog Muaban.net tu goi ban giao trong `work/<slug>/`.

  python scripts/wp/wp_draft.py work/<slug> --dry-run     # xem se gui gi, khong cham WP
  python scripts/wp/wp_draft.py work/<slug>               # tao / cap nhat ban nhap
  python scripts/wp/wp_draft.py --check                   # thu dang nhap

Script nay **khong bao gio publish**. `status` gui len luon la `draft`, khong co co
nao doi duoc, va neu bai tren WordPress da o trang thai `publish` thi script dung lai
va bao nguoi that — quy tac 9 cua du an van con nguyen: dang bai la viec cua nguoi.

Ba chot phai qua truoc khi cham vao WordPress, chay theo dung thu tu nay:

  1. `run_qa.py` chay LAI tai cho va phai PASS. Khong tin `qa-report.json` cu, vi file
     do co the sinh ra tu mot ban thao khac.
  2. `lark_sync.py gate work/<slug>` phai tra ve exit 0 — tuc cong duyet bai da mo
     (quy tac 10). Loi nguoi dung trong hoi thoai khong thay duoc buoc nay.
  3. Moi dong trong `image-manifest.csv` phai co `rights_status = CLEARED`. Mot anh
     chua ro ban quyen ma da nam trong thu vien media la rui ro phap ly that.

Dang nhap bang **application password** cua WordPress, doc theo thu tu:

  1. bien moi truong `MBWP_USER` va `MBWP_APP_PASSWORD`
  2. file JSON tro boi `MBWP_CREDENTIALS`, mac dinh `%USERPROFILE%/.muaban-wp.json`:
     {"user": "<tai khoan wp>", "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"}

File thong tin dang nhap **nam ngoai thu muc du an** va khong bao gio duoc chep vao do.
Script khong in mat khau ra man hinh trong bat ky nhanh nao, ke ca khi bao loi.
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

from qa_common import parse_markdown                              # noqa: E402

SITE = "https://muaban.net/blog"
API = SITE + "/wp-json/wp/v2"
DEFAULT_CATEGORY = "nha-dat"          # id 16, 461 bai — chuyen muc bat dong san cua blog
STATE_FILE = ".wp.json"
CRED_DEFAULT = os.path.join(os.path.expanduser("~"), ".muaban-wp.json")


class WpError(RuntimeError):
    pass


# --------------------------------------------------------------- dang nhap

def _read_dotenv() -> dict:
    """Doc .env o goc du an. Khong ghi vao os.environ, de secret khong lan sang
    tien trinh con — `wp_draft` co goi `run_qa.py` va `lark_sync.py` bang subprocess.

    Ly do ham nay ton tai: du an ship `.env.example` va `install.sh` tao `.env`,
    nen nguoi cai dat dien mat khau vao do roi tuong la xong. Truoc day khong mot
    script nao doc file ay, va loi bao ra lai la "chua co thong tin dang nhap" —
    dung kieu bay ma nguoi moi mat ca buoi moi hieu.
    """
    path = os.path.join(ROOT, ".env")
    if not os.path.isfile(path):
        return {}
    out = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                if val:
                    out[key.strip()] = val
    except OSError:
        return {}
    return out


def load_credentials() -> tuple[str, str]:
    user = os.environ.get("MBWP_USER", "").strip()
    pw = os.environ.get("MBWP_APP_PASSWORD", "").strip()
    if user and pw:
        return user, pw

    dotenv = _read_dotenv()
    user = user or dotenv.get("MBWP_USER", "").strip()
    pw = pw or dotenv.get("MBWP_APP_PASSWORD", "").strip()
    if user and pw:
        return user, pw

    path = os.environ.get("MBWP_CREDENTIALS") or CRED_DEFAULT
    if not os.path.isfile(path):
        raise WpError(
            "Chua co thong tin dang nhap WordPress. Chon mot trong ba cach:\n"
            "  1. Dien MBWP_USER va MBWP_APP_PASSWORD vao file .env o goc du an\n"
            "  2. Dat hai bien moi truong do truc tiep\n"
            f"  3. Tao file {path} voi noi dung:\n"
            '     {"user": "<tai khoan wp>", "app_password": "<mat khau ung dung>"}')
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise WpError(f"Khong doc duoc {path}: {exc}") from exc
    user = str(data.get("user") or "").strip()
    pw = str(data.get("app_password") or "").strip()
    if not user or not pw:
        raise WpError(f"File {path} thieu `user` hoac `app_password`.")
    return user, pw


def auth_header(user: str, pw: str) -> str:
    # WordPress bo moi ky tu khong phai chu/so trong mat khau ung dung, nen khoang
    # trang trong ban sao chep tu man hinh admin khong anh huong gi.
    token = f"{user}:{re.sub(r'[^A-Za-z0-9]', '', pw)}".encode()
    return "Basic " + base64.b64encode(token).decode()


def call(method: str, url: str, auth: str, *, data: bytes | None = None,
         content_type: str | None = None, extra: dict | None = None) -> dict:
    req = urllib.request.Request(url, data=data, method=method)   # noqa: S310
    req.add_header("Authorization", auth)
    req.add_header("User-Agent", "muaban-content-seo/1.0")
    if content_type:
        req.add_header("Content-Type", content_type)
    for k, v in (extra or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:    # noqa: S310
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        if exc.code == 401:
            raise WpError("WordPress tu choi dang nhap (401). Kiem tra tai khoan va "
                          "mat khau ung dung; mat khau da bi thu hoi thi tao lai.") from exc
        if exc.code == 403:
            raise WpError(f"Tai khoan khong du quyen (403): {detail}") from exc
        raise WpError(f"WordPress tra ve {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise WpError(f"Khong ket noi duoc toi {SITE}: {exc.reason}") from exc
    return json.loads(body) if body.strip() else {}


def post_json(url: str, auth: str, payload: dict) -> dict:
    return call("POST", url, auth, data=json.dumps(payload).encode("utf-8"),
                content_type="application/json")


# ------------------------------------------------------------ ba chot truoc

def run_gate(folder: str) -> None:
    """Cong duyet bai tren Lark. Chi exit 0 moi duoc di tiep (quy tac 10)."""
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "lark", "lark_sync.py"), "gate", folder],
        cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise WpError("Cong duyet bai chua mo, nen chua duoc tao ban nhap.\n"
                      + (proc.stdout or "").strip()[:600])


def run_qa(folder: str) -> None:
    article = os.path.join(folder, "article.md")
    proc = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "run_qa.py"), article],
        cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout or "").strip().splitlines()[-12:])
        raise WpError("QA chua PASS nen chua duoc tao ban nhap (quy tac 8):\n" + tail)


def read_manifest(folder: str) -> list[dict]:
    path = os.path.join(folder, "image-manifest.csv")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("file_name") or "").strip()]
    bad = [r for r in rows
           if (r.get("rights_status") or "").strip().upper() != "CLEARED"]
    if bad:
        names = ", ".join((r.get("file_name") or "?") for r in bad[:5])
        raise WpError(f"{len(bad)} anh chua CLEARED ban quyen: {names}. "
                      "Xu ly ban quyen truoc, hoac bo anh do khoi bai.")
    return rows


# ------------------------------------------------------- markdown -> html

INLINE_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")


def inline(text: str, media: dict[str, dict]) -> str:
    out = html.escape(text, quote=False)
    # Doi lai dau ngoac cua markdown sau khi escape, de link va anh con nhan ra duoc.
    out = out.replace("&lt;", "<").replace("&gt;", ">") if "<" not in text else out

    def img_sub(m):
        alt, src = m.group(1), m.group(2)
        item = media.get(os.path.basename(src))
        url = item["source_url"] if item else src
        return f'<img src="{url}" alt="{html.escape(alt)}" />'

    out = INLINE_IMG.sub(img_sub, out)
    out = INLINE_LINK.sub(
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="nofollow noopener">'
                  f"{m.group(1)}</a>", out)
    out = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", out)
    return out


def md_to_html(body_lines: list[str], media: dict[str, dict]) -> str:
    """Doi ban thao sang HTML. Giu dung cap heading cua format he Blog (quy tac 14)."""
    out: list[str] = []
    buf: list[str] = []
    list_tag = ""
    table: list[list[str]] = []

    def flush_para():
        if buf:
            out.append("<p>" + inline(" ".join(buf).strip(), media) + "</p>")
            buf.clear()

    def flush_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = ""

    def flush_table():
        if not table:
            return
        head, *rest = table
        rest = [r for r in rest if not all(set(c.strip()) <= set("-: ") for c in r)]
        cells = "".join(f"<th>{inline(c.strip(), media)}</th>" for c in head)
        rows = "".join(
            "<tr>" + "".join(f"<td>{inline(c.strip(), media)}</td>" for c in r) + "</tr>"
            for r in rest)
        out.append(f"<figure class='wp-block-table'><table><thead><tr>{cells}</tr>"
                   f"</thead><tbody>{rows}</tbody></table></figure>")
        table.clear()

    skip_next_caption = False
    for raw in body_lines:
        line = raw.rstrip()
        stripped = line.strip()

        # Trong ban thao, chu thich anh viet thanh mot dong in nghieng ngay duoi anh
        # (do la cach `onpage_check` nhan ra caption). Tren WordPress thi chu thich da
        # nam trong <figcaption> lay tu manifest, nen bo dong nay di cho khoi lap.
        # Khuon cua du an co MOT DONG TRONG giua anh va chu thich (docs/14 muc A4), nen
        # giu co cho toi dong khong trong dau tien. Truoc day co bi xoa ngay o dong trong,
        # va moi chu thich hien HAI lan tren WordPress: trong <figcaption> va thanh mot
        # doan <p><em> ngay duoi — lo ra khi bai 002 lan dau co anh that.
        if skip_next_caption:
            if not stripped:
                continue
            skip_next_caption = False
            if re.fullmatch(r"\*[^*]+\*|_[^_]+_", stripped):
                continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_para(); flush_list()
            table.append(stripped.strip("|").split("|"))
            continue
        flush_table()

        if not stripped:
            flush_para(); flush_list()
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para(); flush_list()
            level = len(m.group(1))
            if level == 1:
                continue                  # H1 la title cua bai dang, khong lap trong than
            out.append(f"<h{level}>{inline(m.group(2), media)}</h{level}>")
            continue

        m = INLINE_IMG.fullmatch(stripped)
        if m:
            flush_para(); flush_list()
            alt, src = m.group(1), m.group(2)
            item = media.get(os.path.basename(src))
            url = item["source_url"] if item else src
            cap = (item or {}).get("caption", "")
            fig = f'<figure class="wp-block-image size-large">' \
                  f'<img src="{url}" alt="{html.escape(alt)}" />'
            credit = (item or {}).get("credit", "")
            if cap or credit:
                parts = [html.escape(cap)] if cap else []
                if credit:
                    parts.append(credit)
                fig += f"<figcaption>{'<br />'.join(parts)}</figcaption>"
            out.append(fig + "</figure>")
            skip_next_caption = True
            continue

        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_tag != "ul":
                flush_list(); out.append("<ul>"); list_tag = "ul"
            out.append(f"<li>{inline(m.group(1), media)}</li>")
            continue

        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_tag != "ol":
                flush_list(); out.append("<ol>"); list_tag = "ol"
            out.append(f"<li>{inline(m.group(1), media)}</li>")
            continue

        if stripped.startswith(">"):
            flush_para(); flush_list()
            out.append(f"<blockquote><p>{inline(stripped.lstrip('> '), media)}</p>"
                       f"</blockquote>")
            continue

        buf.append(stripped)

    flush_para(); flush_list(); flush_table()
    return "\n\n".join(out)


# ------------------------------------------------------------------ chay

CREDIT_SITES = {"commons.wikimedia.org": "Wikimedia Commons", "www.flickr.com": "Flickr",
                "flickr.com": "Flickr", "unsplash.com": "Unsplash", "www.pexels.com": "Pexels"}


def credit_parts(row: dict) -> tuple[str, str]:
    """Tra ve (html, van ban thuong) cua dong ghi cong, hoac ("", "") neu khong can.

    CC BY va CC BY-SA BAT BUOC ghi tac gia, nguon va giay phep o noi anh xuat hien.
    Truoc day figcaption chi mang chu thich, nen dung anh CC BY qua script nay la vi
    pham chinh giay phep cua anh — lo ra khi bai 002 lan dau lay anh tu Wikimedia.
    CC0, Public Domain va anh tu dung thi khong bat buoc, nen khong in.
    """
    lic = (row.get("license") or "").strip()
    if not re.search(r"\bBY\b", lic.upper()):
        return "", ""
    creator = (row.get("creator") or "").strip()
    src = (row.get("source_url") or "").strip()
    lurl = (row.get("license_url") or "").strip()
    host = urllib.parse.urlparse(src).netloc.lower()
    site = CREDIT_SITES.get(host, host)

    def link(href: str, text: str) -> str:
        if not href:
            return html.escape(text)
        return (f'<a href="{html.escape(href)}" target="_blank" '
                f'rel="nofollow noopener">{html.escape(text)}</a>')

    via = f" / {html.escape(site)}" if site else ""
    as_html = f"Ảnh: {link(src, creator)}{via}, {link(lurl, lic)}"
    as_text = f"Ảnh: {creator}{(' / ' + site) if site else ''}, {lic}"
    return as_html, as_text


def _file_sha(path: str) -> str:
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def upload_images(folder: str, rows: list[dict], auth: str,
                  dry: bool, uploaded: dict | None = None) -> dict[str, dict]:
    """Tai anh len thu vien Media. Anh da tai o lan truoc (ghi trong .wp.json) thi
    dung lai, khong tai lan nua — neu khong, moi lan cap nhat ban nhap lai sinh them
    mot bo anh trung trong thu vien Media."""
    media: dict[str, dict] = {}
    uploaded = uploaded or {}
    for row in rows:
        name = (row.get("file_name") or "").strip()
        path = os.path.join(folder, "images", name)
        if not os.path.isfile(path):
            raise WpError(f"Thieu file anh: {path}")
        digest = _file_sha(path)
        old = uploaded.get(name)
        # Chi dung lai khi TEP KHONG DOI. Cat lai anh ma giu nguyen ten tep thi phai tai
        # len lai, neu khong ban nhap van mang anh cu.
        if old and old.get("id") and old.get("sha") == digest and not dry:
            try:
                call("GET", f"{API}/media/{old['id']}?_fields=id", auth)
                media[name] = {"id": old["id"], "source_url": old["source_url"], "sha": digest,
                               "caption": (row.get("caption") or "").strip(),
                               "credit": credit_parts(row)[0],
                               "position": (row.get("position") or "").strip()}
                print(f"  [WP] dung lai anh {name} (media #{old['id']})")
                continue
            except WpError:
                pass                     # anh da bi xoa khoi thu vien: tai lai
        if dry:
            media[name] = {"id": 0, "source_url": f"(chua tai) {name}",
                           "caption": (row.get("caption") or "").strip(),
                           "credit": credit_parts(row)[0],
                           "position": (row.get("position") or "").strip()}
            continue
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        with open(path, "rb") as fh:
            blob = fh.read()
        item = call("POST", API + "/media", auth, data=blob, content_type=ctype,
                    extra={"Content-Disposition": f'attachment; filename="{name}"'})
        # alt va caption la bat buoc cua du an, nen ghi ngay sau khi tai len.
        credit_html, credit_text = credit_parts(row)
        cap_plain = (row.get("caption") or "").strip()
        post_json(f"{API}/media/{item['id']}", auth, {
            "alt_text": (row.get("alt_text") or "").strip(),
            # Thu vien Media cung phai mang ghi cong: anh co the duoc chen lai vao
            # bai khac tu thu vien, luc do khong con figcaption cua bai nay.
            "caption": f"{cap_plain} — {credit_text}" if credit_text else cap_plain,
        })
        media[name] = {"id": item["id"], "source_url": item["source_url"], "sha": digest,
                       "caption": cap_plain,
                       "credit": credit_html,
                       "position": (row.get("position") or "").strip()}
        print(f"  [WP] da tai anh {name} -> media #{item['id']}")
    return media


def category_id(slug: str, auth: str, dry: bool) -> int | None:
    if dry:
        return None
    data = call("GET", f"{API}/categories?slug={slug}&_fields=id,slug", auth)
    return data[0]["id"] if data else None


def report_to_base(folder: str, edit_url: str) -> None:
    """Ghi link ban nhap va trang thai len bang Dieu phoi.

    Khong chet ca luot chi vi buoc nay hong: ban nhap da nam tren WordPress roi, va
    mat dong trang thai tren Base khong lam mat cong viec do. Bao loi roi di tiep.

    Agent chi ghi `state`, `next_action` va `wp_draft_url` — khong bao gio cham vao
    cum `Ket qua duyet` + `Nguoi duyet` (quy tac 10).
    """
    try:
        sys.path.insert(0, os.path.join(SCRIPTS, "lark"))
        import lark_cli as lc
        import lark_sync as ls
        import schema as sch

        state = ls.load_state(folder)
        rid = (state.get("record_id") or "").strip()
        if not rid:
            print("  [WP] thu muc chua push len Lark nen khong ghi duoc trang thai")
            return
        cfg = lc.load_config()
        ls.update_record(cfg, "pipeline", rid, {
            "wp_draft_url": edit_url,
            "state": sch.STATE_LABELS["WP_DRAFTED"],
            "next_action": sch.NEXT_ACTION["WP_DRAFTED"],
            "updated_at": lc.now_vn(),   # now_vn song o lark_cli, khong phai lark_sync
        })
        print("  [WP] da ghi len Base: trang thai 'Da len nhap WordPress' + link ban nhap")
    except Exception as exc:                                   # noqa: BLE001
        print(f"  [WP] khong ghi duoc trang thai len Base: {exc}", file=sys.stderr)


def find_live_post(url: str, auth: str) -> dict | None:
    """Tim bai dang dang tren blog theo slug lay tu URL cu.

    Permalink cua blog la `/blog/<slug>-<post_id>/`, nen doan cuoi URL KHONG phai slug:
    slug that la phan da cat duoi `-<id>`. Lan dau ham nay tra nguyen `chuon-chuon-bay-
    vao-nha-219339` va khong tim thay gi, nen chot khong no va script tao mot ban nhap
    trung slug voi bai dang song.
    """
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    if not tail:
        return None
    candidates = [tail]
    stripped = re.sub(r"-\d+$", "", tail)
    if stripped and stripped != tail:
        candidates.insert(0, stripped)
    for slug in candidates:
        data = call("GET", f"{API}/posts?slug={slug}&_fields=id,link,title,status", auth)
        live = next((x for x in data if x.get("status") == "publish"), None)
        if live:
            return live
    return None


def guard_update(folder: str, auth: str, allow_new: bool) -> None:
    """Bai `url_decision: UPDATE` thi KHONG duoc tao mot ban nhap moi.

    Ly do: ban nhap moi la mot BAI KHAC tren WordPress. Publish nham no la co hai bai
    cung chu de tren cung site — dung dinh nghia noi dung trung lap, va URL cu dang co
    thu hang se bi chinh minh canh tranh. Bai UPDATE phai duoc dan vao chinh bai cu.

    Muon tao ban nhap rieng de nguoi duyet doc thu thi truyen --new-draft, va luc do
    nguoi that chiu trach nhiem khong publish no.
    """
    if allow_new:
        return
    brief_path = os.path.join(folder, "brief.yaml")
    if not os.path.isfile(brief_path):
        return
    sys.path.insert(0, SCRIPTS)
    from qa_common import load_simple_yaml
    brief = load_simple_yaml(brief_path)
    if str(brief.get("url_decision") or "").strip().upper() != "UPDATE":
        return
    urls = brief.get("existing_urls") or []
    if isinstance(urls, str):
        urls = [urls]
    for u in urls:
        u = str(u).strip()
        if not u.startswith("http"):
            continue
        live = find_live_post(u, auth)
        if live:
            raise WpError(
                f"Bai nay la UPDATE cho bai dang dang #{live['id']}: {u}\n"
                "  Script khong sua bai dang song, va cung khong tao ban nhap moi cho bai UPDATE —\n"
                "  mot ban nhap moi la mot BAI KHAC, publish nham la co hai bai cung chu de.\n"
                "  Cach di tiep, chon mot:\n"
                f"    1. Nguoi that mo {SITE}/wp-admin/post.php?post={live['id']}&action=edit\n"
                "       roi dan noi dung tu article.md vao chinh bai do.\n"
                "    2. Chay lai voi --new-draft neu that su muon mot ban nhap rieng de doc thu;\n"
                "       khi do TUYET DOI khong publish ban nhap do.")


def load_state(folder: str) -> dict:
    path = os.path.join(folder, STATE_FILE)
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}
    return {}


def save_state(folder: str, data: dict) -> None:
    with open(os.path.join(folder, STATE_FILE), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def run(folder: str, dry: bool, category: str, allow_new: bool = False) -> int:
    folder = folder.rstrip("\\/")
    article = os.path.join(folder, "article.md")
    if not os.path.isfile(article):
        raise WpError(f"Khong thay {article}")

    doc = parse_markdown(article)
    fm = doc.front_matter
    title = str(fm.get("title") or "").strip()
    slug = str(fm.get("slug") or "").strip()
    excerpt = str(fm.get("meta_description") or "").strip()
    if not title or not slug:
        raise WpError("Front matter thieu `title` hoac `slug`.")

    print(f"[WP] {os.path.basename(folder)}")
    if dry:
        print("     CHE DO THU — khong goi WordPress, khong tao gi")
    else:
        run_qa(folder)
        print("     QA: PASS")
        run_gate(folder)
        print("     cong duyet bai: DA MO")
    rows = read_manifest(folder)
    print(f"     anh: {len(rows)} dong manifest, tat ca CLEARED"
          if rows else "     anh: chua co anh nao")

    auth = ""
    if not dry:
        user, pw = load_credentials()
        auth = auth_header(user, pw)
        me = call("GET", f"{API}/users/me?_fields=id,name,slug", auth)
        print(f"     dang nhap: {me.get('name')} (id {me.get('id')})")

    # Chot UPDATE ton tai de khong TAO THEM mot bai moi. Cap nhat ban nhap da co trong
    # .wp.json thi khong tao bai nao, nen khong chan. Truoc day chot chay moi lan, nen
    # bai 002 — UPDATE cho bai dang song 219339, da co ban nhap #616855 — se bi chan
    # ngay luot cap nhat anh dau tien sau khi duyet.
    prior = load_state(folder)
    if not dry and not prior.get("post_id"):
        guard_update(folder, auth, allow_new)

    media = upload_images(folder, rows, auth, dry, prior.get("media") or {})
    body_start = next((i for i, l in enumerate(doc.lines)
                       if re.match(r"^#\s", l.strip())), 0)
    content = md_to_html(doc.lines[body_start:], media)

    payload = {
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "content": content,
        "status": "draft",            # co dinh. Khong co duong nao doi thanh publish.
    }
    hero = next((m for m in media.values() if m.get("position") == "hero"), None)
    if hero and hero.get("id"):
        payload["featured_media"] = hero["id"]
    cid = category_id(category, auth, dry)
    if cid:
        payload["categories"] = [cid]

    if dry:
        print(f"\n     title   : {title}")
        print(f"     slug    : {slug}")
        print(f"     excerpt : {excerpt[:80]}...")
        print(f"     status  : draft")
        print(f"     content : {len(content)} ky tu HTML, "
              f"{content.count('<h3')} muc H3, {content.count('<figure')} figure")
        print("\n     Chay lai khong co --dry-run de tao ban nhap that.")
        return 0

    state = load_state(folder)
    post_id = state.get("post_id")
    if post_id:
        current = call("GET", f"{API}/posts/{post_id}?context=edit&_fields=id,status",
                       auth)
        if current.get("status") == "publish":
            raise WpError(f"Bai #{post_id} da duoc dang that roi. Script nay khong sua "
                          "bai dang song — nguoi that quyet dinh sua hay khong.")
        item = post_json(f"{API}/posts/{post_id}", auth, payload)
        print(f"  [WP] da cap nhat ban nhap #{item['id']}")
    else:
        item = post_json(f"{API}/posts", auth, payload)
        print(f"  [WP] da tao ban nhap #{item['id']}")

    edit_url = f"{SITE}/wp-admin/post.php?post={item['id']}&action=edit"
    save_state(folder, {"post_id": item["id"], "slug": slug, "edit_url": edit_url,
                        "media": {k: {"id": v["id"], "source_url": v["source_url"],
                                      "sha": v.get("sha", "")}
                                  for k, v in media.items() if v.get("id")}})
    report_to_base(folder, edit_url)
    print(f"\n     Mo de duyet va dang: {edit_url}")
    print("     Script khong dang bai. Nhan Publish la viec cua nguoi that.")
    return 0


def check_login() -> int:
    user, pw = load_credentials()
    me = call("GET", f"{API}/users/me?_fields=id,name,slug", auth_header(user, pw))
    print(f"[WP] dang nhap duoc: {me.get('name')} (id {me.get('id')}, "
          f"slug {me.get('slug')})")
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                          # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(
        description="Tao ban nhap WordPress tu goi ban giao. Khong bao gio publish.")
    ap.add_argument("folder", nargs="?", help="work/<slug>")
    ap.add_argument("--dry-run", action="store_true",
                    help="chi in ra se gui gi, khong goi WordPress")
    ap.add_argument("--category", default=DEFAULT_CATEGORY)
    ap.add_argument("--check", action="store_true", help="thu dang nhap roi thoat")
    ap.add_argument("--new-draft", action="store_true",
                    help="cho phep tao ban nhap moi ke ca khi bai la UPDATE cua mot URL dang song")
    args = ap.parse_args()

    try:
        if args.check:
            return check_login()
        if not args.folder:
            ap.print_help()
            return 2
        return run(args.folder, args.dry_run, args.category, args.new_draft)
    except WpError as exc:
        print(f"[WP] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
