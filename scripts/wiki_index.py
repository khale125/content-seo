"""Dung lai muc luc cua wiki tri thuc tu front matter cua tung trang.

  python scripts/wiki_index.py build    # ghi de wiki/index.md
  python scripts/wiki_index.py check    # exit 1 neu index.md lech so voi thuc te

Muc luc la thu nguoi doc mo dau tien, nen no phai luon dung. Dung sua index.md
bang tay: sua front matter cua trang roi chay 'build'.

Ban ghi ra hoan toan suy ra tu noi dung wiki, khong chua ngay chay lenh, nen
'check' on dinh qua cac ngay.
"""

from __future__ import annotations

import argparse
import os
import sys

from qa_common import force_utf8_stdout
import wiki_common as W

TYPE_LABELS = {
    "van-ban": "Văn bản pháp luật",
    "khai-niem": "Khái niệm",
    "dia-ban": "Địa bàn",
    "so-lieu": "Số liệu",
    "tong-hop": "Tổng hợp",
}

STATUS_LABELS = {
    "con-hieu-luc": "còn hiệu lực",
    "het-hieu-luc": "**hết hiệu lực**",
    "sua-doi": "đã sửa đổi",
    "chua-ro": "chưa rõ",
    "khong-ap-dung": "—",
}

HEADER = """# Mục lục wiki

> File này do `python scripts/wiki_index.py build` dựng lại từ front matter của từng trang.
> **Đừng sửa tay.** Sửa trang rồi chạy lại lệnh; `wiki_index.py check` sẽ báo khi mục lục lệch.
>
> Wiki **không phải nguồn**. Mỗi claim ở đây mang theo `source_url` và trích dẫn nguyên văn để
> bài viết trích dẫn nguồn gốc, không trích dẫn wiki. Xem `docs/11-wiki-tri-thuc.md`.
"""


def evidence_cell(page: W.Page) -> str:
    verified = page.count_status("VERIFIED")
    partial = page.count_status("PARTIAL")
    gap = page.count_status("GAP")
    parts = []
    if verified:
        parts.append(f"{verified} xác minh")
    if partial:
        parts.append(f"{partial} một phần")
    if gap:
        parts.append(f"**{gap} thiếu nguồn**")
    return " · ".join(parts) if parts else "—"


def render(pages: list) -> str:
    usable = [p for p in pages if p.page_id and not p.parse_error]
    out = [HEADER]

    total_claims = sum(len(p.claims) for p in usable)
    verified = sum(p.count_status("VERIFIED") for p in usable)
    gap = sum(p.count_status("GAP") for p in usable)
    updates = sorted(x for x in (p.meta.get("updated") for p in usable) if x)
    newest = updates[-1] if updates else "—"

    out.append(
        f"**{len(usable)} trang · {total_claims} claim · {verified} đã xác minh · "
        f"{gap} còn thiếu nguồn · trang mới nhất cập nhật {newest}**\n"
    )

    if not usable:
        out.append("Wiki chưa có trang nào. Xem `docs/11-wiki-tri-thuc.md` để biết cách thêm trang đầu tiên.\n")
        return "\n".join(out)

    for page_type in W.VALID_TYPES:
        group = [p for p in usable if p.page_type == page_type]
        if not group:
            continue
        group.sort(key=lambda p: p.page_id)
        out.append(f"## {TYPE_LABELS[page_type]}\n")
        out.append("| Trang | Tình trạng | Cập nhật | Bằng chứng | Dùng trong bài |")
        out.append("|---|---|---|---|---|")
        for p in group:
            used = ", ".join(p.meta_list("used_in")) or "—"
            status = STATUS_LABELS.get(p.status, p.status or "—")
            title = p.title or p.page_id
            out.append(
                f"| [{title}]({p.rel_path}) | {status} | {p.meta.get('updated') or '—'} "
                f"| {evidence_cell(p)} | {used} |"
            )
        out.append("")

    orphans = [p for p in pages if not p.page_id or p.parse_error]
    if orphans:
        out.append("## Trang chưa đọc được\n")
        out.append("`wiki_lint.py` sẽ nói rõ hỏng chỗ nào.\n")
        for p in orphans:
            out.append(f"- `{p.rel_path}` — {p.parse_error or 'thiếu trường id'}")
        out.append("")

    return "\n".join(out)


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Dung lai muc luc wiki tri thuc.")
    ap.add_argument("action", choices=["build", "check"])
    ap.add_argument("--wiki", default=None, help="Thu muc wiki (mac dinh: <project>/wiki)")
    args = ap.parse_args()

    wiki_root = args.wiki or os.path.join(W.project_root(), "wiki")
    if not os.path.isdir(wiki_root):
        print(f"Khong tim thay thu muc wiki: {wiki_root}", file=sys.stderr)
        return 2

    pages = W.load_pages(wiki_root)
    content = render(pages).rstrip() + "\n"
    index_path = os.path.join(wiki_root, "index.md")

    if args.action == "build":
        with open(index_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print(f"Da ghi {os.path.relpath(index_path, W.project_root())} "
              f"({len([p for p in pages if p.page_id])} trang).")
        return 0

    if not os.path.exists(index_path):
        print("Chua co wiki/index.md. Chay: python scripts/wiki_index.py build")
        return 1
    with open(index_path, "r", encoding="utf-8-sig") as fh:
        current = fh.read()
    if current.replace("\r\n", "\n").rstrip() == content.rstrip():
        print("Muc luc khop voi noi dung wiki.")
        return 0
    print("Muc luc da lech so voi cac trang wiki.")
    print("Chay: python scripts/wiki_index.py build")
    return 1


if __name__ == "__main__":
    sys.exit(main())
