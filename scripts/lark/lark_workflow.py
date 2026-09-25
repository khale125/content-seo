"""Base Workflow bao tin khi 'Ket qua duyet' thay doi.

  python scripts/lark/lark_workflow.py --create
  python scripts/lark/lark_workflow.py --show
  python scripts/lark/lark_workflow.py --enable
  python scripts/lark/lark_workflow.py --disable
  python scripts/lark/lark_workflow.py --json      # in payload, khong goi API

Mat xich thu nhat cua chuoi bao duyet:

    Ban doi o Ket qua duyet tren Base
      -> workflow nay gui tin vao nhom chat co bot
      -> bot day event ve may, agent doc va chay tiep

Hai chi tiet khong duoc sai:

1. Dung SetRecordTrigger chu KHONG dung ChangeRecordTrigger. Loai sau bat ca
   them-moi, nen moi lan `lark_sync.py push` tao ban ghi deu no.

2. field_watch_info dung operator "is" va chi liet ke dung hai gia tri
   Dong y / Tu choi. Day la chot chong vong lap: cmd_push XOA TRANG o duyet sau
   khi tieu thu phe duyet. Neu trigger bat "moi thay doi cua field" thi chinh
   thao tac xoa trang cua agent se kich hoat lai workflow, va agent tu ban thong
   bao cho minh.

Tin nhan chi la chuong cua. No KHONG phai bang chung da duyet — chi
`lark_sync.py gate work/<slug>` tra ve exit 0 moi la da duyet (CLAUDE.md quy
tac 10). Workflow nay khong ghi gi vao Base.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import lark_cli as lc
import schema as S

WORKFLOW_TITLE = "Báo khi có kết quả duyệt"
TRIGGER_ID = "trigger_1"
ACTION_ID = "action_1"

# Cac truong duoc nhac trong noi dung tin nhan, theo thu tu hien thi.
MESSAGE_FIELDS = ["content_id", "state", "review", "reviewer", "feedback"]


def _label(key: str) -> str:
    return dict((c[0], c[1]) for c in S.PIPELINE_COLUMNS)[key]


def field_ids(cfg: dict) -> dict[str, str]:
    """{nhan hien thi: field_id} cua bang Dieu phoi."""
    res = lc.base_cmd(["+field-list", "--base-token", lc.base_token(cfg),
                       "--table-id", lc.table_id(cfg, "pipeline"), "--limit", "200"], cfg)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    out = {}
    for f in (data.get("items") or data.get("fields") or []):
        if isinstance(f, dict):
            name = (f.get("name") or "").strip()
            fid = (f.get("field_id") or f.get("id") or "").strip()
            if name and fid:
                out[name] = fid
    return out


def chat_id(cfg: dict) -> str:
    cid = (cfg.get("notify_chat_id") or "").strip()
    if not cid:
        raise lc.LarkError(
            "config.json chua co 'notify_chat_id'. Tao nhom co bot roi dien chat_id (oc_...)."
        )
    return cid


def build(cfg: dict) -> dict:
    ids = field_ids(cfg)
    review_label = _label("review")
    if review_label not in ids:
        raise lc.LarkError(f"Bang Dieu phoi khong co truong '{review_label}'.")

    content = [{"value_type": "text", "value": "Bản ghi vừa được duyệt hoặc từ chối.\n"}]
    for key in MESSAGE_FIELDS:
        label = _label(key)
        fid = ids.get(label)
        if not fid:
            continue
        content.append({"value_type": "text", "value": f"{label}: "})
        content.append({"value_type": "ref", "value": f"$.{TRIGGER_ID}.{fid}"})
        content.append({"value_type": "text", "value": "\n"})

    return {
        "client_token": f"content-seo-{int(time.time())}",
        "title": WORKFLOW_TITLE,
        "steps": [
            {
                "id": TRIGGER_ID,
                "type": "SetRecordTrigger",
                "title": "Ô Kết quả duyệt đổi thành Đồng ý hoặc Từ chối",
                "next": ACTION_ID,
                "data": {
                    "table_name": S.PIPELINE_TABLE,
                    "field_watch_info": [{
                        "field_name": review_label,
                        # "containsAny" chu khong phai "is": voi truong
                        # SingleSelect, operator "is" chi nhan DUNG MOT option,
                        # ma o day can khop ca Dong y lan Tu choi.
                        "operator": "containsAny",
                        # Chi hai gia tri nay. O trang (do agent xoa) khong khop,
                        # nen khong kich hoat lai workflow.
                        #
                        # value_type PHAI la "option": Lark tu choi "text" cho
                        # truong select (fieldType 3) voi thong bao
                        # "allowed: 'option,ref'".
                        "value": [{"value_type": "option", "value": {"name": v}}
                                  for v in S.REVIEW_LABELS.values()],
                    }],
                    "trigger_control_list": [],
                },
            },
            {
                "id": ACTION_ID,
                "type": "LarkMessageAction",
                "title": "Báo vào nhóm duyệt",
                "next": None,
                "data": {
                    "receiver": [{"value_type": "group",
                                  "value": {"id": chat_id(cfg), "name": "Duyệt content SEO"}}],
                    "send_to_everyone": False,
                    "title": [{"value_type": "text", "value": "Content SEO — có kết quả duyệt"}],
                    "content": content,
                    "btn_list": [{
                        "text": "Mở bảng Điều phối",
                        "btn_action": "openLink",
                        "link": [{"value_type": "text", "value": cfg.get("base_url", "")}],
                    }],
                },
            },
        ],
    }


def find_workflow(cfg: dict) -> dict | None:
    res = lc.base_cmd(["+workflow-list", "--base-token", lc.base_token(cfg)], cfg)
    data = res.get("data") if isinstance(res.get("data"), dict) else res
    for item in (data.get("items") or []):
        if isinstance(item, dict) and (item.get("title") or "").strip() == WORKFLOW_TITLE:
            return item
    return None


def workflow_id(cfg: dict) -> str:
    wf = find_workflow(cfg)
    if not wf:
        raise lc.LarkError(
            f"Chua co workflow '{WORKFLOW_TITLE}'. Chay --create truoc."
        )
    return (wf.get("workflow_id") or wf.get("id") or "").strip()


# --------------------------------------------------------------------------

def cmd_create(cfg: dict) -> int:
    if find_workflow(cfg):
        raise lc.LarkError(
            f"Da co workflow '{WORKFLOW_TITLE}' tren Base. Dung --show de xem, "
            "hoac xoa tren giao dien Base neu muon tao lai."
        )
    payload = build(cfg)
    lc.base_cmd(["+workflow-create", "--base-token", lc.base_token(cfg),
                 "--json", json.dumps(payload, ensure_ascii=False)], cfg, timeout=300)
    wf = find_workflow(cfg)
    print(f"Da tao '{WORKFLOW_TITLE}' (dang TAT).")
    print(f"  workflow_id: {(wf or {}).get('workflow_id') or (wf or {}).get('id')}")
    print("Buoc ke tiep: --show de doc lai, roi --enable.")
    return 0


def cmd_show(cfg: dict) -> int:
    wid = workflow_id(cfg)
    res = lc.base_cmd(["+workflow-get", "--base-token", lc.base_token(cfg),
                       "--workflow-id", wid], cfg)
    print(json.dumps(res.get("data") or res, ensure_ascii=False, indent=2))
    return 0


def cmd_toggle(cfg: dict, on: bool) -> int:
    wid = workflow_id(cfg)
    verb = "+workflow-enable" if on else "+workflow-disable"
    lc.base_cmd([verb, "--base-token", lc.base_token(cfg), "--workflow-id", wid], cfg)
    print(("Da BAT " if on else "Da TAT ") + WORKFLOW_TITLE)
    return 0


def main() -> int:
    lc.force_utf8()
    ap = argparse.ArgumentParser(description="Base Workflow bao khi co ket qua duyet.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--create", action="store_true")
    g.add_argument("--show", action="store_true")
    g.add_argument("--enable", action="store_true")
    g.add_argument("--disable", action="store_true")
    g.add_argument("--json", action="store_true", help="In payload, khong goi API")
    args = ap.parse_args()

    try:
        cfg = lc.load_config()
        if args.json:
            print(json.dumps(build(cfg), ensure_ascii=False, indent=2))
            return 0
        if args.create:
            return cmd_create(cfg)
        if args.show:
            return cmd_show(cfg)
        return cmd_toggle(cfg, args.enable)
    except lc.LarkError as exc:
        print(f"Loi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
