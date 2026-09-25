"""Dinh nghia cau truc Lark Base cho content-seo.

Hai lop ten goi, co chu dich:
  - KHOA NOI BO (content_id, state, review...) — code dung, ASCII, on dinh.
  - NHAN HIEN THI (Mã bài, Trạng thái, Kết quả duyệt...) — ten truong tren Base.

Nguoi dung chi nhin nhan tieng Viet; code khong bao gio phu thuoc vao chuoi
tieng Viet. Doi nhan hien thi chi can sua o day, khong dung toi logic.

Nguyen tac thiet ke cot: mot o chi ton tai neu nguoi duyet PHAI nhin no de ra
quyet dinh. Moi thu khac song trong file cuc bo va trong tai lieu tren Drive.
"""

from __future__ import annotations


# --------------------------------------------------------------------------
# Tien ich anh xa gia tri chuan <-> nhan hien thi
# --------------------------------------------------------------------------

def invert(mapping: dict[str, str]) -> dict[str, str]:
    return {v: k for k, v in mapping.items()}


def to_label(mapping: dict[str, str], canonical: str) -> str:
    return mapping.get((canonical or "").strip(), (canonical or "").strip())


def to_canonical(mapping: dict[str, str], value: str) -> str:
    """Chap nhan ca nhan tieng Viet lan gia tri chuan, de go tay kieu nao cung hieu."""
    v = (value or "").strip()
    if not v:
        return ""
    rev = invert(mapping)
    if v in rev:
        return rev[v]
    upper = v.upper().replace(" ", "_")
    return upper if upper in mapping else v


# --------------------------------------------------------------------------
# State machine
# --------------------------------------------------------------------------

# Quy trinh bat dau bang viec NGUOI DUNG dua tu khoa chinh + volume, nen khong con
# cong duyet chu de. "RESEARCHING" la trang thai lam viec, KHONG phai cong duyet:
# agent dang nghien cuu va len outline, khong ai phai bam gi.
STATE_LABELS = {
    "RESEARCHING": "Đang lên outline",
    "OUTLINE_PENDING": "Chờ duyệt outline",
    "DRAFTING": "Đang viết bài",
    "ARTICLE_PENDING": "Chờ duyệt bài",
    "DONE": "Đã duyệt, chờ bàn giao",
    # Ban nhap da nam tren WordPress, cho nguoi that doc va bam Publish. Agent khong
    # bao gio di qua duoc trang thai nay — dang bai la viec cua nguoi (quy tac 9).
    "WP_DRAFTED": "Đã lên nháp WordPress",
    "SKIPPED": "Bỏ qua",
}
STATES = list(STATE_LABELS)
STATE_OPTIONS = list(STATE_LABELS.values())

# Trang thai nao la mot cong duyet, va cong do mo thi di tiep sang dau.
GATE_STATES = {
    "OUTLINE_PENDING": "DRAFTING",
    "ARTICLE_PENDING": "DONE",
}

# Cong nao thi nguoi duyet dang doc tai lieu nao.
GATE_DOCUMENT = {
    "OUTLINE_PENDING": "Outline",
    "ARTICLE_PENDING": "Bài viết",
}

NEXT_ACTION = {
    "RESEARCHING": "Agent lên outline",
    "OUTLINE_PENDING": "Bạn duyệt outline",
    "DRAFTING": "Agent viết bài",
    "ARTICLE_PENDING": "Bạn duyệt bài",
    "DONE": "Bàn giao",
    "WP_DRAFTED": "Bạn đọc bản nháp rồi đăng",
    "SKIPPED": "—",
}

REVIEW_LABELS = {"APPROVED": "Đồng ý", "REJECTED": "Từ chối"}
REVIEW_OPTIONS = list(REVIEW_LABELS.values())

URL_DECISION_LABELS = {
    "CREATE": "Tạo bài mới",
    "UPDATE": "Cập nhật bài cũ",
    "MERGE": "Gộp bài",
    "SKIP": "Không viết",
}

CLAIM_TYPE_LABELS = {
    "FACT": "Dữ kiện",
    "INTERPRETATION": "Diễn giải",
    "FORECAST": "Dự báo",
    "EXPERIENCE": "Trải nghiệm",
}
RISK_LABELS = {"LOW": "Thấp", "MED": "Vừa", "HIGH": "Cao"}
CLAIM_STATUS_LABELS = {
    "VERIFIED": "Đã xác minh",
    "PARTIAL": "Một phần",
    "GAP": "Thiếu nguồn",
}

EVENT_LABELS = {
    "INTAKE": "Nhận từ khoá",
    "PUSH": "Đồng bộ lên",
    "PULL": "Đọc trạng thái",
    "REMOVE": "Gỡ bản ghi",
}

