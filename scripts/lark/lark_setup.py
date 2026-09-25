"""Tao va kiem tra Base cho content-seo. Chay mot lan luc dung du an.

  python scripts/lark/lark_setup.py --title "Content SEO — Bat dong san"
  python scripts/lark/lark_setup.py --verify
  python scripts/lark/lark_setup.py --rebuild

Khac voi ban Sheet truoc day: khong con do rong cot, freeze hay to mau. Base
thuc thi kieu du lieu that, nen phan "trang tri" bien mat va phan "rang buoc"
manh len — truong select chi nhan dung option da khai bao.

Ma thoat: 0 = on, 1 = co van de can sua, 2 = loi chay.
"""

from __future__ import annotations

import argparse
import json
import sys

import lark_cli as lc
import schema as S


# --------------------------------------------------------------------------
# Tien ich
# --------------------------------------------------------------------------

def _first(data: dict, *keys: str) -> str:
    """Lay gia tri dau tien tim duoc trong cac khoa, ke ca long mot cap."""
    for key in keys:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    for val in data.values():
        if isinstance(val, dict):
            found = _first(val, *keys)
            if found:
                return found
    return ""


def table_map(cfg: dict) -> dict[str, str]:
    """Ten bang -> table_id, doc that tu Base."""
    res = lc.base_cmd(["+table-list", "--base-token", lc.base_token(cfg), "--limit", "100"], cfg)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    items = data.get("items") or data.get("tables") or []
    out = {}
    for item in items:
        if isinstance(item, dict):
            name = (item.get("name") or "").strip()
            tid = (item.get("table_id") or item.get("id") or "").strip()
            if name and tid:
                out[name] = tid
    return out


# Ma kieu truong cua Bitable. Chi liet ke nhung kieu schema.py dang dung.
FIELD_TYPE_NUM = {"text": 1, "number": 2, "select": 3, "link": 18}


def field_items(cfg: dict, table_id: str) -> list[dict]:
    """Danh sach truong day du: can field_id va property.options de doi chieu select.

    Phai goi API tho. `base +field-list` cua CLI tra ve field_id = null va
    property = null, nen khong dung duoc cho viec doi chieu hay sua option.
    """
    res = lc.api("GET",
                 f"/open-apis/bitable/v1/apps/{lc.base_token(cfg)}/tables/{table_id}/fields",
                 cfg, page_all=True)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    out = []
    for f in (data.get("items") or []):
        if not isinstance(f, dict):
            continue
        out.append({
            "name": (f.get("field_name") or f.get("name") or "").strip(),
            "field_id": f.get("field_id"),
            "type": f.get("type"),
            "options": [o.get("name") for o in ((f.get("property") or {}).get("options") or [])],
            # Giu ca id: sua option ma khong gui lai id cu thi Lark coi do la option
            # moi tinh va **xoa trang moi o dang dung option do**. Xem sync_select_options.
            "option_items": [{"id": o.get("id"), "name": o.get("name")}
                             for o in ((f.get("property") or {}).get("options") or [])],
        })
    return out


def field_names(cfg: dict, table_id: str) -> list[str]:
    return [f["name"] for f in field_items(cfg, table_id)]


def select_gaps(cfg: dict, spec: dict, table_id: str) -> list[tuple]:
    """[(ten truong, field_id, option dang co, option con thieu)] cho cac cot select."""
    want = {label: [o["name"] for o in (fspec.get("options") or [])]
            for _k, label, fspec in spec["columns"] if fspec.get("type") == "select"}
    gaps = []
    for f in field_items(cfg, table_id):
        if f["name"] not in want or f["type"] != FIELD_TYPE_NUM["select"]:
            continue
        lack = [o for o in want[f["name"]] if o not in f["options"]]
        if lack:
            gaps.append((f["name"], f["field_id"], f["option_items"], lack))
    return gaps


