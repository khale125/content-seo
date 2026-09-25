"""Dong bo hai chieu giua work/<slug>/ va Lark Base.

  push   work/<slug>     day artifact len, tinh lai trang thai
  pull   work/<slug>     doc nguoc trang thai duyet ve may
  gate   work/<slug>     cong duyet hien tai da mo chua (exit 0 = mo)
  status                 liet ke toan bo pipeline
  remove work/<slug>     go mot ban ghi khoi Lark

Mo hinh duyet — chi MOT cum ba o cho ca ba cong:

  Mot ban ghi tai mot thoi diem chi dung o dung mot cong. Cot "Trang thai" cho biet
  dang duyet cai gi. Nguoi duyet dien "Ket qua duyet" + "Nguoi duyet" (+ "Gop y" neu tu choi).

  Ten truong tren Base la nhan tieng Viet; code lam viec bang khoa noi bo ASCII.
  read_table() dich nhan -> khoa khi doc, schema.to_label() dich nguoc khi ghi.

  Phe duyet cu khong bao gio duoc tai su dung: moi khi noi dung duoc duyet thay doi
  (checksum cua outline + bai + evidence ledger), agent tang `version` va XOA TRANG
  cum duyet. Agent chi duoc phep xoa trang — khong bao gio duoc ghi APPROVED.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lark_cli as lc
import schema as S
from qa_common import make_slug

STATE_FILE = ".lark.json"
REVIEWED_FILES = ("outline.md", "article.md", "evidence-ledger.csv")


# --------------------------------------------------------------------------
# Artifact cuc bo
# --------------------------------------------------------------------------

def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_state(workdir: str) -> dict:
    path = os.path.join(workdir, STATE_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_state(workdir: str, state: dict) -> None:
    with open(os.path.join(workdir, STATE_FILE), "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def load_brief(workdir: str) -> dict:
    path = os.path.join(workdir, "brief.yaml")
    if not os.path.exists(path):
        return {}
    from qa_common import load_simple_yaml
    return load_simple_yaml(path)


def load_ledger(workdir: str) -> list[dict]:
    path = os.path.join(workdir, "evidence-ledger.csv")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def load_seo_fields(workdir: str) -> dict:
    """SEO fields nam trong front matter cua article.md, khong phai file rieng.

    Bai chua viet thi tra ve rong; cmd_push giu nguyen gia tri cu tren Base thay
    vi ghi de bang chuoi rong.
    """
    path = os.path.join(workdir, "article.md")
    if not os.path.exists(path):
        return {}
    from qa_common import parse_front_matter
    front, _ = parse_front_matter(_read(path))
    return {k: str(front.get(k) or "").strip()
            for k in ("title", "meta_description", "slug")}


def load_qa(workdir: str) -> dict:
    path = os.path.join(workdir, "qa-report.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def content_hash(workdir: str) -> str:
    """Checksum cua dung nhung gi nguoi duyet nhin. Doi checksum = phe duyet het hieu luc."""
    h = hashlib.sha256()
    for name in REVIEWED_FILES:
        path = os.path.join(workdir, name)
        h.update(name.encode())
        h.update(_read(path).encode() if os.path.exists(path) else b"")
    return h.hexdigest()[:16]


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(_PROJECT_ROOT, "templates")
WORK_DIR = os.path.join(_PROJECT_ROOT, "work")


def substantive(workdir: str, filename: str, min_chars: int) -> bool:
    """File da co noi dung that chua, hay moi chi la template chua dien.

    Kiem hai lop: du dai, VA khac voi template goc. Mot template copy nguyen
    xi dai hon nguong nhung khong phai noi dung da viet.
    """
    path = os.path.join(workdir, filename)
    if not os.path.exists(path):
        return False
    body = _read(path).strip()
    if len(body) < min_chars:
        return False
    tpl = os.path.join(TEMPLATES_DIR, filename)
    if os.path.exists(tpl) and body == _read(tpl).strip():
        return False
    return True


def _joinlist(value) -> str:
    if isinstance(value, list):
        return "\n".join(str(v) for v in value if str(v).strip())
    return str(value or "")


# --------------------------------------------------------------------------
# Brief -> tai lieu Markdown cho nguoi duyet
# --------------------------------------------------------------------------

BRIEF_LAYOUT = [
    ("Quyết định cần bạn duyệt", [
        ("Truy vấn chính", "primary_query"),
        ("Volume search (người dùng cung cấp)", "search_volume"),
        ("Quyết định URL", "url_decision"),
        ("Lý do quyết định", "url_decision_reason"),
        ("URL hiện có cùng intent", "existing_urls"),
    ]),
    ("Bài này phục vụ ai", [
        ("Người đọc", "reader"),
        ("Đọc xong họ quyết định được gì", "reader_task"),
        ("Mức độ hiểu biết", "reader_knowledge"),
        ("Intent", "intent"),
    ]),
    ("Vì sao viết bài này", [
        ("Vì sao là bây giờ", "why_now"),
        ("Dạng khoảng trống", "gap_type"),
        ("Bằng chứng khoảng trống", "gap_evidence"),
        ("Thứ bài này có mà top không có", "unique_angle"),
    ]),
    ("Phạm vi", [
        ("Địa bàn", "geography"),
        ("Loại hình", "property_type"),
        ("Mốc dữ liệu", "data_as_of"),
        ("Rủi ro YMYL", "ymyl_areas"),
        ("Cần chuyên gia rà soát", "expert_review_scope"),
    ]),
    ("Nội dung phải trả lời", [
        ("Câu hỏi", "questions_to_answer"),
        ("Thực thể phải nhắc tới", "entities"),
        ("Biến thể cùng bài", "same_page_variants"),
        ("Truy vấn tách thành bài khác", "separate_pages"),
    ]),
    ("Sau khi đọc", [
        ("CTA", "cta"),
        ("Liên kết nội bộ dự kiến", "internal_link_targets"),
        ("Nguồn ngoài dự kiến", "external_source_targets"),
        ("Rà soát lại sau", "review_after"),
    ]),
]


def render_brief(brief: dict, content_id: str, version: str, state: str) -> str:
    out = [f"# Brief — {brief.get('primary_query') or content_id}", ""]
    out.append(f"`{content_id}` · phiên bản `{version}` · trạng thái `{state}`")
    out.append("")
    out.append("> Duyệt trên Lark Base: điền `Kết quả duyệt` và `Người duyệt` ở bảng Điều phối.")
    out.append("> Từ chối thì thêm lý do vào ô `feedback`.")
    out.append("")
    for section, fields in BRIEF_LAYOUT:
        rows = [(label, _joinlist(brief.get(key)).strip()) for label, key in fields]
        rows = [(l, v) for l, v in rows if v]
        if not rows:
            continue
        out.append(f"## {section}")
        out.append("")
        for label, value in rows:
            if "\n" in value:
                out.append(f"**{label}**")
                out.append("")
                for line in value.splitlines():
                    out.append(f"- {line}")
                out.append("")
            else:
                out.append(f"- **{label}:** {value}")
        out.append("")
    missing = [label for _, fields in BRIEF_LAYOUT for label, key in fields
               if not _joinlist(brief.get(key)).strip()]
    if missing:
        out.append("## Trường còn trống trong brief")
        out.append("")
        out.append("Để trống là hợp lệ khi chưa tra được — nhưng đừng điền phỏng đoán.")
        out.append("")
        out.append(", ".join(missing))
        out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Lark helpers — Base
#
# Base dia chi hoa ban ghi bang `record_id` bat bien, khong phai so hang. Nguoi
# dung sap xep, loc, chen hay xoa thoai mai ma dong bo khong lung lay — day la
# khac biet lon nhat so voi ban Sheet truoc day.
#
# Phan con lai cua file van lam viec bang KHOA NOI BO va chuoi; hai ham
# `_flatten` / `_to_cell` la lop dem duy nhat biet den kieu du lieu cua Base.
# --------------------------------------------------------------------------

def _label_map(table: str) -> tuple[dict, dict]:
    cols = S.SPEC[table]["columns"]
    return ({k: lb for k, lb, _ in cols}, {lb: k for k, lb, _ in cols})


def _flatten(value) -> str:
    """CellValue cua Base -> chuoi phang."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(str(item.get("name") or item.get("text")
                                 or item.get("link") or item.get("id") or ""))
            else:
                parts.append(str(item))
        return ", ".join(p for p in parts if p).strip()
    if isinstance(value, dict):
        return str(value.get("name") or value.get("text")
                   or value.get("link") or value.get("id") or "").strip()
    return str(value)


