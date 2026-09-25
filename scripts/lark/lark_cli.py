"""Wrapper mong quanh @larksuite/cli.

Moi lenh Lark trong project nay di qua day, de co mot cho duy nhat xu ly:
cau hinh duong dan, parse JSON envelope, va bao loi ro rang.

Khong luu bat ky secret nao trong file config. Viec xac thuc do lark-cli tu lo
(dang nhap mot lan bang trinh duyet, token nam trong profile cua CLI).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
VN_TZ = timezone(timedelta(hours=7))

DEFAULT_TIMEOUT = 180


class LarkError(RuntimeError):
    pass


def now_vn() -> str:
    return datetime.now(VN_TZ).isoformat(timespec="seconds")


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

def _discover_node() -> str | None:
    for candidate in (
        os.environ.get("LARK_NODE"),
        r"C:\Users\{}\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe".format(
            os.environ.get("USERNAME", "")),
        shutil.which("node"),
        "/usr/bin/node",
        "/usr/local/bin/node",
    ):
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def _npm_global_root() -> str | None:
    """Hoi npm xem thu muc goi toan cuc nam dau. Tren VPS day la cach chac nhat."""
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        return None
    try:
        proc = subprocess.run([npm, "root", "-g"], capture_output=True, timeout=30,
                              encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    root = (proc.stdout or "").strip().splitlines()
    return root[0].strip() if root and os.path.isdir(root[0].strip()) else None


def _discover_cli() -> str | None:
    env = os.environ.get("LARK_CLI_ENTRY")
    if env and os.path.exists(env):
        return env

    # Duong dan truc tiep: <root goi toan cuc>/@larksuite/cli/scripts/run.js
    direct = []
    npm_root = _npm_global_root()
    if npm_root:
        direct.append(npm_root)
    direct += [
        "/usr/lib/node_modules",
        "/usr/local/lib/node_modules",
        os.path.expanduser("~/.local/share/pnpm/global/5/node_modules"),
        os.path.expanduser("~/.npm-global/lib/node_modules"),
    ]
    for root in direct:
        entry = os.path.join(root, "@larksuite", "cli", "scripts", "run.js")
        if os.path.exists(entry):
            return entry

    # Quet rong: pnpm doi ten thu muc theo hash nen khong doan duoc duong dan
    roots = [
        os.path.expandvars(r"%LOCALAPPDATA%\pnpm\global"),
        os.path.expanduser("~/AppData/Local/pnpm/global"),
        os.path.expanduser("~/.local/share/pnpm/global"),
        os.path.expanduser("~/.cache/pnpm/global"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if "run.js" in filenames and os.path.normpath(dirpath).replace("\\", "/").endswith(
                    "@larksuite/cli/scripts"):
                return os.path.join(dirpath, "run.js")
            # khong di sau qua muc can thiet
            if dirpath.count(os.sep) - root.count(os.sep) > 6:
                dirnames[:] = []
    return None


def load_config(required: bool = True) -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
    else:
        cfg = {}

    # Bien moi truong thang duong dan trong config, va duong dan khong ton tai thi
    # di do lai. Truoc day day la `setdefault`, nen mot config.json mang duong dan
    # cua may khac lam ca bo Lark chet ma LARK_NODE khong cuu duoc — dung loi ma
    # mot lan chuyen sang VPS se gap ngay.
    if os.environ.get("LARK_NODE") or not (
            cfg.get("node_executable") and os.path.exists(cfg["node_executable"])):
        cfg["node_executable"] = _discover_node()
    if os.environ.get("LARK_CLI_ENTRY") or not (
            cfg.get("lark_cli_entry") and os.path.exists(cfg["lark_cli_entry"])):
        cfg["lark_cli_entry"] = _discover_cli()

    if not cfg.get("node_executable") or not os.path.exists(cfg["node_executable"]):
        raise LarkError(
            "Khong tim thay node. Cai Node.js roi dat bien moi truong LARK_NODE, "
            "hoac them 'node_executable' vao scripts/lark/config.json."
        )
    if not cfg.get("lark_cli_entry") or not os.path.exists(cfg["lark_cli_entry"]):
        raise LarkError(
            "Khong tim thay @larksuite/cli. Cai bang 'npm i -g @larksuite/cli' "
            "(hoac pnpm add -g), hoac dat LARK_CLI_ENTRY tro toi "
            ".../@larksuite/cli/scripts/run.js."
        )
    if required and not cfg.get("app_token"):
        raise LarkError(
            "Chua co Base. Chay: python scripts/lark/lark_setup.py --title \"...\""
        )
    return cfg


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------
# Goi CLI
# --------------------------------------------------------------------------

def run(args: list[str], cfg: dict | None = None, timeout: int = DEFAULT_TIMEOUT,
        allow_empty: bool = True, stdin: str | None = None) -> dict:
    cfg = cfg or load_config(required=False)
    cmd = [cfg["node_executable"], cfg["lark_cli_entry"], *args]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, timeout=timeout,
            encoding="utf-8", errors="replace",
            input=stdin if stdin is not None else "",
        )
    except subprocess.TimeoutExpired:
        raise LarkError(f"Lark CLI qua thoi gian ({timeout}s): {' '.join(args[:3])}")

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()

    if not out:
        if proc.returncode != 0:
            raise LarkError(err or f"Lark CLI thoat voi ma {proc.returncode}")
        if allow_empty:
            return {}
        raise LarkError("Lark CLI khong tra ve du lieu")

    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        if proc.returncode != 0:
            raise LarkError(err or out[:500])
        raise LarkError(f"Khong doc duoc JSON tu Lark CLI: {out[:300]}")

    if isinstance(parsed, dict) and parsed.get("ok") is False:
        msg = (parsed.get("error") or {}).get("message") or out[:500]
        raise LarkError(msg)
    return parsed


# --------------------------------------------------------------------------
# Toa do trong Base
# --------------------------------------------------------------------------

def base_token(cfg: dict) -> str:
    token = (cfg.get("app_token") or "").strip()
    if not token:
        raise LarkError(
            "config.json chua co 'app_token'. Chay: "
            "python scripts/lark/lark_setup.py --title \"...\""
        )
    return token


def table_id(cfg: dict, key: str) -> str:
    tid = ((cfg.get("tables") or {}).get(key) or "").strip()
    if not tid:
        raise LarkError(
            f"config.json chua co tables.{key}. Chay: python scripts/lark/lark_setup.py --rebuild"
        )
    return tid


# --------------------------------------------------------------------------
# Nhom lenh `base` — dung cho thao tac schema: tao Base, bang, truong, view
#
# Mac dinh cua vai lenh `base` la --format markdown, nen luon ep --format json.
# Base luon thao tac voi danh tinh nguoi dung: --as bot chi thay tai nguyen cua
# chinh bot va tra ve "empty success" thay vi bao loi.
# --------------------------------------------------------------------------

def base_cmd(args: list[str], cfg: dict, timeout: int = DEFAULT_TIMEOUT) -> dict:
    return run(["base", *args, "--as", "user", "--format", "json"], cfg, timeout=timeout)


# --------------------------------------------------------------------------
# Nhom lenh `drive` — thu muc va di chuyen tai lieu
#
# Dung shortcut chu khong goi thang API: `+move` cua CLI tu poll task bat dong
# bo (Drive tra ve task_id cho thu muc), con goi thang endpoint /move thi phai
# tu xu ly vong poll do.
# --------------------------------------------------------------------------

def drive_cmd(args: list[str], cfg: dict, timeout: int = DEFAULT_TIMEOUT) -> dict:
    return run(["drive", *args, "--as", "user", "--format", "json"], cfg, timeout=timeout)


def folder_children(cfg: dict, folder_token: str) -> list[dict]:
    """Danh sach tep va thu muc con truc tiep cua mot thu muc Drive."""
    res = api("GET", "/open-apis/drive/v1/files", cfg,
              params={"folder_token": folder_token}, page_all=True)
    data = _unwrap(res)
    items = data.get("files") or data.get("items") or []
    return [i for i in items if isinstance(i, dict)]


def create_folder(cfg: dict, parent_token: str, name: str) -> str:
    res = drive_cmd(["+create-folder", "--folder-token", parent_token, "--name", name], cfg)
    data = _unwrap(res)
    return (data.get("token") or data.get("folder_token") or "").strip()


def move_file(cfg: dict, file_token: str, folder_token: str, file_type: str = "file") -> None:
    drive_cmd(["+move", "--file-token", file_token, "--type", file_type,
               "--folder-token", folder_token], cfg, timeout=300)


# --------------------------------------------------------------------------
# Record — di qua `lark-cli api` chu khong qua shortcut `base`
#
# Hai ly do, deu la gioi han that cua CLI:
#   1. Chi `api` co --page-all. Shortcut `base` chi co offset/limit thu cong.
#   2. Chi `api` doc duoc payload tu stdin. Shortcut `base` chi nhan @file voi
#      duong dan TUONG DOI, ma payload cua mot bai dai vuot gioi han ~32K cua
#      dong lenh Windows.
# Envelope tra ve van la {ok, data} nen run() parse duoc nhu moi lenh khac.
# --------------------------------------------------------------------------

API_ROOT = "/open-apis/base/v3/bases"
MAX_BATCH = 200          # tran cua batch_create / batch_update / batch_delete


def records_path(cfg: dict, table_key: str, suffix: str = "") -> str:
    return f"{API_ROOT}/{base_token(cfg)}/tables/{table_id(cfg, table_key)}/records{suffix}"


def api(method: str, path: str, cfg: dict, data=None, params: dict | None = None,
        page_all: bool = False, timeout: int = DEFAULT_TIMEOUT) -> dict:
    args = ["api", method, path, "--as", "user"]
    if params:
        args += ["--params", json.dumps(params, ensure_ascii=False)]
    if page_all:
        args += ["--page-all"]
    stdin = None
    if data is not None:
        args += ["--data", "-"]
        stdin = json.dumps(data, ensure_ascii=False)
    return run(args, cfg, timeout=timeout, stdin=stdin)


def _unwrap(res: dict) -> dict:
    """Boc lop `data` cua envelope; chap nhan ca truong hop khong co lop nay."""
    if not isinstance(res, dict):
        return {}
    data = res.get("data")
    return data if isinstance(data, dict) else res


def extract_records(res: dict) -> list[dict]:
    """Chuan hoa ve [{'record_id': str, 'fields': {nhan_hien_thi: gia_tri}}].

    API base/v3 tra ve dang MA TRAN chu khong phai danh sach object:
      data.fields         = ten cot, theo thu tu
      data.data           = mang cac dong, moi dong la mang gia tri cung thu tu
      data.record_id_list = record_id, chay SONG SONG voi data.data
    Ghep ba thu do lai moi ra duoc ban ghi. Van giu nhanh doc 'items'/'records'
    phong khi phien ban CLI khac tra ve dang object.
    """
    data = _unwrap(res)

    rows = data.get("data")
    names = data.get("fields")
    ids = data.get("record_id_list") or []
    if isinstance(rows, list) and isinstance(names, list) and names:
        out = []
        for i, row in enumerate(rows):
            if not isinstance(row, list):
                continue
            out.append({
                "record_id": ids[i] if i < len(ids) else "",
                "fields": {names[j]: row[j] for j in range(min(len(names), len(row)))},
            })
        return out

    items = data.get("items") or data.get("records") or []
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        out.append({
            "record_id": item.get("record_id") or item.get("id") or "",
            "fields": item.get("fields") or {},
        })
    return out


def list_records(cfg: dict, table_key: str) -> list[dict]:
    res = api("GET", records_path(cfg, table_key), cfg, page_all=True, timeout=300)
    return extract_records(res)


def create_records(cfg: dict, table_key: str, records: list[dict]) -> list[str]:
    """records = [{nhan_hien_thi: CellValue}]. Tra ve danh sach record_id."""
    ids: list[str] = []
    for i in range(0, len(records), MAX_BATCH):
        res = api("POST", records_path(cfg, table_key, "/batch_create"), cfg,
                  data={"create_records": records[i:i + MAX_BATCH]}, timeout=300)
        ids += (_unwrap(res).get("record_id_list") or [])
    return ids


def update_records(cfg: dict, table_key: str, updates: dict) -> None:
    """updates = {record_id: {nhan_hien_thi: CellValue}}."""
    items = list(updates.items())
    for i in range(0, len(items), MAX_BATCH):
        api("POST", records_path(cfg, table_key, "/batch_update"), cfg,
            data={"update_records": dict(items[i:i + MAX_BATCH])}, timeout=300)


def delete_records(cfg: dict, table_key: str, record_ids: list[str]) -> None:
    ids = [r for r in record_ids if r]
    for i in range(0, len(ids), MAX_BATCH):
        api("POST", records_path(cfg, table_key, "/batch_delete"), cfg,
            data={"record_id_list": ids[i:i + MAX_BATCH]}, timeout=300)


# --------------------------------------------------------------------------

def force_utf8() -> None:
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:                                     # noqa: BLE001
            pass
