"""Chay ca ba lop kiem tra va tong hop ket qua.

  python scripts/run_qa.py work/<slug>/article.md \
      --ledger work/<slug>/evidence-ledger.csv \
      --brief  work/<slug>/brief.yaml \
      --json   work/<slug>/qa-report.json

Khong truyen --ledger/--brief thi script tu tim hai file cung thu muc voi bai viet.
SEO fields (title, meta, slug) doc tu FRONT MATTER cua article.md; co --seo cho
truong hop hiem hoi ai do giu chung trong mot file YAML rieng.

Ma thoat: 0 = PASS (khong con BLOCK), 1 = con BLOCK, 2 = loi chay.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from qa_common import BLOCK, WARN, force_utf8_stdout, print_report

import evidence_check
import house_voice_check
import human_voice_check
import onpage_check

# SEO fields song trong front matter cua article.md, nen khong co seo-fields.yaml
# trong bo tu tim. Van doc duoc neu ai do truyen --seo cho mot file rieng.
DEFAULT_SIBLINGS = {
    "ledger": "evidence-ledger.csv",
    "brief": "brief.yaml",
}


def resolve_siblings(article: str, args) -> dict[str, str | None]:
    folder = os.path.dirname(os.path.abspath(article))
    out = {}
    for key, filename in DEFAULT_SIBLINGS.items():
        given = getattr(args, key)
        if given:
            out[key] = given
            continue
        candidate = os.path.join(folder, filename)
        out[key] = candidate if os.path.exists(candidate) else None
    out["seo"] = args.seo          # chi khi nguoi dung truyen --seo
    return out


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="QA tong hop cho bai viet content SEO.")
    ap.add_argument("article")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--brief", default=None)
    ap.add_argument("--seo", default=None)
    ap.add_argument("--lexicon", default=None)
    ap.add_argument("--json", dest="json_out", default=None, help="Ghi ket qua ra file JSON")
    ap.add_argument("--lenient", action="store_true",
                    help="Ha con so khong co cho dua xuong WARN (ra soat so bo)")
    ap.add_argument("--all", action="store_true", help="Hien ca dong INFO")
    args = ap.parse_args()

    if not os.path.exists(args.article):
        print(f"Khong tim thay bai viet: {args.article}", file=sys.stderr)
        return 2

    paths = resolve_siblings(args.article, args)
    reports = []

    print(f"Bai viet : {args.article}")
    for key, value in paths.items():
        if key == "seo" and not value:
            continue          # SEO fields nam trong front matter; khong co file rieng la binh thuong
        print(f"{key.ljust(9)}: {value or '(khong co)'}")

    try:
        reports.append(human_voice_check.run(args.article, args.lexicon))
        reports.append(house_voice_check.run(args.article))
        reports.append(onpage_check.run(args.article, paths["brief"], paths["seo"],
                                        args.lexicon, paths["ledger"]))
        if paths["ledger"]:
            reports.append(evidence_check.run(args.article, paths["ledger"], strict=not args.lenient))
        else:
            from qa_common import Report
            r = Report("Bang chung va chong bia dat")
            r.add("ledger", BLOCK, "Khong tim thay evidence-ledger.csv.",
                  guidance="Moi bai phai co evidence ledger truoc khi qua QA. "
                           "Copy tu templates/evidence-ledger.csv.")
            reports.append(r)
    except Exception as exc:                      # noqa: BLE001 - bao loi ro cho nguoi chay
        print(f"\nLoi khi chay QA: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    for report in reports:
        print_report(report, show_info=args.all)

    blocks = sum(r.count(BLOCK) for r in reports)
    warns = sum(r.count(WARN) for r in reports)
    status = "PASS" if blocks == 0 else "FAIL"

    print()
    print("=" * 64)
    print(f"KET QUA: {status}    BLOCK={blocks}   WARN={warns}")
    if blocks:
        print("Phai sua het BLOCK truoc khi ban giao.")
    if warns:
        print("Moi WARN phai duoc sua hoac giai trinh trong qa-report.md.")
    print("Luu y: may chi bat duoc loi co hoc. Do chinh xac, tinh huu ich va")
    print("viec co bia dat hay khong van phai do nguoi kiem. Xem docs/07-qa-va-ban-giao.md.")
    print("=" * 64)

    if args.json_out:
        payload = {
            "article": os.path.abspath(args.article),
            "inputs": paths,
            "status": status,
            "block_count": blocks,
            "warn_count": warns,
            "reports": [r.to_dict() for r in reports],
        }
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"Da ghi: {args.json_out}")

    return 1 if blocks else 0


if __name__ == "__main__":
    sys.exit(main())
