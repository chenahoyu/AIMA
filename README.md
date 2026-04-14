# AI‑MA (v0.5) — Natural‑language grandMA3 OSC Assistant
# AI‑MA (v0.5) — 自然语言 grandMA3 OSC 助手

AI‑MA is a Streamlit-based web console that turns natural-language lighting requests into structured commands and sends them to **grandMA3** via **OSC/UDP** (`/cmd`).

AI‑MA 是一个基于 Streamlit 的 Web 控制台，它能将自然语言灯光需求转化为结构化指令，并通过 **OSC/UDP** (`/cmd`) 发送至 **grandMA3** 控制台。

This README describes the **`backup/v0.5/`** snapshot.
本自述文件描述的是 **`backup/v0.5/`** 快照版本。

---

## Features | 功能特性

* **Chat-style UI**: Built with Streamlit (`app.py`).
    **对话式 UI**: 使用 Streamlit 构建 (`app.py`)。

* **Natural language → JSON → grandMA3 commands**: Seamless translation of intent to syntax.
    **自然语言 → JSON → grandMA3 指令**: 实现意图到语法的无缝转换。

* **OSC sender**: Features command sanitization and small inter-command delay for stability.
    **OSC 发送器**: 具备指令清洗功能及指令间微秒级延迟，确保传输稳定性。

* **Conversation persistence**: Local JSON storage for history.
    **对话持久化**: 使用本地 JSON 文件保存历史记录。

* **Local caching**: Stores API keys, base URL, model ID, and UI preferences.
    **本地缓存**: 缓存 API 密钥、基准 URL、模型 ID 及 UI 偏好设置。

* **CLI launcher**: Includes language selection, IP/port prompts, and environment checks.
    **命令行启动器**: 支持语言选择、IP/端口提示及环境检查 (`scripts/launcher.py`)。

* **Network modes**: Supports direct connection, system proxy, env SOCKS5, or custom proxies.
    **网络模式**: 支持直连、系统代理、环境变量 SOCKS5 及自定义代理。

* **Global UI language switching**: Supports ZH/EN/JA for the console.
    **全球化多语言切换**: 控制台支持中文、英文、日文切换。

* **Static developer doc**: Offline Chinese documentation in HTML format.
    **静态开发文档**: 提供离线版中文开发文档 (`docs/开发文档.html`)。

---

## Tech Stack | 技术栈

* **Python**: 3.9+ recommended (3.10+ preferred).
    **Python**: 推荐 3.9+ (首选 3.10+)。

* **UI**: Streamlit.
    **界面**: Streamlit。

* **LLM**: OpenAI Python SDK (OpenAI-compatible Chat Completions endpoint).
    **大模型**: OpenAI Python SDK (兼容 OpenAI 的聊天补全接口)。

* **HTTP**: `httpx` (with SOCKS support).
    **HTTP**: `httpx` (支持 SOCKS 代理)。

* **Models**: Pydantic v2.
    **模型层**: Pydantic v2。

* **OSC**: `python-osc`.
    **OSC**: `python-osc`。

---

## Getting Started | 快速上手

### Prerequisites | 前提条件
- Python 3.9+
- macOS/Linux shell

### Install | 安装
```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

### Run (local) | 运行 (本地)
```bash
./venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

### Run via CLI launcher | 通过命令行启动器运行
The launcher guides you through language selection, server setup, and environment checks.
启动器将引导您完成语言选择、服务器设置和环境检查。
```bash
/v0.5/scripts/launcher.py
```

---

## Configuration | 配置说明

### grandMA3 OSC
Configure host and port in the UI sidebar or via `config.py`.
在 UI 侧边栏或通过 `config.py` 配置主机和端口。
* `ma3_osc_host` (Default: `127.0.0.1`)
* `ma3_osc_port` (Default: `8000`)

### LLM API
In the UI sidebar, configure the API Key, Base URL, and Model ID.
在 UI 侧边栏配置 API 密钥、接口地址及模型 ID。

---

## Usage | 使用流程

1.  **Open the web console**: Access via your browser.
    **打开 Web 控制台**: 通过浏览器访问。
2.  **Enter request**: e.g., “Set fixtures 101–105 to red at 50%”.
    **输入需求**: 例如 “将 101 到 105 号灯具设为红色，亮度 50%”。
3.  **LLM Processing**: The app calls the LLM to produce strict JSON.
    **大模型处理**: 应用程序调用大模型生成严格的 JSON 格式指令。
4.  **Preview**: View the pending OSC command strings.
    **预览**: 查看待发送的 OSC 指令字符串。
5.  **Send**: Confirm to send or enable auto-send mode.
    **发送**: 确认发送或开启自动发送模式。

---

## Architecture | 系统架构

1.  **UI (`app.py`)**: Manages input and session state.
    **UI (`app.py`)**: 管理用户输入和会话状态。
2.  **Translator (`src/ai/translator.py`)**: Handles LLM calls and JSON repair.
    **翻译器 (`src/ai/translator.py`)**: 处理大模型调用及 JSON 修复。
3.  **Command Builder**: Converts models into grandMA3 command strings.
    **指令构建器**: 将数据模型转换为 grandMA3 指令字符串。
4.  **OSC Client (`src/osc/osc_client.py`)**: Sends commands to `/cmd` over UDP.
    **OSC 客户端 (`src/osc/osc_client.py`)**: 通过 UDP 将指令发送至 `/cmd`。
5.  **Persistence**: Local storage for settings and history.
    **持久化**: 本地存储配置及历史记录。

---

## Security | 安全提示

* Do **not** commit real API keys to version control.
    请 **不要** 将真实的 API 密钥提交至版本控制系统。
* Cache uses Base64 encoding; for production, use environment variables.
    缓存采用 Base64 编码；生产环境建议使用环境变量。
* Add authentication if the app is exposed to the internet.
    如果暴露在互联网上，请增加身份验证和网络限制。

---

## Contact | 联系方式
Developer / 开发者: `chenhaoyuuu0917@gmail.com`