# Ba o duy nhat nguoi duyet dien.
REVIEW_BLOCK = ["review", "reviewer", "feedback"]


# --------------------------------------------------------------------------
# Cac bang trong Base — moi cot la (khoa_noi_bo, nhan_hien_thi, dac_ta_truong)
#
# Dac ta truong la mot dict ghep thang vao field JSON cua `base +field-create`
# (xem `lark-cli skills read lark-base references/lark-base-field-schema.md`).
# Khac voi Sheet: khong con do rong px, va Base THUC THI kieu du lieu chu khong
# chi goi y — select chi nhan dung option da khai bao.
# --------------------------------------------------------------------------


def _txt() -> dict:
    return {"type": "text"}


def _url() -> dict:
    return {"type": "text", "style": {"type": "url"}}


def _num() -> dict:
    return {"type": "number"}


def _check() -> dict:
    return {"type": "checkbox"}


def _sel(options, multiple: bool = False) -> dict:
    return {"type": "select", "multiple": multiple,
            "options": [{"name": o} for o in options]}


PIPELINE_TABLE = "Điều phối"
# Thu tu duoi day la THU TU COT tren Base, xep theo luong cong viec doc tu trai
# sang phai: ban dua de bai -> agent lam -> tai lieu de doc -> tin hieu chat luong
# -> cum ban bam -> thu se len Google -> so sach. Doi thu tu o day roi chay
# `lark_setup.py --rebuild` la Base doi theo.
PIPELINE_COLUMNS = [
    # --- Bạn đưa đề bài ---
    ("content_id", "Mã bài", _txt()),          # truong dau tien = primary field
    ("primary_query", "Truy vấn chính", _txt()),
    # Volume do NGUOI DUNG cung cap cung voi tu khoa chinh. De kieu so de sap xep va
    # uu tien bai ngay tren Base; agent khong bao gio tu dien con so nay.
    ("search_volume", "Volume", _num()),
    # CONG TAC CHAY, khong phai cong duyet. Ban tich o nay thi `lark_sync.py intake` moi
    # keo dong do xuong may va bat dau lam. Nho vay dong dang nhap do khong bi cuon vao
    # chay. No KHONG dung cum "Ket qua duyet" + "Nguoi duyet", khong di qua gate_status,
    # va khong bi xoa trang khi noi dung doi.
    ("keyword_ok", "Duyệt từ khoá", _check()),
    # --- Luồng đang ở đâu ---
    ("state", "Trạng thái", _sel(STATE_OPTIONS)),
    ("next_action", "Việc kế tiếp", _txt()),
    ("version", "Bản", _txt()),                 # PHAI la text: gia tri dang "0.1.4"
    # --- Tài liệu để bạn đọc khi duyệt ---
    ("brief_url", "Brief", _url()),
    ("outline_url", "Outline", _url()),
    ("article_url", "Bài viết", _url()),
    # Link mo thang ban nhap trong wp-admin, do `scripts/wp/wp_draft.py` ghi sau khi
    # tao nhap. Base nho vay noi duoc bai dang o dau, thay vi de link nam mot minh
    # duoi may trong work/<slug>/.wp.json.
    ("wp_draft_url", "Bản nháp WP", _url()),
    # --- Tín hiệu chất lượng, đọc trước khi bấm ---
    ("evidence", "Tóm tắt bằng chứng", _txt()),
    ("qa", "Máy kiểm", _txt()),
    # --- Cụm bạn bấm. Agent chỉ được xóa trắng, không bao giờ tự điền Đồng ý ---
    # Thu tu trong cum theo cach chu du an dang sap tren Base: doc gop y truoc, ky ten,
    # roi moi bam ket qua. Doi schema theo ho de lan `--rebuild` sau khong dap lai.
    ("feedback", "Góp ý / lý do từ chối", _txt()),
    ("reviewer", "Người duyệt", _txt()),        # giu text, khong dung kieu user
    ("review", "Kết quả duyệt", _sel(REVIEW_OPTIONS)),
    # --- Thứ sẽ lên Google. Lay thang tu front matter cua article.md, khong ai phai
    #     go lai, nhung day la thu nguoi duyet hay sua tay nhat truoc khi dang ---
    ("url_decision", "Quyết định URL", _sel(list(URL_DECISION_LABELS.values()))),
    ("slug", "Slug", _txt()),
    ("title", "Tiêu đề", _txt()),
    ("meta_description", "Mô tả meta", _txt()),
    # --- Sổ sách ---
    ("updated_at", "Cập nhật lúc", _txt()),     # chuoi ISO tu now_vn(), khong phai datetime
]

