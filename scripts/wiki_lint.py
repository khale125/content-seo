"""Kiem suc khoe wiki tri thuc.

Wiki chi co gia tri khi no dung. Mot trang dan quy dinh da het hieu luc con nguy
hiem hon khong co trang nao, vi no tao cam giac da kiem chung.

Kiem:
  1. Front matter du truong, id duy nhat, id khop ten file va khop thu muc.
  2. Moi claim VERIFIED co nguon HTTPS, trich dan nguyen van, va ngay lay ve.
  3. Khong ngay nao o tuong lai.
  4. Lien ket cheo ([[id]], related, superseded_by) tro toi trang co that.
  5. Trang het hieu luc ma van con bai dang dung -> canh bao do.
  6. evidence-ledger.csv co wiki_ref tro toi trang khong ton tai hoac da het hieu luc.
  7. Trang cu, trang mo coi, claim GAP, log.md sai dinh dang.

Chay:
  python scripts/wiki_lint.py
  python scripts/wiki_lint.py --json wiki/lint-report.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

from qa_common import BLOCK, WARN, Report, force_utf8_stdout, print_report
import wiki_common as W


# --------------------------------------------------------------------------
# 1. Front matter
# --------------------------------------------------------------------------

def check_meta(pages: list, report: Report) -> dict:
    by_id: dict = {}
    today = dt.date.today()

    for page in pages:
        where = page.rel_path

        if page.parse_error:
            report.add("trang", BLOCK, f"{where}: {page.parse_error}",
                       guidance="Copy templates/wiki-page.md lam khung.")
            continue

        missing = [k for k in W.REQUIRED_META if not str(page.meta.get(k) or "").strip()]
        if missing:
            report.add("front-matter", BLOCK, f"{where}: thieu truong {', '.join(missing)}.",
                       guidance="Truong bat buoc: " + ", ".join(W.REQUIRED_META))
            continue

        pid = page.page_id
        if not W.ID_RE.match(pid):
            report.add("front-matter", BLOCK, f"{where}: id '{pid}' khong phai kebab khong dau.")
        stem = os.path.splitext(os.path.basename(page.path))[0]
        if pid != stem:
            report.add("front-matter", BLOCK,
                       f"{where}: id '{pid}' khong khop ten file '{stem}.md'.",
                       guidance="Doi ten file hoac doi id cho trung nhau.")
        if pid in by_id:
            report.add("front-matter", BLOCK,
                       f"{where}: id '{pid}' da dung o {by_id[pid].rel_path}.")
            continue
        by_id[pid] = page

        if page.page_type not in W.VALID_TYPES:
            report.add("front-matter", BLOCK,
                       f"{where}: type '{page.page_type}' khong hop le.",
                       guidance="Chon mot trong: " + ", ".join(W.VALID_TYPES))
        else:
            folder = os.path.basename(os.path.dirname(page.path))
            if folder != page.page_type:
                report.add("front-matter", BLOCK,
                           f"{where}: type '{page.page_type}' khong khop thu muc '{folder}'.")

        if page.status not in W.VALID_PAGE_STATUS:
            report.add("front-matter", BLOCK,
                       f"{where}: status '{page.status}' khong hop le.",
                       guidance="Chon mot trong: " + ", ".join(W.VALID_PAGE_STATUS))

        for key in W.DATE_META:
            raw = str(page.meta.get(key) or "").strip()
            if not raw:
                continue
            parsed = W.parse_date(raw)
            if parsed is None:
                report.add("ngay", WARN, f"{where}: '{key}' sai dinh dang YYYY-MM-DD ({raw}).")
            elif key != "review_after" and parsed > today:
                report.add("ngay", BLOCK, f"{where}: '{key}' o tuong lai ({raw}).",
                           guidance="Ngay cap nhat khong the o tuong lai.")

        if page.status == "het-hieu-luc" and not str(page.meta.get("superseded_by") or "").strip():
            report.add("hieu-luc", WARN,
                       f"{where}: het hieu luc nhung khong ghi 'superseded_by'.",
                       guidance="Ghi id cua van ban thay the de tra nguoc duoc.")

    return by_id


# --------------------------------------------------------------------------
# 2. Claim
# --------------------------------------------------------------------------

def check_claims(pages: list, report: Report) -> None:
    today = dt.date.today()
    seen_sources: dict = {}

    for page in pages:
        if page.parse_error or not page.page_id:
            continue
        where = page.rel_path

        if not page.claims and page.page_type != "tong-hop":
            report.add("claim", WARN, f"{where}: trang khong co claim nao.",
                       guidance="Trang khong mang bang chung thi khong giup duoc bai viet. "
                                "Them claim hoac xoa trang.")

        for claim in page.claims:
            head = claim.text[:60]
            status = claim.get("status").upper()
            src_type = claim.get("source_type").upper()

            if status not in W.VALID_CLAIM_STATUS:
                report.add("claim", BLOCK,
                           f"{where}: claim thieu truong 'status' hop le.", line=claim.line,
                           snippet=head,
                           guidance="Chon mot trong: " + ", ".join(W.VALID_CLAIM_STATUS))
                continue

            if src_type and src_type not in W.VALID_SOURCE_TYPES:
                report.add("claim", WARN, f"{where}: source_type '{src_type}' la.",
                           line=claim.line, snippet=head)

            if status == "VERIFIED":
                url = claim.get("source_url")
                quote = claim.get("supporting_quote")
                if not url.startswith("https://"):
                    report.add("claim", BLOCK,
                               f"{where}: claim VERIFIED khong co source_url HTTPS.",
                               line=claim.line, snippet=head,
                               guidance="Wiki khong phai nguon. Khong co URL goc thi ha "
                                        "xuong PARTIAL hoac GAP.")
                if len(quote) < W.MIN_QUOTE_CHARS:
                    report.add("claim", BLOCK,
                               f"{where}: claim VERIFIED thieu trich dan nguyen van "
                               f"(toi thieu {W.MIN_QUOTE_CHARS} ky tu).",
                               line=claim.line, snippet=head,
                               guidance="Chep nguyen van doan trong nguon chung minh claim nay.")
                if not claim.get("retrieved_date"):
                    report.add("claim", BLOCK,
                               f"{where}: claim VERIFIED thieu retrieved_date.",
                               line=claim.line, snippet=head)
            elif status == "GAP":
                report.add("claim", WARN, f"{where}: claim con GAP.",
                           line=claim.line, snippet=head,
                           guidance="No bang chung. Lay nguon, thu hep claim, hoac xoa.")

            for key in W.CLAIM_DATE_FIELDS:
                raw = claim.get(key)
                if not raw:
                    continue
                parsed = W.parse_date(raw)
                if parsed is None:
                    report.add("ngay", WARN, f"{where}: '{key}' sai dinh dang ({raw}).",
                               line=claim.line, snippet=head)
                elif parsed > today:
                    report.add("ngay", BLOCK, f"{where}: '{key}' o tuong lai ({raw}).",
                               line=claim.line, snippet=head)

            url = claim.get("source_url")
            published = claim.get("published_date")
            if url and published:
                prev = seen_sources.get(url)
                if prev and prev[0] != published:
                    report.add("mau-thuan", WARN,
                               f"{where}: cung nguon nhung published_date khac voi {prev[1]} "
                               f"({published} vs {prev[0]}).",
                               line=claim.line, snippet=url,
                               guidance="Mot nguon chi co mot ngay cong bo. Doi chieu lai.")
                else:
                    seen_sources[url] = (published, where)


# --------------------------------------------------------------------------
# 3. Lien ket cheo va trang mo coi
# --------------------------------------------------------------------------

def check_links(pages: list, by_id: dict, work_root: str, report: Report) -> None:
    slugs = W.work_slugs(work_root)
    incoming: dict = {pid: 0 for pid in by_id}

    for page in pages:
        if page.parse_error or not page.page_id:
            continue
        where = page.rel_path
        targets = list(page.links) + page.meta_list("related") + page.meta_list("supersedes")
        sup = str(page.meta.get("superseded_by") or "").strip()
        if sup:
            targets.append(sup)

        for target in targets:
            if target == page.page_id:
                continue
            if target not in by_id:
                report.add("lien-ket", BLOCK,
                           f"{where}: tro toi trang khong ton tai '{target}'.",
                           guidance="Tao trang do, hoac sua lai id.")
            else:
                incoming[target] = incoming.get(target, 0) + 1

        for slug in page.meta_list("used_in"):
            if slug not in slugs:
                report.add("used-in", WARN,
                           f"{where}: 'used_in' tro toi slug khong co trong work/ ('{slug}').",
                           guidance="Bai da doi ten hoac chua tao. Cap nhat lai.")

        used = page.meta_list("used_in")
        if page.status == "het-hieu-luc" and used:
            report.add("het-hieu-luc", BLOCK,
                       f"{where}: van ban het hieu luc nhung con {len(used)} bai dang dung "
                       f"({', '.join(used)}).",
                       guidance="Day vua la rui ro YMYL vua la co hoi UPDATE. Cap nhat bai "
                                "sang van ban thay the, roi xoa slug khoi 'used_in'.")

    for pid, page in by_id.items():
        if incoming.get(pid, 0) == 0 and not page.meta_list("used_in"):
            report.add("mo-coi", WARN,
                       f"{page.rel_path}: khong trang nao tro toi, cung khong bai nao dung.",
                       guidance="Noi vao trang lien quan, dung cho mot bai, hoac xoa.")


# --------------------------------------------------------------------------
# 4. Do tuoi
# --------------------------------------------------------------------------

def check_freshness(pages: list, report: Report) -> None:
    today = dt.date.today()
    for page in pages:
        if page.parse_error or not page.page_id:
            continue
        where = page.rel_path

        age = W.days_since(str(page.meta.get("updated") or ""), today)
        limit = W.stale_limit(page.page_type)
        if age is not None and age > limit:
            report.add("do-tuoi", WARN,
                       f"{where}: cap nhat cach day {age} ngay (nguong {limit}).",
                       guidance="Mo lai nguon, xac nhan con dung, roi cap nhat 'updated'.")

        review = W.parse_date(str(page.meta.get("review_after") or ""))
        if review is not None and review < today:
            report.add("do-tuoi", WARN,
                       f"{where}: da qua han ra soat ({review.isoformat()}).")


# --------------------------------------------------------------------------
# 5. Doi chieu voi evidence ledger
# --------------------------------------------------------------------------

def check_ledgers(by_id: dict, work_root: str, report: Report) -> int:
    refs = W.ledger_refs(work_root)
    for slug, claim_id, ref in refs:
        page_id = ref.split("#", 1)[0].strip()
        if page_id not in by_id:
            report.add("ledger", BLOCK,
                       f"work/{slug}: {claim_id} co wiki_ref '{page_id}' khong ton tai.",
                       guidance="Sua wiki_ref, hoac tao trang wiki tuong ung.")
            continue
        page = by_id[page_id]
        if page.status == "het-hieu-luc":
            report.add("ledger", BLOCK,
                       f"work/{slug}: {claim_id} dung trang '{page_id}' da HET HIEU LUC.",
                       guidance="Bai dang dan can cu khong con hieu luc. Doi sang van ban thay the.")
        elif page.status == "chua-ro":
            report.add("ledger", WARN,
                       f"work/{slug}: {claim_id} dung trang '{page_id}' co hieu luc chua ro.")
    return len(refs)


# --------------------------------------------------------------------------
# 6. log.md
# --------------------------------------------------------------------------

def check_log(wiki_root: str, report: Report) -> int:
    path = os.path.join(wiki_root, "log.md")
    if not os.path.exists(path):
        report.add("log", WARN, "Khong co wiki/log.md.",
                   guidance="Log la thu duy nhat cho biet wiki duoc bao tri hay bi bo hoang.")
        return 0
    with open(path, "r", encoding="utf-8-sig") as fh:
        lines = fh.read().splitlines()

    entries = 0
    in_fence = False
    for n, line in enumerate(lines, start=1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence or not line.startswith("- "):
            continue
        m = W.LOG_LINE_RE.match(line.strip())
        if not m:
            report.add("log", WARN, "Dong log sai dinh dang.", line=n,
                       snippet=line.strip()[:80],
                       guidance="Dinh dang: - YYYY-MM-DD · ACTION · <page-id> · mo ta")
            continue
        if m.group(2) not in W.VALID_LOG_ACTIONS:
            report.add("log", WARN, f"Hanh dong '{m.group(2)}' khong hop le.", line=n,
                       guidance="Chon mot trong: " + ", ".join(W.VALID_LOG_ACTIONS))
        entries += 1
    return entries


# --------------------------------------------------------------------------

def run(wiki_root: str, work_root: str) -> Report:
    report = Report(name=f"Wiki tri thuc — {wiki_root}")
    pages = W.load_pages(wiki_root)

    by_id = check_meta(pages, report)
    check_claims(pages, report)
    check_links(pages, by_id, work_root, report)
    check_freshness(pages, report)
    ref_count = check_ledgers(by_id, work_root, report)
    log_entries = check_log(wiki_root, report)

    usable = [p for p in pages if p.page_id and not p.parse_error]
    report.metrics["so trang"] = len(pages)
    report.metrics["trang doc duoc"] = len(usable)
    report.metrics["so claim"] = sum(len(p.claims) for p in usable)
    report.metrics["claim VERIFIED"] = sum(p.count_status("VERIFIED") for p in usable)
    report.metrics["claim GAP"] = sum(p.count_status("GAP") for p in usable)
    report.metrics["trang het hieu luc"] = sum(1 for p in usable if p.status == "het-hieu-luc")
    report.metrics["ledger tro toi wiki"] = ref_count
    report.metrics["dong log"] = log_entries
    return report


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Kiem suc khoe wiki tri thuc.")
    ap.add_argument("--wiki", default=None)
    ap.add_argument("--work", default=None)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    root = W.project_root()
    wiki_root = args.wiki or os.path.join(root, "wiki")
    work_root = args.work or os.path.join(root, "work")

    if not os.path.isdir(wiki_root):
        print(f"Khong tim thay thu muc wiki: {wiki_root}", file=sys.stderr)
        return 2

    try:
        report = run(wiki_root, work_root)
    except Exception as exc:                                  # noqa: BLE001
        print(f"Loi khi kiem wiki: {exc}", file=sys.stderr)
        return 2

    print_report(report, show_info=args.all)
    print()
    print(f"BLOCK: {report.count(BLOCK)}   WARN: {report.count(WARN)}")
    if report.blocked:
        print("Sua het BLOCK truoc khi dua wiki vao dung cho bai moi.")

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, ensure_ascii=False, indent=2)

    return 1 if report.blocked else 0


if __name__ == "__main__":
    sys.exit(main())