def sync_select_options(cfg: dict, spec: dict, table_id: str) -> None:
    """Them option con thieu vao cac cot select da ton tai.

    THUAN THEM, giong phan con lai cua rebuild: option cu khong bi xoa, vi ban ghi
    dang dung no van phai doc duoc. Muon don thi xoa tay tren Base.

    **Phai gui lai option cu kem `id` cua chung.** Ban dau ham nay gui
    `[{"name": o} for o in have + lack]`, tuc khong co id nao; Lark hieu la toan bo
    option deu moi, cap id moi cho ca danh sach, va **moi o dang tro toi option cu bi
    xoa trang**. Da xay ra that ngay 24/09/2026: chi them mot option
    "Da len nhap WordPress" ma o Trang thai cua bai 001 mat gia tri "Cho duyet bai".
    Mat mot o select khong bao loi o dau — khong ai nhin thay cho den luc luong sau
    doc Base va thay bai nhu chua bat dau.
    """
    for name, fid, have, lack in select_gaps(cfg, spec, table_id):
        if not fid:
            print(f"  [BO QUA] {spec['name']}/{name}: khong doc duoc field_id")
            continue
        print(f"  [OPTION] {spec['name']}/{name}: them " + ", ".join(lack))
        options = [{"id": o["id"], "name": o["name"]} if o.get("id") else {"name": o["name"]}
                   for o in have] + [{"name": o} for o in lack]
        lc.api("PUT",
               f"/open-apis/bitable/v1/apps/{lc.base_token(cfg)}/tables/{table_id}/fields/{fid}",
               cfg,
               data={"field_name": name, "type": FIELD_TYPE_NUM["select"],
                     "property": {"options": options}})


def views_of(cfg: dict, table_id: str) -> list[dict]:
    """[{id, name, type}] cua moi view trong bang."""
    res = lc.base_cmd(["+view-list", "--base-token", lc.base_token(cfg),
                       "--table-id", table_id, "--limit", "100"], cfg)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    out = []
    for v in (data.get("views") or data.get("items") or []):
        if isinstance(v, dict) and (v.get("id") or v.get("view_id")):
            out.append({"id": v.get("id") or v.get("view_id"),
                        "name": v.get("name") or "", "type": v.get("type") or ""})
    return out


def view_order(cfg: dict, table_id: str, view_id: str) -> list[str]:
    res = lc.base_cmd(["+view-get-visible-fields", "--base-token", lc.base_token(cfg),
                       "--table-id", table_id, "--view-id", view_id], cfg)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    vf = data.get("visible_fields")
    return [str(x) for x in vf] if isinstance(vf, list) else []


def is_subsequence(got: list[str], want: list[str]) -> bool:
    """`got` co phai `want` da bi bo bot vai phan tu, thu tu con lai giu nguyen?

    Dung de phan biet "nguoi duyet an vai cot" voi "thu tu cot sai".
    """
    it = iter(want)
    return all(name in it for name in got)


def wanted_order(cfg: dict, spec: dict, table_id: str) -> list[str]:
    """Thu tu cot mong muon: theo schema, cac truong la chen sau moc VIEW_EXTRA_AFTER."""
    want = S.labels(spec["columns"])
    on_base = field_names(cfg, table_id)
    extras = [f for f in on_base if f and f not in want]
    if not extras:
        return [w for w in want if w in on_base]

    anchor = (getattr(S, "VIEW_EXTRA_AFTER", {}) or {}).get(spec["id"])
    order = [w for w in want if w in on_base]
    if anchor and anchor in order:
        i = order.index(anchor) + 1
        return order[:i] + extras + order[i:]
    return order + extras


def sync_view_order(cfg: dict, spec: dict, table_id: str,
                    new_fields: tuple[str, ...] = ()) -> None:
    """Ap thu tu cot cua schema len MOI view cua bang, NHUNG khong dung toi cot da an.

    Ap cho moi view chu khong chi view dau tien: nguoi duyet lam viec tren view da
    loc san, de view do lech thu tu thi coi nhu chua sap gi.

    Cho de sai truoc day: ham nay tung dat `visible_fields = want`, tuc bat hien lai
    dung nhung cot ma nguoi duyet da co y an trong view cua ho. `--verify` thi da phan
    biet "an bot cot" voi "sai thu tu" tu truoc, nen rebuild cung phai ton trong dieu
    do. Nay chi sap lai nhung cot DANG HIEN, cong voi cac cot vua duoc tao o luot
    rebuild nay — cot moi chua tung xuat hien trong view nao nen khong the la cot an.
    """
    want = wanted_order(cfg, spec, table_id)
    if not want:
        return
    for v in views_of(cfg, table_id):
        if v["type"] and v["type"] != "grid":
            continue
        have = view_order(cfg, table_id, v["id"])
        if not have:
            continue
        keep = [f for f in want if f in have or f in new_fields]
        if keep == have:
            continue
        hidden = len(want) - len(keep)
        print(f"  [COT   ] {spec['name']}/{v['name'] or v['id']}: sap lai {len(keep)} cot"
              + (f" (giu an {hidden})" if hidden else ""))
        lc.base_cmd(["+view-set-visible-fields", "--base-token", lc.base_token(cfg),
                     "--table-id", table_id, "--view-id", v["id"],
                     "--json", json.dumps({"visible_fields": keep}, ensure_ascii=False)], cfg)