def _to_cell(table: str, key: str, value):
    """Chuoi noi bo -> CellValue dung kieu. Select phai la mang ten option."""
    if key in S.SELECT_KEYS.get(table, set()):
        text = str(value or "").strip()
        return [text] if text else None
    if value is None:
        return ""
    return str(value)


def build_fields(table: str, payload: dict) -> dict:
    key_to_label, _ = _label_map(table)
    return {key_to_label[k]: _to_cell(table, k, v)
            for k, v in payload.items() if k in key_to_label}


def read_table(cfg: dict, table: str) -> list[dict]:
    """Tra ve [{'record_id':..., 'values': {khoa_noi_bo: chuoi}, 'fields': {...}}]."""
    key_to_label, _ = _label_map(table)
    out = []
    for rec in lc.list_records(cfg, table):
        fields = rec["fields"]
        out.append({
            "record_id": rec["record_id"],
            "values": {k: _flatten(fields.get(lb)) for k, lb in key_to_label.items()},
            "fields": fields,
        })
    return out


def create_record(cfg: dict, table: str, payload: dict) -> str:
    ids = lc.create_records(cfg, table, [build_fields(table, payload)])
    return ids[0] if ids else ""


def update_record(cfg: dict, table: str, record_id: str, payload: dict) -> None:
    lc.update_records(cfg, table, {record_id: build_fields(table, payload)})


def find_record(cfg: dict, content_id: str) -> dict | None:
    for rec in read_table(cfg, "pipeline"):
        if rec["values"].get("content_id", "").strip() == content_id:
            return rec
    return None


