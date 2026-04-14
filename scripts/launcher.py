#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import socket
import subprocess
import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent
APP_FILE = APP_DIR / "app.py"
REQUIREMENTS_FILE = APP_DIR / "requirements.txt"


LANG_ZH = "zh"
LANG_EN = "en"
LANG_JA = "ja"


TEXT = {
    LANG_ZH: {
        "title": "AI‑MA 启动器（命令行）",
        "choose_lang": "第一步：选择语言 / Choose language / 言語を選択",
        "lang_prompt": "请输入 1/2/3 后回车：",
        "lang_opts": ["1) 中文", "2) English", "3) 日本語"],
        "ask_ip": "请输入监听 IP（例如 127.0.0.1 或 0.0.0.0）：",
        "ask_port": "请输入端口（1-65535，例如 8502）：",
        "checking": "正在检测运行环境...",
        "ok": "环境检测通过。",
        "missing_app": "找不到 app.py：{path}",
        "bad_python": "Python 版本过低：{ver}。请使用 Python 3.9+（建议 3.10+）。",
        "missing_dep": "缺少依赖：{name}。请先安装依赖：{cmd}",
        "run": "正在启动服务：{url}",
        "hint_stop": "按 Ctrl+C 停止服务。",
        "invalid_ip": "IP 地址无效：{ip}",
        "invalid_port": "端口无效：{port}",
        "port_in_use": "端口已被占用：{ip}:{port}。请换一个端口或停止占用进程。",
        "install_cmd": "./venv/bin/python -m pip install -r requirements.txt  （或 python3 -m pip install -r requirements.txt）",
    },
    LANG_EN: {
        "title": "AI‑MA Launcher (CLI)",
        "choose_lang": "Step 1: Choose language / 选择语言 / 言語を選択",
        "lang_prompt": "Enter 1/2/3 and press Enter: ",
        "lang_opts": ["1) 中文", "2) English", "3) 日本語"],
        "ask_ip": "Server address (e.g. 127.0.0.1 or 0.0.0.0): ",
        "ask_port": "Port (1-65535, e.g. 8502): ",
        "checking": "Checking runtime environment...",
        "ok": "Environment OK.",
        "missing_app": "Cannot find app.py: {path}",
        "bad_python": "Python version too old: {ver}. Please use Python 3.9+ (3.10+ recommended).",
        "missing_dep": "Missing dependency: {name}. Install requirements first: {cmd}",
        "run": "Starting server at: {url}",
        "hint_stop": "Press Ctrl+C to stop.",
        "invalid_ip": "Invalid IP address: {ip}",
        "invalid_port": "Invalid port: {port}",
        "port_in_use": "Port already in use: {ip}:{port}. Choose another port or stop the process.",
        "install_cmd": "./venv/bin/python -m pip install -r requirements.txt  (or python3 -m pip install -r requirements.txt)",
    },
    LANG_JA: {
        "title": "AI‑MA ランチャー（CLI）",
        "choose_lang": "ステップ1：言語を選択 / Choose language / 选择语言",
        "lang_prompt": "1/2/3 を入力して Enter：",
        "lang_opts": ["1) 中文", "2) English", "3) 日本語"],
        "ask_ip": "待受IP（例：127.0.0.1 または 0.0.0.0）：",
        "ask_port": "ポート（1-65535、例：8502）：",
        "checking": "実行環境をチェック中...",
        "ok": "環境チェックOK。",
        "missing_app": "app.py が見つかりません：{path}",
        "bad_python": "Python バージョンが古すぎます：{ver}。Python 3.9+（推奨 3.10+）を使用してください。",
        "missing_dep": "依存関係が不足しています：{name}。先にインストールしてください：{cmd}",
        "run": "起動中：{url}",
        "hint_stop": "Ctrl+C で停止します。",
        "invalid_ip": "IP アドレスが無効です：{ip}",
        "invalid_port": "ポートが無効です：{port}",
        "port_in_use": "ポートが使用中です：{ip}:{port}。別のポートにするか、プロセスを停止してください。",
        "install_cmd": "./venv/bin/python -m pip install -r requirements.txt  （または python3 -m pip install -r requirements.txt）",
    },
}


def _t(lang: str, key: str, **kwargs) -> str:
    base = TEXT.get(lang, TEXT[LANG_ZH]).get(key, key)
    try:
        return base.format(**kwargs)
    except Exception:
        return base