def create_table(cfg: dict, spec: dict, extra_fields: list[dict] | None = None) -> None:
    fields = S.field_specs(spec["columns"]) + list(extra_fields or [])
    lc.base_cmd([
        "+table-create",
        "--base-token", lc.base_token(cfg),
        "--name", spec["name"],
        "--fields", json.dumps(fields, ensure_ascii=False),
    ], cfg, timeout=300)


def sync_config_tables(cfg: dict) -> dict[str, str]:
    """Doi chieu ten bang tren Base voi SPEC, ghi table_id vao config."""
    found = table_map(cfg)
    tables = {}
    missing = []
    for spec in S.TABLES:
        tid = found.get(spec["name"])
        if tid:
            tables[spec["id"]] = tid
        else:
            missing.append(spec["name"])
    cfg["tables"] = tables
    lc.save_config(cfg)
    if missing:
        print("  [THIEU] bang chua co: " + ", ".join(missing))
    return tables


def fill_guide(cfg: dict) -> None:
    """Do noi dung huong dan vao bang Huong dan (xoa cu, ghi moi)."""
    existing = lc.list_records(cfg, "guide")
    if existing:
        lc.delete_records(cfg, "guide", [r["record_id"] for r in existing])
    muc, noi_dung = S.labels(S.GUIDE_COLUMNS)
    rows = [{muc: row[0], noi_dung: row[1]} for row in S.GUIDE_ROWS]
    lc.create_records(cfg, "guide", rows)


def make_review_view(cfg: dict) -> None:
    """View 'Dang cho toi duyet'. Khong chan setup neu that bai."""
    pipeline = lc.table_id(cfg, "pipeline")
    try:
        lc.base_cmd([
            "+view-create", "--base-token", lc.base_token(cfg), "--table-id", pipeline,
            "--json", json.dumps({"name": S.REVIEW_VIEW_NAME, "type": "grid"},
                                 ensure_ascii=False),
        ], cfg)
        # Ket qua cua +view-create long trong mang, khong doc thang duoc id —
        # liet ke lai roi tim theo ten cho chac.
        listed = lc.base_cmd(["+view-list", "--base-token", lc.base_token(cfg),
                              "--table-id", pipeline], cfg)
        views = (listed.get("data") or {}).get("views") or []
        view_id = next((v.get("id") for v in views
                        if isinstance(v, dict) and v.get("name") == S.REVIEW_VIEW_NAME), "")
        if not view_id:
            print("  [BO QUA] tao view xong nhung khong doc duoc view_id, chua dat duoc bo loc.")
            return
        lc.base_cmd([
            "+view-set-filter", "--base-token", lc.base_token(cfg), "--table-id", pipeline,
            "--view-id", view_id,
            "--json", json.dumps(S.review_view_filter(), ensure_ascii=False),
        ], cfg)
        print(f"  [OK] view '{S.REVIEW_VIEW_NAME}' da co bo loc")
    except lc.LarkError as exc:
        print(f"  [BO QUA] khong tao duoc view '{S.REVIEW_VIEW_NAME}': {exc}")
        print("          Khong sao — day chi la tien nghi, quy trinh khong phu thuoc vao no.")


# --------------------------------------------------------------------------
# create
# --------------------------------------------------------------------------