# Truong co tren Base ma khong nam trong schema — vi du truong lien ket nguoc tu bang
# Bang chung — duoc chen ngay SAU cot ghi o day, thay vi bi day xuong cuoi. Nho vay
# cot Claim nam canh nhom bang chung dung cho no thuoc ve.
VIEW_EXTRA_AFTER = {
    "pipeline": "Máy kiểm",
    "evidence": "Mã bài",
}

EVIDENCE_TABLE = "Bằng chứng"
EVIDENCE_COLUMNS = [
    ("claim_id", "Mã claim", _txt()),           # primary field
    ("content_id", "Mã bài", _txt()),
    ("claim", "Câu sẽ viết trong bài", _txt()),
    ("claim_type", "Loại phát ngôn", _sel(list(CLAIM_TYPE_LABELS.values()))),
    ("risk", "Rủi ro", _sel(list(RISK_LABELS.values()))),
    ("source_url", "Nguồn", _url()),
    ("supporting_quote", "Trích nguyên văn từ nguồn", _txt()),
    ("status", "Tình trạng", _sel(list(CLAIM_STATUS_LABELS.values()))),
    ("note", "Ghi chú", _txt()),
]

# Truong lien ket Bang chung -> Dieu phoi. `link_table` duoc dien bang table_id
# that luc chay lark_setup.py, nen de None o day.
EVIDENCE_LINK_KEY = "pipeline"
EVIDENCE_LINK_LABEL = "Bài"
PIPELINE_BACKLINK_LABEL = "Claim"


def evidence_link_field(pipeline_table_id: str) -> dict:
    """Field JSON cho lien ket hai chieu Bang chung <-> Dieu phoi."""
    return {
        "name": EVIDENCE_LINK_LABEL,
        "type": "link",
        "link_table": pipeline_table_id,
        "bidirectional": True,
        "bidirectional_link_field_name": PIPELINE_BACKLINK_LABEL,
    }


AUDIT_TABLE = "Nhật ký"
AUDIT_COLUMNS = [
    ("ts", "Thời điểm", _txt()),                # primary field
    ("content_id", "Mã bài", _txt()),
    ("version", "Bản", _txt()),
    ("event", "Sự kiện", _sel(list(EVENT_LABELS.values()))),
    ("actor", "Ai làm", _txt()),
    ("state", "Trạng thái", _txt()),
    ("details", "Chi tiết", _txt()),
]

GUIDE_TABLE = "Hướng dẫn"
GUIDE_COLUMNS = [("muc", "Mục", _txt()), ("noi_dung", "Nội dung", _txt())]
GUIDE_ROWS = [
    ["Bạn cần làm gì",
     "Nhìn cột Trạng thái và Việc kế tiếp. Khi Việc kế tiếp nói 'Bạn duyệt ...', mở link tương ứng "
     "(Brief / Outline / Bài viết), đọc, rồi điền cột Kết quả duyệt và Người duyệt."],
    ["Duyệt",
     "Kết quả duyệt = Đồng ý, và Người duyệt = tên bạn. Đủ hai ô đó là cổng mở. "
     "Không cần điền gì thêm."],
    ["Từ chối",
     "Kết quả duyệt = Từ chối, Người duyệt = tên bạn, và ghi lý do cụ thể vào cột Góp ý. "
     "Agent đọc góp ý, sửa, rồi đưa lại lên cùng ô đó."],
    ["Vì sao chỉ có MỘT cụm duyệt",
     "Một bản ghi tại một thời điểm chỉ đứng ở đúng một cổng. Cột Trạng thái cho biết bạn đang "
     "duyệt cái gì: 'Chờ duyệt outline' thì đọc Outline, 'Chờ duyệt bài' thì đọc Bài viết. "
     "'Đang lên outline' không phải cổng duyệt — agent đang làm, bạn chưa cần bấm gì."],
    ["Phê duyệt cũ có bị dùng lại không",
     "Không. Mỗi khi nội dung được duyệt thay đổi, agent tăng số Bản và XÓA TRẮNG cả ba ô duyệt. "
     "Bạn sẽ luôn duyệt đúng thứ đang nằm trước mặt. Agent chỉ được phép xóa trắng ô duyệt, "
     "không bao giờ được tự điền Đồng ý."],
    ["Cột Duyệt từ khoá",
     "Đây là CÔNG TẮC CHẠY, không phải cổng duyệt. Gõ từ khóa và Volume xong, tích ô này thì "
     "agent mới kéo dòng xuống máy và bắt đầu lên outline. Chưa tích thì dòng nằm im, nên bạn "
     "cứ nhập dở nhiều dòng rồi tích sau cũng được. Agent không bao giờ tự tích ô này."],
    ["Cột Volume",
     "Volume search do BẠN cung cấp cùng với từ khóa chính, không phải số agent tự đo. "
     "Dùng để sắp xếp và ưu tiên bài ngay trên bảng này. Trống nghĩa là bạn chưa đưa số."],
    ["Cột Bằng chứng",
     "Dạng '12 đã xác minh · 1 thiếu nguồn'. Thiếu nguồn nghĩa là claim chưa tra ra nguồn — "
     "claim đó không được xuất hiện trong bài dưới dạng câu khẳng định. Chi tiết ở bảng Bằng chứng, hoặc bấm trường Claim."],
    ["Cột Máy kiểm",
     "Dạng 'ĐẠT · 0 chặn · 3 cảnh báo'. Mọi lỗi chặn phải hết trước khi bài lên cổng duyệt. "
     "Giải trình cho từng cảnh báo nằm trong qa-report.md ở thư mục bàn giao trên máy."],
    ["Cột nào bạn không nên sửa",
     "Mọi cột ngoài Kết quả duyệt / Người duyệt / Góp ý đều do agent quản lý và sẽ bị ghi đè ở "
     "lần đồng bộ kế tiếp. Muốn đổi brief thì ghi vào Góp ý và từ chối, đừng sửa ô."],
    ["Giới hạn",
     "Máy kiểm ĐẠT chỉ nghĩa là không còn lỗi cơ học. Bài có đúng không, có hữu ích không, "
     "có bịa không thì vẫn phải bạn kiểm."],
    ["Không publish",
     "Base này dừng ở gói bàn giao. Việc đăng bài và tạo bản nháp CMS thuộc quy trình của "
     "D:\\Codex\\workspaces\\Create content blog."],
]


