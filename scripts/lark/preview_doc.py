"""Ban xem truoc CO ANH cua bai viet, dang tai lieu Lark, cho nguoi duyet doc.

Vi sao can: `push` dua `article.md` len Drive duoi dang tep Markdown. Anh trong bai
tro bang duong dan tuong doi `images/<ten>.jpg`, ma cac tep anh khong di theo, nen
tren Lark nguoi duyet thay bai khong co anh nao — trong khi cong duyet bai chinh la
cho duyet ca anh lan chu thich. Lo ra o bai 002, lan dau co anh that.

Cach lam: dung tai lieu Lark tu noi dung bai (bo dong anh, giu dong chu thich), roi
chen tung anh bang `docs +media-insert` NGAY TREN dong chu thich cua no. Chu thich
khong trung nhau nen dinh vi chac chan. Lan push sau GHI DE dung tai lieu cu
(`+update --command overwrite`) roi chen lai anh, nen link nguoi duyet da mo van
dung duoc.

Ban nay chi de DOC. Nguon su that van la `article.md` trong repo.
"""

from __future__ import annotations

import csv
import os
import re

import lark_cli as lc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

IMG_RE = re.compile(r"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$")
ITALIC_RE = re.compile(r"^\s*\*([^*].*[^*])\*\s*$")


def _split_front_matter(text: str) -> tuple[dict, str]:
    fm = {}
    if text.startswith("---"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            for line in parts[0].splitlines()[1:]:
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip('"').strip("'")
            return fm, parts[1]
    return fm, text


def _manifest(workdir: str) -> dict:
    path = os.path.join(workdir, "image-manifest.csv")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {(r.get("file_name") or "").strip(): r for r in csv.DictReader(fh)
                if (r.get("file_name") or "").strip()}


def _credit(row: dict) -> str:
    lic = (row.get("license") or "").strip()
    if not re.search(r"\bBY\b", lic.upper()):
        return ""
    return f"Ảnh: {(row.get('creator') or '').strip()}, {lic}"


def build(workdir: str) -> tuple[str, list[dict]]:
    """Tra ve (markdown khong co dong anh, danh sach anh can chen).

    Moi anh: file (duong dan tuong doi tu ROOT), caption (chuoi de dinh vi), alt.
    Anh khong co dong chu thich ngay duoi thi khong dinh vi duoc -> bo qua va bao.
    """
    with open(os.path.join(workdir, "article.md"), encoding="utf-8") as fh:
        fm, body = _split_front_matter(fh.read())
    rows = _manifest(workdir)

    head = []
    for key, label in (("title", "Title"), ("meta_description", "Meta description"),
                       ("slug", "Slug")):
        if fm.get(key):
            head.append(f"> **{label}:** {fm[key]}")
    out = (head + [""]) if head else []

    images, pending = [], None
    lines = body.split("\n")
    for line in lines:
        m = IMG_RE.match(line)
        if m:
            name = os.path.basename(m.group(2))
            pending = {"file": os.path.join(workdir, "images", name), "alt": m.group(1),
                       "name": name}
            continue
        if pending is not None:
            if not line.strip():
                continue
            cm = ITALIC_RE.match(line)
            if cm:
                cap = cm.group(1).strip()
                credit = _credit(rows.get(pending["name"], {}))
                out.append(f"*{cap}*" + (f" — {credit}" if credit else ""))
                pending["caption"] = cap
                images.append(pending)
                pending = None
                continue
            pending = None                 # anh khong co chu thich: khong dinh vi duoc
        out.append(line)
    return "\n".join(out).strip() + "\n", images


def _token_url(env: dict) -> tuple[str, str]:
    data = env.get("data") or env
    doc = data.get("document") if isinstance(data.get("document"), dict) else {}
    token = (data.get("document_id") or data.get("doc_token") or data.get("token")
             or doc.get("document_id") or "")
    url = data.get("url") or data.get("doc_url") or doc.get("url") or ""
    return token, url


def publish(cfg: dict, workdir: str, title: str, token: str | None,
            folder_token: str = "") -> tuple[str, str, list[str]]:
    """Tao hoac ghi de tai lieu xem truoc, roi chen anh. Tra ve (url, token, loi)."""
    content, images = build(workdir)
    errors: list[str] = []

    if token:
        lc.run(["docs", "+update", "--doc", token, "--command", "overwrite",
                "--doc-format", "markdown", "--content", "-"], cfg, timeout=300, stdin=content)
        url = ""
    else:
        args = ["docs", "+create", "--doc-format", "markdown", "--title", title,
                "--content", "-"]
        if folder_token:
            args += ["--parent-token", folder_token]
        env = lc.run(args, cfg, timeout=300, stdin=content)
        token, url = _token_url(env)
        if not token:
            raise lc.LarkError(f"Tao tai lieu xem truoc khong tra ve token: {str(env)[:300]}")

    # lark-cli tu choi duong dan tuyet doi ngoai thu muc dang dung, nen chay tu ROOT
    # va dua duong dan tuong doi.
    here = os.getcwd()
    os.chdir(ROOT)
    try:
        for img in images:
            rel = os.path.relpath(img["file"], ROOT).replace("\\", "/")
            if not os.path.isfile(rel):
                errors.append(f"thieu tep anh {rel}")
                continue
            try:
                lc.run(["docs", "+media-insert", "--doc", token, "--file", rel,
                        "--selection-with-ellipsis", img["caption"], "--before",
                        "--align", "center"], cfg, timeout=300)
            except lc.LarkError as exc:
                errors.append(f"{img['name']}: {str(exc)[:160]}")
    finally:
        os.chdir(here)

    if not url:
        base_url = cfg.get("base_url") or ""
        host = base_url.split("/base/")[0] if "/base/" in base_url else ""
        url = f"{host}/docx/{token}" if host else ""
    return url, token, errors