def create(title: str, folder_token: str | None) -> int:
    cfg = lc.load_config(required=False)
    if cfg.get("app_token"):
        raise lc.LarkError(
            "config.json da co app_token: " + cfg["app_token"] +
            "\nXoa truong do neu that su muon tao Base moi, hoac dung --verify / --rebuild."
        )

    pipeline_spec = S.SPEC["pipeline"]
    # Khong truyen --time-zone: Lark tu choi "Asia/Ho_Chi_Minh", va du an khong
    # phu thuoc mui gio cua Base (updated_at luu dang text tu now_vn()).
    args = [
        "+base-create",
        "--name", title,
        "--table-name", pipeline_spec["name"],
        "--fields", json.dumps(S.field_specs(pipeline_spec["columns"]), ensure_ascii=False),
    ]
    if folder_token:
        args += ["--folder-token", folder_token]

    print(f"Tao Base '{title}' ...")
    res = lc.base_cmd(args, cfg, timeout=300)
    app_token = _first(res, "app_token", "base_token", "token")
    if not app_token:
        raise lc.LarkError("Tao Base xong nhung khong doc duoc app_token tu ket qua tra ve:\n"
                           + json.dumps(res, ensure_ascii=False)[:600])

    cfg["app_token"] = app_token
    cfg["base_url"] = _first(res, "url", "base_url") or f"https://base.larksuite.com/base/{app_token}"
    cfg["title"] = title
    for legacy in ("workbook_url", "spreadsheet_token", "sheets"):
        cfg.pop(legacy, None)
    lc.save_config(cfg)
    print(f"  app_token: {app_token}")

    tables = sync_config_tables(cfg)
    pipeline_id = tables.get("pipeline")
    if not pipeline_id:
        raise lc.LarkError("Khong tim thay bang '%s' sau khi tao Base." % pipeline_spec["name"])

    # Bang Bang chung mang them truong lien ket hai chieu ve Dieu phoi.
    print("Tao cac bang con lai ...")
    create_table(cfg, S.SPEC["evidence"], [S.evidence_link_field(pipeline_id)])
    create_table(cfg, S.SPEC["audit"])
    create_table(cfg, S.SPEC["guide"])
    sync_config_tables(cfg)

    print("Do noi dung huong dan ...")
    fill_guide(cfg)

    print("Tao view cho nguoi duyet ...")
    make_review_view(cfg)

    print()
    print("XONG. Base: " + cfg["base_url"])
    print("Buoc ke tiep: python scripts/lark/lark_sync.py push work/<slug>")
    return 0


# --------------------------------------------------------------------------
# verify
# --------------------------------------------------------------------------

def verify() -> int:
    cfg = lc.load_config()
    print("Base: " + (cfg.get("base_url") or cfg.get("app_token", "")))
    found = table_map(cfg)
    problems = 0

    for spec in S.TABLES:
        tid = found.get(spec["name"])
        if not tid:
            print(f"[THIEU] bang '{spec['name']}'")
            problems += 1
            continue
        want = S.labels(spec["columns"])
        if spec["id"] == "evidence":
            want = want + [S.EVIDENCE_LINK_LABEL]
        if spec["id"] == "pipeline":
            want = want + [S.PIPELINE_BACKLINK_LABEL]
        have = field_names(cfg, tid)
        missing = [w for w in want if w not in have]
        extra = [h for h in have if h not in want]
        if missing:
            print(f"[THIEU] {spec['name']}: {', '.join(missing)}")
            problems += 1
        # Doi ten mot option trong schema.py ma khong doi tren Base thi push dau tien
        # se vo, nen verify phai bao ca cho nay chu khong chi bao thieu truong.
        gaps = select_gaps(cfg, spec, tid)
        for fname, _fid, _have, lack in gaps:
            print(f"[OPTION] {spec['name']}/{fname}: thieu option " + ", ".join(lack))
            problems += 1
        if extra:
            print(f"[THUA ] {spec['name']}: {', '.join(extra)}")
        # Thu tu cot cung phai khop schema, vi cot moi them luon bi Lark day xuong cuoi.
        #
        # Nhung phai phan biet HAI viec khac nhau, khong thi bao dong oan: nguoi duyet co
        # quyen AN mot vai cot trong view cua ho, va khi do `visible_fields` ngan hon
        # want_order du thu tu con lai van dung. Truoc day cho nay bao "thu tu cot lech"
        # cho ca truong hop do, va cach "sua" duy nhat la chay --rebuild — tuc bat hien
        # lai dung nhung cot ho da co y an. Chi coi la lech khi thu tu TUONG DOI sai.
        want_order = wanted_order(cfg, spec, tid)
        lech, an = [], []
        for v in views_of(cfg, tid):
            if v["type"] and v["type"] != "grid":
                continue
            got = view_order(cfg, tid, v["id"])
            if not got or got == want_order:
                continue
            name = v["name"] or v["id"]
            if is_subsequence(got, want_order):
                an.append("%s (%d cot an)" % (name, len(want_order) - len(got)))
            else:
                lech.append(name)
        if lech:
            print(f"[COT   ] {spec['name']}: thu tu cot lech o view " + ", ".join(lech))
            problems += 1
        if an:
            print(f"[AN    ] {spec['name']}: " + ", ".join(an)
                  + " — thu tu dung, khong can sua. Muon hien lai thi chay --rebuild.")
        if not missing and not extra and not gaps and not lech:
            print(f"[OK   ] {spec['name']} ({len(have)} truong)")

    if cfg.get("tables") != {s["id"]: found[s["name"]] for s in S.TABLES if s["name"] in found}:
        print("[LECH ] config.json.tables khong khop Base — dang cap nhat lai.")
        sync_config_tables(cfg)

    print()
    print("Khong co van de." if not problems else f"Co {problems} van de can sua.")
    return 1 if problems else 0