# View loc san tren bang Dieu phoi: dung mot cho de nguoi duyet mo moi ngay.
REVIEW_VIEW_NAME = "Đang chờ tôi duyệt"


def review_view_filter() -> dict:
    """Ban ghi dang dung o mot cong VA chua ai dien ket qua duyet."""
    gate_labels = [STATE_LABELS[s] for s in GATE_STATES]
    return {
        "logic": "and",
        "conditions": [
            ["Trạng thái", "intersects", gate_labels],
            ["Kết quả duyệt", "empty"],
        ],
    }


# --------------------------------------------------------------------------

def keys(columns) -> list[str]:
    return [c[0] for c in columns]


def labels(columns) -> list[str]:
    return [c[1] for c in columns]


def field_specs(columns) -> list[dict]:
    """Mang field JSON cho `base +table-create --fields` / `+field-create --json`."""
    out = []
    for _key, label, spec in columns:
        field = {"name": label}
        field.update(spec)
        out.append(field)
    return out


PIPELINE_KEYS = keys(PIPELINE_COLUMNS)
PIPELINE_LABELS = labels(PIPELINE_COLUMNS)
EVIDENCE_KEYS = keys(EVIDENCE_COLUMNS)
EVIDENCE_LABELS = labels(EVIDENCE_COLUMNS)
AUDIT_KEYS = keys(AUDIT_COLUMNS)
AUDIT_LABELS = labels(AUDIT_COLUMNS)

# Anh xa khoa noi bo -> nhan hien thi, dung khi dung payload ghi record.
PIPELINE_FIELD = dict(zip(PIPELINE_KEYS, PIPELINE_LABELS))
EVIDENCE_FIELD = dict(zip(EVIDENCE_KEYS, EVIDENCE_LABELS))
AUDIT_FIELD = dict(zip(AUDIT_KEYS, AUDIT_LABELS))

# Truong la select -> gia tri ghi phai boc trong mang mot phan tu.
SELECT_KEYS = {
    "pipeline": {k for k, _l, spec in PIPELINE_COLUMNS if spec.get("type") == "select"},
    "evidence": {k for k, _l, spec in EVIDENCE_COLUMNS if spec.get("type") == "select"},
    "audit": {k for k, _l, spec in AUDIT_COLUMNS if spec.get("type") == "select"},
}


TABLES = [
    {"id": "pipeline", "name": PIPELINE_TABLE, "columns": PIPELINE_COLUMNS},
    {"id": "evidence", "name": EVIDENCE_TABLE, "columns": EVIDENCE_COLUMNS},
    {"id": "audit", "name": AUDIT_TABLE, "columns": AUDIT_COLUMNS},
    {"id": "guide", "name": GUIDE_TABLE, "columns": GUIDE_COLUMNS},
]

SPEC = {t["id"]: t for t in TABLES}
