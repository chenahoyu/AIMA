# AI‑MA (v0.5) — Natural‑language grandMA3 OSC Assistant

AI‑MA is a Streamlit-based web console that turns natural-language lighting requests into structured commands and sends them to **grandMA3** via **OSC/UDP** (`/cmd`).

This README describes the **`backup/v0.5/`** snapshot.

## Features

- **Chat-style UI** built with Streamlit (`app.py`)
- **Natural language → JSON → grandMA3 commands**
- **OSC sender** with command sanitization and small inter-command delay for stability
- **Conversation persistence** (local JSON)
- **Local caching** for API key / base URL / model id and UI preferences (local JSON)
- **CLI launcher** with language selection + IP/port prompts + environment checks (`scripts/launcher.py`)
- **Network modes for API calls**: direct, system proxy, env SOCKS5, custom proxy
- **Global UI language switching** (ZH/EN/JA) for the console UI
- **Static Chinese developer doc (HTML)** for offline handoff (`docs/开发文档.html`)

## Tech stack

- **Python**: 3.9+ recommended (3.10+ preferred)
- **UI**: Streamlit
- **LLM**: OpenAI Python SDK (OpenAI-compatible Chat Completions endpoint)
- **HTTP**: `httpx` (with SOCKS support)
- **Models**: Pydantic v2
- **OSC**: `python-osc`
- **Dev**: `pytest`, `black`, `flake8`

See `requirements.txt` for pinned versions.

## Getting started

### Prerequisites

- Python 3.9+ (3.10+ preferred)
- macOS/Linux shell (examples use POSIX paths)

### Install

From `backup/v0.5/`:

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

### Run (local)

```bash
./venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
```

Open:

- `http://127.0.0.1:8502`

### Run via CLI launcher (recommended)

The launcher guides you through:

1. Choose UI language (ZH/EN/JA)
2. Enter server IP and port
3. Environment checks (Python version, required deps)
4. Start Streamlit bound to your chosen address/port

If your system Python does not have Streamlit installed, run the launcher using the project venv:

```bash
/Users/chenhaoyu/AI-MA/venv/bin/python backup/v0.5/scripts/launcher.py
```

## Configuration

### grandMA3 OSC

Configure host/port in the UI sidebar (OSC settings) or via defaults in `config.py`:

- `ma3_osc_host` (default `127.0.0.1`)
- `ma3_osc_port` (default `8000`)

### LLM API (OpenAI-compatible)

In the UI sidebar (API settings), configure:

- API Key
- API Base URL (expects an OpenAI-compatible base URL; the app builds `/chat/completions` as needed)
- Model ID

The UI also provides an **API availability check** to return actionable diagnostics (HTTP status, proxy issues, etc.).

### Local cache and persistence

This snapshot stores local runtime data under `src/`:

- API/cache: `src/.api_cache/api_keys.json`
- Conversations: `src/.conversations/conversations.json`

## Usage

1. Open the web console.
2. Enter a natural-language lighting request (e.g. “Set fixtures 101–105 to red at 50%”).
3. The app calls the LLM to produce **strict JSON** (with an `actions` list).
4. The app builds OSC command strings and shows a **pending send** preview.
5. Confirm to send (or enable auto-send).

## Architecture

High-level flow:

1. **UI** (`app.py`) collects user input and manages session state.
2. **Translator** (`src/ai/translator.py`) calls the LLM and returns a `GMA3Command` model.
3. **Command builder** (`app.py`) converts the model into grandMA3 command strings.
4. **OSC client** (`src/osc/osc_client.py`) sends each command to `/cmd` over UDP.
5. **Persistence** (`src/utils/*.py`) stores conversations and cached settings locally.

## File structure (v0.5)

```text
backup/v0.5/
├─ app.py                      # Streamlit UI + orchestration (chat, OSC/API settings, i18n, caching)
├─ app_simple.py               # Simplified/older variant (reference)
├─ app_modern.py               # Modern UI experiment (reference)
├─ app_complete.py             # Complete/experiment variant (reference)
├─ config.py                   # Pydantic settings (defaults)
├─ requirements.txt            # Pinned dependencies
├─ scripts/
│  ├─ launcher.py              # CLI launcher (language → IP/port → checks → start Streamlit)
│  └─ ai-ma-toggle.command      # Double-clickable toggle (macOS) for a fixed port (reference)
├─ .streamlit/
│  └─ config.toml              # Streamlit theme config
├─ src/
│  ├─ ai/
│  │  ├─ models.py             # Pydantic models (GMA3Command, actions, etc.)
│  │  └─ translator.py         # LLM client + JSON extraction/repair
│  ├─ osc/
│  │  └─ osc_client.py         # OSC sender (sanitization + delay)
│  ├─ utils/
│  │  ├─ api_key_cache.py      # Local cache (Base64 encoding + chmod 600)
│  │  └─ conversation_manager.py# Local conversation store (JSON)
│  ├─ .api_cache/
│  │  └─ api_keys.json         # Runtime cache file (do not commit secrets)
│  └─ .conversations/
│     └─ conversations.json    # Runtime conversation store
├─ data/                       # Fixtures/presets/sequences/knowledge_base (project data)
└─ docs/
   └─ 开发文档.html             # Static Chinese developer documentation (HTML)
```

## Development

### Formatting

```bash
./venv/bin/python -m black .
./venv/bin/python -m flake8 .
```

### Tests

```bash
./venv/bin/python -m pytest -q
```

## Deployment notes

For server deployments (example):

```bash
./venv/bin/python -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 8502 \
  --server.headless true
```

Put the app behind a reverse proxy (Nginx/Caddy) for **TLS** and access control.

## Security

- Do **not** commit real `.env` or API keys.
- Current cache uses Base64 encoding (not strong encryption). For production/public deployments, prefer environment variables or a secret manager.
- If exposed to the internet, add authentication and network restrictions.

## Contributing

Issues and PRs are welcome. Keep changes small and focused, and include a brief test plan in PR descriptions.

## License

No license is included in this snapshot. If you plan to open-source it, add a `LICENSE` file (e.g., MIT/Apache-2.0) and update this section accordingly.

## Contact

Developer: `chenhaoyuuu0917@gmail.com`