def _choose_language() -> str:
    print("========================================")
    print("AI‑MA Launcher / 启动器 / ランチャー")
    print("========================================")
    print(TEXT[LANG_ZH]["choose_lang"])
    for line in TEXT[LANG_ZH]["lang_opts"]:
        print("  " + line)
    choice = input(TEXT[LANG_ZH]["lang_prompt"]).strip()
    if choice == "2":
        return LANG_EN
    if choice == "3":
        return LANG_JA
    return LANG_ZH


def _is_valid_ip(ip: str) -> bool:
    try:
        socket.inet_aton(ip)
        return True
    except OSError:
        return False


def _parse_port(raw: str) -> int | None:
    try:
        port = int(raw)
    except Exception:
        return None
    if 1 <= port <= 65535:
        return port
    return None


def _port_in_use(ip: str, port: int) -> bool:
    # Best-effort: try to bind. If it fails, the port is in use (or restricted).
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((ip, port))
        return False
    except OSError:
        return True
    finally:
        try:
            s.close()
        except Exception:
            pass


def _check_environment(lang: str) -> None:
    print(_t(lang, "checking"))

    if not APP_FILE.exists():
        raise SystemExit(_t(lang, "missing_app", path=str(APP_FILE)))

    if sys.version_info < (3, 9):
        raise SystemExit(_t(lang, "bad_python", ver=sys.version.split()[0]))

    required_imports = [
        "streamlit",
        "httpx",
        "openai",
        "pythonosc",
        "pydantic",
    ]
    for name in required_imports:
        try:
            importlib.import_module(name)
        except Exception:
            cmd = _t(lang, "install_cmd")
            preferred = _find_preferred_python()
            if preferred and Path(preferred).resolve() != Path(sys.executable).resolve():
                cmd = cmd + f"\nTip: try running with project venv python:\n  {preferred} {Path(__file__).resolve()}"
            raise SystemExit(_t(lang, "missing_dep", name=name, cmd=cmd))

    print(_t(lang, "ok"))


def _find_preferred_python() -> str | None:
    """
    Prefer a project venv python if it exists, so the launcher works even when
    system python doesn't have dependencies installed.
    """
    candidates: list[Path] = []
    # backup/v0.5/venv
    candidates.append(APP_DIR / "venv" / "bin" / "python")
    # repo root venv (e.g. AI-MA/venv) if this snapshot lives under backup/v0.5
    candidates.append(APP_DIR.parent.parent / "venv" / "bin" / "python")
    # common names
    candidates.append(APP_DIR / ".venv" / "bin" / "python")
    candidates.append(APP_DIR.parent.parent / ".venv" / "bin" / "python")

    for p in candidates:
        # Note: on some systems venv python may be a symlink with restrictive
        # mode bits; existence is enough for execv().
        if p.exists():
            return str(p)
    return None


def _reexec_if_needed() -> None:
    preferred = _find_preferred_python()
    if not preferred:
        return
    # If the current interpreter already has required deps, keep it.
    # Otherwise, try to switch to the preferred project venv python.
    try:
        importlib.import_module("streamlit")
        return
    except Exception:
        pass
    # Important: do NOT resolve symlinks here; venv python is often a symlink
    # and relies on its own directory to locate pyvenv.cfg/site-packages.
    if Path(sys.executable).resolve() == Path(preferred).resolve():
        return
    try:
        os.execv(preferred, [preferred, *sys.argv])
    except Exception:
        return


def main() -> int:
    # Auto-switch to project venv python if available, before any interactive IO,
    # so stdin alignment stays consistent.
    _reexec_if_needed()

    lang = _choose_language()
    print()
    print(_t(lang, "title"))
    print()

    ip = input(_t(lang, "ask_ip")).strip()
    if not _is_valid_ip(ip):
        print(_t(lang, "invalid_ip", ip=ip))
        return 2

    port_raw = input(_t(lang, "ask_port")).strip()
    port = _parse_port(port_raw)
    if port is None:
        print(_t(lang, "invalid_port", port=port_raw))
        return 2

    if _port_in_use(ip, port):
        print(_t(lang, "port_in_use", ip=ip, port=port))
        return 2

    _check_environment(lang)

    url = f"http://{ip}:{port}"
    print(_t(lang, "run", url=url))
    print(_t(lang, "hint_stop"))
    print()

    env = os.environ.copy()
    # Make sure Streamlit binds exactly to the user-provided address.
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_FILE),
        "--server.headless",
        "true",
        "--server.address",
        ip,
        "--server.port",
        str(port),
    ]
    proc = subprocess.Popen(cmd, cwd=str(APP_DIR), env=env)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        try:
            proc.terminate()
        except Exception:
            pass
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