def next_content_id(cfg: dict) -> str:
    # Ma bai la so thu tu thuan: 001, 002, 003. Van chap nhan dang cu "SEO-001"
    # khi doc, de ban ghi tu truoc con dem duoc vao lan cap ma tiep theo.
    nums = [int(m.group(1)) for rec in read_table(cfg, "pipeline")
            if (m := re.match(r"(?:SEO-)?(\d+)$", rec["values"].get("content_id", "").strip()))]
    return f"{(max(nums) + 1) if nums else 1:03d}"


def audit(cfg: dict, content_id: str, version: str, event: str, actor: str,
          state: str, details: str) -> None:
    create_record(cfg, "audit", {
        "ts": lc.now_vn(), "content_id": content_id, "version": version,
        "event": S.to_label(S.EVENT_LABELS, event), "actor": actor,
        "state": S.to_label(S.STATE_LABELS, state), "details": details[:1500],
    })


def upload_markdown(cfg: dict, name: str, content: str, file_token: str | None,
                    folder_token: str = "") -> tuple[str, str]:
    """Tai lieu van nam tren Drive, KHONG phai attachment cua Base.

    Ly do giu nguyen: `markdown +overwrite --file-token` ghi de dung tep cu nen
    duong dan khong doi — link nguoi duyet da mo van dung duoc. Attachment cua
    Base sinh file_token moi moi lan ghi, lam chet link cu.

    lark-cli tu choi duong dan tuyet doi ngoai cwd, nen day noi dung qua stdin.
    """
    if not content.strip():
        return "", file_token or ""
    if file_token:
        args = ["markdown", "+overwrite", "--file-token", file_token, "--name", name, "--content", "-"]
    else:
        args = ["markdown", "+create", "--name", name, "--content", "-"]
        target = folder_token or cfg.get("doc_folder_token") or ""
        if target:
            args += ["--folder-token", target]
    env = lc.run(args, cfg, timeout=300, stdin=content)
    data = env.get("data") or {}
    token = data.get("file_token") or data.get("token") or file_token or ""
    url = data.get("url") or data.get("file_url") or ""
    if not url and token:
        base_url = cfg.get("base_url") or ""
        host = base_url.split("/base/")[0] if "/base/" in base_url else base_url.rstrip("/")
        url = f"{host}/file/{token}" if host else ""
    return url, token


def upload_file(cfg: dict, workdir: str, filename: str, name: str,
                token: str | None, folder_token: str = "") -> tuple[str, str]:
    path = os.path.join(workdir, filename)
    if not os.path.exists(path):
        return "", token or ""
    return upload_markdown(cfg, name, _read(path), token, folder_token)


# --------------------------------------------------------------------------
# Tai lieu nam o dau tren Drive
#
# Hai kieu xep, chon bang config.doc_layout:
#
#   "article" — moi bai mot thu muc chua ca bon tai lieu. O cong duyet nguoi
#               duyet doc brief va outline canh nhau, dung thu can doc cung luc.
#               Doi hoi scope `space:folder:create` vi phai tu tao thu muc.
#
#   "type"    — bon thu muc co san theo giai doan, khai trong config.doc_folders.
#               Khong tao thu muc nao nen khong can scope tren. Giai doan nao
#               chua khai thu muc thi tai lieu roi ve thu muc goc.
#
# Doi kieu xep = sua config roi push lai; place_docs se tu chuyen tep sang cho
# moi vi state["placed"] ghi nho tung tep dang nam o thu muc nao.
#
# `markdown +overwrite` khong doi thu muc cua tep da co, nen tep cu luon phai
# duoc MOVE mot lan rieng.
# --------------------------------------------------------------------------

DOC_KINDS = ("brief", "outline", "article")


def article_folder(cfg: dict, content_id: str, slug: str, state: dict) -> str:
    """Thu muc rieng cua bai; tao neu chua co. Chuoi rong = khong cau hinh duoc."""
    saved = (state.get("folder_token") or "").strip()
    if saved:
        return saved
    parent = (cfg.get("doc_folder_token") or "").strip()
    if not parent:
        return ""

    name = f"{content_id} - {slug}"
    # Tim theo ten truoc khi tao: push lai sau khi mat .lark.json khong duoc
    # sinh ra thu muc trung ten.
    for item in lc.folder_children(cfg, parent):
        if item.get("type") == "folder" and (item.get("name") or "").strip() == name:
            state["folder_token"] = item.get("token", "")
            return state["folder_token"]

    state["folder_token"] = lc.create_folder(cfg, parent, name)
    return state["folder_token"]


def doc_targets(cfg: dict, content_id: str, slug: str, state: dict) -> dict:
    """{loai tai lieu: folder_token}. Gia tri rong = de o thu muc goc."""
    root = (cfg.get("doc_folder_token") or "").strip()
    if (cfg.get("doc_layout") or "type").strip() == "article":
        folder = article_folder(cfg, content_id, slug, state)
        return {kind: folder for kind in DOC_KINDS}
    mapping = cfg.get("doc_folders") or {}
    return {kind: (mapping.get(kind) or root or "").strip() for kind in DOC_KINDS}