# --------------------------------------------------------------------------
# rebuild
# --------------------------------------------------------------------------

def rebuild() -> int:
    """Bo sung bang va truong con thieu. THUAN THEM — khong xoa gi bao gio.

    Truoc day rebuild tu choi chay khi bang Dieu phoi con ban ghi. Chan nhu vay
    la qua tay: no khoa luon duong sua schema ma CLAUDE.md quy tac 11 chi dinh
    (sua schema.py roi --rebuild) tren moi Base dang co du lieu that. Truong bi
    bo khoi schema.py van phai xoa tay tren Base — rebuild khong dung toi.
    """
    cfg = lc.load_config()
    found = table_map(cfg)

    for spec in S.TABLES:
        if spec["name"] in found:
            print(f"  [CO   ] {spec['name']}")
            continue
        extra = []
        if spec["id"] == "evidence":
            pid = found.get(S.PIPELINE_TABLE) or (table_map(cfg)).get(S.PIPELINE_TABLE)
            if not pid:
                print("  [HOAN ] Bang chung can bang Dieu phoi co truoc, se tao o luot sau")
                continue
            extra = [S.evidence_link_field(pid)]
        print(f"  [TAO  ] {spec['name']}")
        create_table(cfg, spec, extra)
        found = table_map(cfg)

    sync_config_tables(cfg)

    # Bo sung truong con thieu trong cac bang da co.
    for spec in S.TABLES:
        tid = (cfg.get("tables") or {}).get(spec["id"])
        if not tid:
            continue
        have = field_names(cfg, tid)
        missing = [f for f in S.field_specs(spec["columns"]) if f["name"] not in have]
        if spec["id"] == "evidence" and S.EVIDENCE_LINK_LABEL not in have:
            pid = (cfg.get("tables") or {}).get("pipeline")
            if pid:
                missing.append(S.evidence_link_field(pid))
        if missing:
            print(f"  [THEM ] {spec['name']}: " + ", ".join(f["name"] for f in missing))
            lc.base_cmd(["+field-create", "--base-token", lc.base_token(cfg),
                         "--table-id", tid,
                         "--json", json.dumps(missing, ensure_ascii=False)], cfg, timeout=300)
        sync_select_options(cfg, spec, tid)
        sync_view_order(cfg, spec, tid,
                        tuple(f["name"] for f in missing))

    fill_guide(cfg)
    print()
    print("Rebuild xong.")
    return 0


# --------------------------------------------------------------------------

def main() -> int:
    lc.force_utf8()
    ap = argparse.ArgumentParser(description="Tao va kiem tra Base cho content-seo.")
    ap.add_argument("--title", default="Content SEO — Bất động sản (Muaban.net)")
    ap.add_argument("--folder-token", default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()

    try:
        if args.verify:
            return verify()
        if args.rebuild:
            return rebuild()
        return create(args.title, args.folder_token)
    except lc.LarkError as exc:
        print(f"Loi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