def place_docs(cfg: dict, targets: dict, tokens: dict, state: dict) -> int:
    """Chuyen tai lieu chua nam dung cho. Tra ve so tep da chuyen."""
    placed = dict(state.get("placed") or {})
    moved = 0
    for kind, token in tokens.items():
        folder = targets.get(kind) or ""
        if not token or not folder or placed.get(token) == folder:
            continue
        lc.move_file(cfg, token, folder)
        placed[token] = folder
        moved += 1
    state["placed"] = placed
    return moved


def replace_evidence(cfg: dict, content_id: str, new_rows: list[dict],
                     pipeline_record_id: str = "") -> None:
    """Xoa claim cu cua bai roi tao lai.

    Ban Sheet phai doc ca bang, loc, ghi de tu A2 va lam trang phan du. Base xoa
    dung nhung ban ghi can xoa, nen cac bai khac khong bi dung toi.
    """
    old = [r["record_id"] for r in read_table(cfg, "evidence")
           if r["values"].get("content_id", "").strip() == content_id]
    if old:
        lc.delete_records(cfg, "evidence", old)
    if not new_rows:
        return
    records = []
    for row in new_rows:
        fields = build_fields("evidence", row)
        if pipeline_record_id:
            fields[S.EVIDENCE_LINK_LABEL] = [{"id": pipeline_record_id}]
        records.append(fields)
    lc.create_records(cfg, "evidence", records)


# --------------------------------------------------------------------------
# Trang thai va cong duyet
# --------------------------------------------------------------------------

def gate_status(values: dict) -> dict:
    """Danh gia cum duyet doi voi trang thai hien tai."""
    state = S.to_canonical(S.STATE_LABELS, values.get("state", ""))
    review = S.to_canonical(S.REVIEW_LABELS, values.get("review", ""))
    reviewer = (values.get("reviewer") or "").strip()
    feedback = (values.get("feedback") or "").strip()

    if state not in S.GATE_STATES:
        return {"is_gate": False, "open": False, "state": state, "review": review,
                "reviewer": reviewer, "feedback": feedback, "missing": [],
                "rejected": review == "REJECTED"}

    missing = []
    if review != "APPROVED":
        missing.append("cột 'Kết quả duyệt' đang là 'Từ chối'" if review == "REJECTED"
                       else "cột 'Kết quả duyệt' chưa đặt 'Đồng ý'")
    if not reviewer:
        missing.append("cột 'Người duyệt' còn trống")

    return {"is_gate": True, "open": not missing, "state": state, "review": review,
            "reviewer": reviewer, "feedback": feedback, "missing": missing,
            "rejected": review == "REJECTED"}


def derive_state(values: dict, qa: dict, has_outline: bool, has_article: bool,
                 url_decision: str) -> str:
    """Trang thai moi = trang thai cu + cong da mo hay chua + artifact da co hay chua."""
    if url_decision.strip().upper() == "SKIP":
        return "SKIPPED"

    prev = S.to_canonical(S.STATE_LABELS, values.get("state", ""))
    gate = gate_status(values)

    # Dang o mot cong va cong chua mo -> dung nguyen cho.
    if gate["is_gate"] and not gate["open"]:
        return prev

    # Cong da mo -> di tiep.
    if gate["is_gate"] and gate["open"]:
        advanced = S.GATE_STATES[prev]
        if advanced == "DRAFTING" and has_article and qa.get("status") == "PASS":
            return "ARTICLE_PENDING"
        return advanced

    if prev == "DRAFTING":
        return "ARTICLE_PENDING" if (has_article and qa.get("status") == "PASS") else "DRAFTING"
    if prev in ("DONE", "SKIPPED", "WP_DRAFTED"):
        return prev            # ba trang thai cuoi: push sau khong keo nguoc ve cong

    # Dang nghien cuu: co outline roi thi len cong duyet outline.
    if prev == "RESEARCHING":
        return "OUTLINE_PENDING" if has_outline else "RESEARCHING"

    # Ban ghi moi. Quy trinh moi bat dau tu tu khoa nguoi dung dua, khong co cong
    # duyet chu de, nen chua co outline thi chi la dang lam.
    return "OUTLINE_PENDING" if has_outline else "RESEARCHING"


# --------------------------------------------------------------------------
# intake — Base -> may. Huong duy nhat di nguoc lai so voi push.
# --------------------------------------------------------------------------

TRUTHY = ("true", "1", "yes", "checked", "da duyet")


def _unique_slug(base_slug: str, record_id: str) -> str:
    """Tra ve slug chua bi thu muc khac chiem.

    Thu muc da ton tai VA tro dung ban ghi nay thi dung lai (intake chay lai khong
    tao ban sao). Tro ban ghi khac thi them hau to so.
    """
    slug, n = base_slug, 1
    while True:
        folder = os.path.join(WORK_DIR, slug)
        if not os.path.isdir(folder):
            return slug
        owner = (load_state(folder) or {}).get("record_id", "")
        if not owner or owner == record_id:
            return slug
        n += 1
        slug = f"{base_slug}-{n}"


def seed_workdir(slug: str, values: dict) -> str:
    """Tao work/<slug>/ voi dung nhung file thuoc buoc nghien cuu.

    Giu nguyen khuon cua `radar.py _seed_folder`: brief + ledger rong + serp-notes,
    va **khong** copy `outline.md`. Mot template chua dien van la file co noi dung,
    nen copy no vao se lam `substantive()` tuong outline da viet xong va day ban ghi
    vuot qua cong duyet outline.
    """
    folder = os.path.join(WORK_DIR, slug)
    os.makedirs(folder, exist_ok=True)

    brief_path = os.path.join(folder, "brief.yaml")
    if not os.path.exists(brief_path):
        body = _read(os.path.join(TEMPLATES_DIR, "brief.yaml"))
        today = lc.now_vn()[:10]
        fill = {
            "content_id": values.get("content_id", ""),
            "slug": slug,
            "created": today,
            "author_agent": "lark_sync intake",
            "primary_query": values.get("primary_query", ""),
            # Ghi DUNG con so nguoi dung go, ke ca khi la 0. Khong tu doi, khong tu doan.
            "search_volume": values.get("search_volume", ""),
            "data_as_of": today,
        }
        for key, val in fill.items():
            body = re.sub(r'(?m)^%s: "[^"]*"' % re.escape(key),
                          '%s: "%s"' % (key, val.replace('"', "'")), body, count=1)
        with open(brief_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)

    ledger = os.path.join(folder, "evidence-ledger.csv")
    if not os.path.exists(ledger):
        src = os.path.join(TEMPLATES_DIR, "evidence-ledger.csv")
        with io.open(src, encoding="utf-8-sig", newline="") as fh:
            header = next(csv.reader(fh))
        with io.open(ledger, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(header)

    for name in ("serp-notes.md", "competitors.json"):
        dst = os.path.join(folder, name)
        src = os.path.join(TEMPLATES_DIR, name)
        if not os.path.exists(dst) and os.path.exists(src):
            with open(dst, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(_read(src))
    return folder


def cmd_intake(cfg: dict, content_id: str | None) -> int:
    """Keo moi dong da tich 'Duyet tu khoa' xuong may va danh dau dang lam.

    Chot chong chay hai lan: chi nhat dong co o Trang thai TRONG. Ngay sau khi tao
    thu muc, lenh ghi `state = RESEARCHING` len Base, nen luot intake sau bo qua dong do.
    """
    picked = []
    for rec in read_table(cfg, "pipeline"):
        v = rec["values"]
        cid = (v.get("content_id") or "").strip()
        if content_id and cid != content_id:
            continue
        if (v.get("keyword_ok") or "").strip().lower() not in TRUTHY:
            continue
        if (v.get("state") or "").strip():
            continue
        if not (v.get("primary_query") or "").strip():
            continue
        picked.append(rec)

    if not picked:
        print("Khong co dong nao dang cho. Dong duoc nhat phai co: o 'Duyệt từ khoá' da tich, "
              "'Truy vấn chính' da dien, va 'Trạng thái' con trong.")
        return 0

    for rec in picked:
        v = rec["values"]
        cid = (v.get("content_id") or "").strip() or next_content_id(cfg)
        query = v.get("primary_query", "").strip()
        base_slug = make_slug(query)
        if not base_slug:
            print(f"  [BO QUA] {cid}: truy van khong sinh duoc slug ({query!r})")
            continue
        slug = _unique_slug(base_slug, rec["record_id"])
        folder = seed_workdir(slug, {**v, "content_id": cid})

        save_state(folder, {**load_state(folder), "record_id": rec["record_id"],
                            "content_id": cid, "intaken_at": lc.now_vn()})
        update_record(cfg, "pipeline", rec["record_id"], {
            "content_id": cid,
            "state": S.to_label(S.STATE_LABELS, "RESEARCHING"),
            "next_action": S.NEXT_ACTION.get("RESEARCHING", ""),
            "updated_at": lc.now_vn(),
        })
        audit(cfg, cid, "", "INTAKE", "content-seo agent", "RESEARCHING",
              f"tu khoa: {query} | volume: {v.get('search_volume') or '(trong)'} | slug: {slug}")

        vol = v.get("search_volume") or "(trong)"
        print(f"{cid}  {query}")
        print(f"  volume       : {vol}")
        print(f"  thu muc      : work/{slug}")
        print(f"  trang thai   : -> {S.to_label(S.STATE_LABELS, 'RESEARCHING')}")
        print(f"  viec ke tiep : chay skill seo-outline-bds tren work/{slug}")

    print()
    print(f"Base: {cfg.get('base_url') or cfg.get('app_token', '')}")
    return 0


# --------------------------------------------------------------------------
# push
# --------------------------------------------------------------------------

def cmd_push(workdir: str, cfg: dict, force_bump: bool) -> int:
    workdir = os.path.abspath(workdir)
    if not os.path.isdir(workdir):
        raise lc.LarkError(f"Khong tim thay thu muc: {workdir}")

    state = load_state(workdir)
    brief = load_brief(workdir)
    ledger = load_ledger(workdir)
    qa = load_qa(workdir)
    seo = load_seo_fields(workdir)

    content_id = state.get("content_id") or brief.get("content_id") or next_content_id(cfg)
    # Dinh vi theo record_id da luu TRUOC, roi moi quet theo content_id. Quet
    # theo content_id mot minh la mong manh: mot lan doc that bai se khong thay
    # ban ghi cu va push se tao ban ghi TRUNG.
    records = read_table(cfg, "pipeline")
    saved_id = (state.get("record_id") or "").strip()
    row = next((r for r in records if r["record_id"] == saved_id), None) if saved_id else None
    if row is None:
        row = next((r for r in records
                    if r["values"].get("content_id", "").strip() == content_id), None)
    record_id = row["record_id"] if row else ""
    existing = row["values"] if row else {}
    prev_state = existing.get("state", "")
    version = (existing.get("version") or "0.1.0").strip()

    # Ghi dinh danh xuong dia TRUOC khi cham vao Lark, de mot lan push that bai
    # giua chung khong de lai ban ghi mo coi o lan sau.
    state.pop("row", None)          # tan du cua ban Sheet, khong con nghia
    state.update({"content_id": content_id, "record_id": record_id})
    save_state(workdir, state)

    # Noi dung duoc duyet co doi khong? Doi -> phe duyet cu het hieu luc.
    new_hash = content_hash(workdir)
    content_changed = bool(row) and new_hash != state.get("content_hash")
    if not row:
        content_changed = False
    if content_changed or force_bump:
        parts = version.split(".")
        parts[-1] = str(int(parts[-1]) + 1) if parts[-1].isdigit() else "1"
        version = ".".join(parts)

    gate_before = gate_status(existing)
    has_outline = substantive(workdir, "outline.md", 200)
    has_article = substantive(workdir, "article.md", 400)
    url_decision = str(brief.get("url_decision") or "")

    new_state = derive_state(existing, qa, has_outline, has_article, url_decision)

    # Tai lieu cho nguoi duyet
    targets = doc_targets(cfg, content_id, os.path.basename(workdir), state)
    brief_url, brief_token = upload_markdown(
        cfg, f"{content_id} - brief.md",
        render_brief(brief, content_id, version, new_state),
        state.get("brief_token"), targets["brief"])
    outline_url, outline_token = upload_file(
        cfg, workdir, "outline.md", f"{content_id} - outline.md",
        state.get("outline_token"), targets["outline"])
    article_url, article_token = upload_file(
        cfg, workdir, "article.md", f"{content_id} - article.md",
        state.get("article_token"), targets["article"])
    # qa-report.md khong len Drive: bang Dieu phoi khong con cot cho no. Bao cao
    # QA nam trong goi ban giao o work/<slug>/, doc bang may cua nguoi duyet.
    place_docs(cfg, targets, {"brief": brief_token, "outline": outline_token,
                              "article": article_token}, state)

    counts = {"VERIFIED": 0, "PARTIAL": 0, "GAP": 0}
    for r in ledger:
        key = (r.get("status") or "").strip().upper()
        counts[key] = counts.get(key, 0) + 1
    evidence_cell = f"{counts['VERIFIED']} đã xác minh"
    if counts["PARTIAL"]:
        evidence_cell += f" · {counts['PARTIAL']} một phần"
    evidence_cell += f" · {counts['GAP']} thiếu nguồn"

    if qa:
        verdict = "ĐẠT" if qa.get("status") == "PASS" else "KHÔNG ĐẠT"
        qa_cell = (f"{verdict} · {qa.get('block_count', 0)} chặn"
                   f" · {qa.get('warn_count', 0)} cảnh báo")
    else:
        qa_cell = "chưa chạy"

    payload = {
        "content_id": content_id,
        "version": version,
        "state": S.to_label(S.STATE_LABELS, new_state),
        "next_action": S.NEXT_ACTION.get(new_state, "—"),
        "primary_query": brief.get("primary_query", ""),
        "search_volume": brief.get("search_volume", ""),
        "url_decision": S.to_label(S.URL_DECISION_LABELS, url_decision),
        "slug": seo.get("slug") or existing.get("slug", ""),
        "title": seo.get("title") or existing.get("title", ""),
        "meta_description": seo.get("meta_description") or existing.get("meta_description", ""),
        "evidence": evidence_cell if ledger else "chưa có ledger",
        "qa": qa_cell,
        "brief_url": brief_url or existing.get("brief_url", ""),
        "outline_url": outline_url or existing.get("outline_url", ""),
        "article_url": article_url or existing.get("article_url", ""),
        "updated_at": lc.now_vn(),
    }

    fields = dict(payload)

    # Phe duyet het hieu luc trong HAI truong hop, va ca hai deu phai xoa trang
    # cum duyet — neu khong, mot phe duyet cu se tu mo cong ke tiep:
    #   1. Noi dung duoc duyet thay doi (checksum doi).
    #   2. Phe duyet vua duoc TIEU THU de di qua mot cong; no khong con ap dung
    #      cho chang tiep theo.
    # Agent chi duoc phep xoa trang — khong bao gio duoc ghi APPROVED.
    consumed_gate = gate_before["is_gate"] and gate_before["open"] and new_state != prev_state
    cleared = False
    if (content_changed or force_bump or consumed_gate) and any(
            (existing.get(c) or "").strip() for c in S.REVIEW_BLOCK):
        for name in S.REVIEW_BLOCK:
            fields[name] = ""
        cleared = True

    # Mot lan ghi duy nhat: payload va viec xoa trang cum duyet phai nguyen tu,
    # neu khong se co khoanh khac ban ghi mang trang thai moi ma con phe duyet cu.
    if record_id:
        update_record(cfg, "pipeline", record_id, fields)
    else:
        record_id = create_record(cfg, "pipeline", fields)
        state["record_id"] = record_id
        save_state(workdir, state)

    if ledger:
        value_labels = {"claim_type": S.CLAIM_TYPE_LABELS, "risk": S.RISK_LABELS,
                        "status": S.CLAIM_STATUS_LABELS}
        replace_evidence(cfg, content_id, pipeline_record_id=record_id, new_rows=[
            {"content_id": content_id,
             **{h: S.to_label(value_labels[h], r.get(h, "")) if h in value_labels
                else r.get(h, "")
                for h in S.EVIDENCE_KEYS if h != "content_id"}}
            for r in ledger])
    else:
        replace_evidence(cfg, content_id, [], record_id)

    state.update({
        "content_version": version, "content_hash": new_hash,
        "brief_token": brief_token or state.get("brief_token", ""),
        "outline_token": outline_token or state.get("outline_token", ""),
        "article_token": article_token or state.get("article_token", ""),
        "last_push": payload["updated_at"],
    })
    save_state(workdir, state)

    details = f"evidence={evidence_cell}; qa={qa_cell}"
    if cleared:
        why = "da tieu thu de qua cong" if consumed_gate else "noi dung thay doi"
        details += f"; da xoa trang cum duyet ({why})"
    if consumed_gate:
        details += f"; phe duyet boi {gate_before['reviewer']} tai {prev_state}"
    audit(cfg, content_id, version, "PUSH", "content-seo agent", new_state, details)

    print(f"{content_id}  v{version}  ->  bản ghi {record_id}")
    print(f"  trạng thái   : {prev_state or '(mới)'} -> {payload['state']}")
    print(f"  việc kế tiếp : {payload['next_action']}")
    print(f"  bằng chứng   : {payload['evidence']}")
    print(f"  QA           : {qa_cell}")
    if cleared:
        why = ("đã dùng để qua cổng " + prev_state) if consumed_gate else "nội dung đã đổi"
        print(f"  cụm duyệt    : đã xóa trắng ({why})")
    elif gate_before["is_gate"] and gate_before["open"]:
        print(f"  cụm duyệt    : giữ nguyên phê duyệt của {gate_before['reviewer']}")
    for label, url in (("brief", brief_url), ("outline", outline_url),
                       ("article", article_url)):
        if url:
            print(f"  {label:<12} : {url}")
    print(f"\nBase: {cfg.get('base_url', '')}")
    return 0


# --------------------------------------------------------------------------
# pull / gate / status / remove
# --------------------------------------------------------------------------

def _require_row(workdir: str, cfg: dict) -> tuple[str, dict]:
    state = load_state(os.path.abspath(workdir))
    content_id = state.get("content_id")
    if not content_id:
        raise lc.LarkError("Thu muc nay chua duoc push len Lark lan nao.")
    row = find_record(cfg, content_id)
    if not row:
        raise lc.LarkError(f"Khong tim thay {content_id} tren Base.")
    return content_id, row


def cmd_pull(workdir: str, cfg: dict) -> int:
    content_id, row = _require_row(workdir, cfg)
    values = row["values"]
    g = gate_status(values)

    workdir = os.path.abspath(workdir)
    state = load_state(workdir)
    state.update({"remote_state": values.get("state", ""),
                  "remote_version": values.get("version", ""),
                  "gate": g, "pulled_at": lc.now_vn()})
    save_state(workdir, state)

    print(f"{content_id}  (bản ghi {row['record_id']})")
    print(f"  bản trên Lark : {values.get('version','')}")
    print(f"  trạng thái    : {values.get('state','')}")
    print(f"  việc kế tiếp  : {values.get('next_action','')}")
    print()
    if not g["is_gate"]:
        print(f"  Không đứng ở cổng duyệt nào ({values.get('state') or 'trống'}).")
    elif g["open"]:
        print(f"  CỔNG MỞ — {g['reviewer']} đã duyệt.")
    else:
        print("  CỔNG ĐÓNG — còn thiếu:")
        for m in g["missing"]:
            print(f"    - {m}")
    if g["feedback"]:
        print(f"  feedback: {g['feedback']}")
    print(f"\nĐã lưu vào {os.path.join(workdir, STATE_FILE)}")

    audit(cfg, content_id, values.get("version", ""), "PULL", "content-seo agent",
          values.get("state", ""),
          f"gate={'OPEN' if g['open'] else 'CLOSED'}"
          + (f"; reviewer={g['reviewer']}" if g["reviewer"] else ""))
    return 0


def cmd_gate(workdir: str, cfg: dict) -> int:
    try:
        content_id, row = _require_row(workdir, cfg)
    except lc.LarkError as exc:
        print(f"CỔNG ĐÓNG: {exc}")
        return 1

    values = row["values"]
    g = gate_status(values)
    state_name = values.get("state", "")
    doc = S.GATE_DOCUMENT.get(g["state"], "")

    if not g["is_gate"]:
        print(f"KHÔNG PHẢI CỔNG: {content_id} đang ở trạng thái {state_name or 'trống'}.")
        return 1
    if g["open"]:
        print(f"CỔNG MỞ [{g['state']}]: {g['reviewer']} đã duyệt {doc.lower()} "
              f"bản {values.get('version','')}.")
        return 0

    print(f"CỔNG ĐÓNG [{g['state']}]: {content_id} đang chờ bạn duyệt {doc.lower()}.")
    for m in g["missing"]:
        print(f"  - {m}")
    if g["rejected"] and g["feedback"]:
        print(f"  Lý do từ chối: {g['feedback']}")
    print(f"\nBase: {cfg.get('base_url', '')}")
    return 1


def cmd_status(cfg: dict) -> int:
    live = [r for r in read_table(cfg, "pipeline") if r["values"].get("content_id", "").strip()]
    if not live:
        print("Chưa có bài nào trên Lark.")
        return 0
    print(f"{'MÃ BÀI':<9} {'BẢN':<6} {'TRẠNG THÁI':<24} {'DUYỆT':<9} "
          f"{'MÁY KIỂM':<27} TRUY VẤN CHÍNH")
    print("-" * 118)
    for r in live:
        v = r["values"]
        print(f"{v.get('content_id',''):<9} {v.get('version',''):<6} {v.get('state',''):<24} "
              f"{(v.get('review','') or '—'):<9} {v.get('qa',''):<27} {v.get('primary_query','')}")
    print(f"\nBase: {cfg.get('base_url', '')}")
    return 0


def cmd_remove(workdir: str, cfg: dict, content_id: str | None, keep_audit: bool) -> int:
    if not content_id:
        content_id = load_state(os.path.abspath(workdir)).get("content_id") if workdir else None
    if not content_id:
        raise lc.LarkError("Can --content-id hoac mot thu muc da tung push.")

    row = find_record(cfg, content_id)
    if row:
        lc.delete_records(cfg, "pipeline", [row["record_id"]])
        print(f"Đã xóa bản ghi Điều phối của {content_id}")
    else:
        print(f"Không thấy {content_id} trong bảng Điều phối")

    replace_evidence(cfg, content_id, [])
    print("Đã xóa các claim tương ứng trong bảng Bằng chứng")

    if not keep_audit:
        doomed = [r["record_id"] for r in read_table(cfg, "audit")
                  if r["values"].get("content_id", "").strip() == content_id]
        if doomed:
            lc.delete_records(cfg, "audit", doomed)
        print(f"Đã xóa {len(doomed)} dòng Nhật ký của bản ghi này")

    if workdir:
        path = os.path.join(os.path.abspath(workdir), STATE_FILE)
        if os.path.exists(path):
            os.remove(path)
            print(f"Đã xóa {path}")
    return 0


def main() -> int:
    lc.force_utf8()
    ap = argparse.ArgumentParser(description="Dong bo content-seo voi Lark Base.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("push", help="Day artifact len Lark")
    p.add_argument("workdir")
    p.add_argument("--bump", action="store_true",
                   help="Tang version va xoa trang cum duyet ngay ca khi noi dung khong doi")

    p = sub.add_parser("pull", help="Doc nguoc trang thai duyet")
    p.add_argument("workdir")

    p = sub.add_parser("gate", help="Cong duyet hien tai da mo chua (exit 0 = mo)")
    p.add_argument("workdir")

    p = sub.add_parser("remove", help="Go mot ban ghi khoi Lark")
    p.add_argument("workdir", nargs="?", default=None)
    p.add_argument("--content-id", default=None)
    p.add_argument("--keep-audit", action="store_true")

    p = sub.add_parser("intake", help="Keo dong da tich 'Duyet tu khoa' tu Base xuong may")
    p.add_argument("--content-id", default=None, help="Chi nhat mot ma bai")

    sub.add_parser("status", help="Liet ke toan bo pipeline")

    args = ap.parse_args()
    try:
        cfg = lc.load_config(required=True)
        if args.cmd == "push":
            return cmd_push(args.workdir, cfg, args.bump)
        if args.cmd == "pull":
            return cmd_pull(args.workdir, cfg)
        if args.cmd == "gate":
            return cmd_gate(args.workdir, cfg)
        if args.cmd == "remove":
            return cmd_remove(args.workdir, cfg, args.content_id, args.keep_audit)
        if args.cmd == "intake":
            return cmd_intake(cfg, args.content_id)
        if args.cmd == "status":
            return cmd_status(cfg)
    except lc.LarkError as exc:
        print(f"Loi: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
