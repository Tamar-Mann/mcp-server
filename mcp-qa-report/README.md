# MCP QA Report (Local MCP Server)

A local **Model Context Protocol (MCP)** server that provides a single practical tool:

- **`qa_report`** — run sanity checks against an MCP project (this repo *or any other local MCP project*) and return a clear ✅/⚠️/❌ checklist report.

This project was built as an MCP implementation exercise and as a **general-purpose validator** for quickly checking local MCP servers during development or review.

Built with reviewers in mind — because checking the same basics over and over adds up. `qa_report` packages the essentials into a quick checklist :)

---

## What this MCP does

`qa_report()` runs a small battery of protocol-level checks, for example:

- Server starts and responds over **STDIO**
- STDIO integrity (no noise before `initialize`)
- Tools are registered and discoverable (`tools/list`)
- Tool metadata quality (description presence/quality)
- Optional end-to-end tool invocation smoke test (`tools/call`), when a safe tool is available (e.g. `ping`)

The output is intentionally **a checklist**, not a score.

---

## Repository layout

The actual Python package lives under `mcp-qa-report/`:

```text
mcp-qa-report/
  pyproject.toml
  src/
    mcp_server/           # MCP server entrypoint + tools
    application/          # orchestration (runner, policies)
    domain/               # ports + models
    infrastructure/       # checks, process runner, json-rpc client, reporters
  tests/                  # unit / integration / e2e
```

Design highlights (clean layering, kept lightweight):

- **SRP**: checks, runner, reporters, and process/JSON-RPC plumbing are separated.
- **Dependency inversion**: the runner depends on `QACheck` / `Reporter` protocols; infrastructure implements them.
- **Extensible**: add a new check by implementing `QACheck` and wiring it in `application/container.py`.

---

## Requirements

- Python **3.11+**
- Node.js (only for running the Inspector UI)

---

## Environment variables (optional)

This project does **not** require a `.env` file.  
All settings are optional and can be provided as regular environment variables in your shell / CI.

If you want a simple starting point for future use, keep a tracked `./.env.example` file
and copy it locally to `.env` (do **not** commit `.env`):

```bash
cp .env.example .env
```

> Note: the code does not auto-load `.env`.
> `.env.example` is tracked only as documentation and a future-friendly template (for local dev/CI).  
> To use it, export the variables in your shell/CI (or later add a loader like `python-dotenv`).

### Supported variables

- `LOG_LEVEL` — controls logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`
- `RUN_INTEGRATION` — when set to `1`, enables `@pytest.mark.integration` tests (default: skipped)
- `RUN_E2E` — when set to `1`, enables `@pytest.mark.e2e` tests (default: skipped)

---

## Install with uv (recommended)

```bash
cd mcp-qa-report
uv venv
# Windows PowerShell:
#   .\.venv\Scripts\Activate.ps1
# macOS/Linux:
#   source .venv/bin/activate

uv pip install -e .
uv pip install --group dev
```

Run the server:

```bash
uv run python -m mcp_server.server
```

> If you prefer, after install you can also run the script entrypoint:
> `uv run qa-report-mcp`

---

## Install (venv + pip)

### Windows PowerShell
```powershell
cd mcp-qa-report
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
pip install pytest
```

### macOS / Linux (bash/zsh)
```bash
cd mcp-qa-report
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
pip install pytest
```

> Alternative (no install): you can run by setting `PYTHONPATH=src` so Python can import `mcp_server/`. Editable install is still the cleanest approach to avoid import issues.

---

## Run the MCP server (stdio)

After installation, run:

```bash
python -m mcp_server.server
```

The server logs to **stderr** (so it does not break MCP stdio JSON-RPC traffic).  
You can control log verbosity via `LOG_LEVEL` (e.g. `LOG_LEVEL=DEBUG`).

---

## Use with MCP Inspector

1) Start the Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2) In the Inspector UI, create a **STDIO** server connection:

- **Command**: `python`
- **Args**: `-m mcp_server.server`
- **Working directory**: point it to the `mcp-qa-report` folder (recommended)

3) Connect, then open **Tools** and call **`qa_report`**.

---

## `qa_report` inputs

### `project_path` (string, default `"."`)
Path to the target project you want to validate.  
`"."` means “the server process working directory”.

### `command` (array of strings, optional)
How to start the **target** MCP server you are checking.

- If provided, this is **highest priority** and will be used as-is.
- If omitted / `null`, the tool auto-detects a start command using (in order):
  1) `.vscode/mcp.json` or `mcp.json` (`servers` or `mcpServers`) — prefers an entry with `"type": "stdio"` if present, otherwise uses the first one.
  2) `pyproject.toml` scripts — picks a likely entrypoint and runs it via the current Python interpreter.
  3) `package.json` scripts — uses `npm run start` (or `npm run dev` as a fallback).

### `fail_fast` (bool, default `true`)
- `true`: stop on first ❌ (faster).
- `false`: run all checks and aggregate results.

### `output_path` (string, optional)
Controls whether the report is returned **as text** or **written to disk**.

- If **omitted / `null`** → the tool returns the report text (no files written).
- If provided but **empty/whitespace** → treated like omitted (`null`) and returns text.
- If provided and non-empty:
  - **Directory mode** (either ends with `/` or `\`, **or** has **no suffix/extension**)  
    Writes `qa_report.txt` inside that directory (under `project_path`).  
    Examples: `out/`, `out\`, `out`
  - **File mode** (has a suffix/extension, and does **not** end with a slash)  
    Writes exactly to that file path (under `project_path`).  
    Example: `out/report.md`

**Note:** “no suffix/extension” means that `output_path="out"` is treated as a directory, not a file. If you want a file, give it an extension (e.g. `out/report.txt`).

**Safety:** paths are forced to stay **under `project_path`** (escaping with `../` is blocked).

---

## Tests

This project uses **pytest** and groups tests into three levels:

- **Unit tests** (default): fast tests that do not spawn subprocesses.
- **Integration tests** (`@pytest.mark.integration`): start a real MCP server subprocess and validate core protocol calls (`initialize`, `tools/list`).
- **E2E tests** (`@pytest.mark.e2e`): start a real MCP server subprocess and validate end-to-end tool invocation (`tools/call`, e.g. `ping`).

### Run unit tests (default)
```bash
pytest -q
```

### Run integration tests
PowerShell:
```powershell
$env:RUN_INTEGRATION="1"
pytest -q -m integration
Remove-Item Env:RUN_INTEGRATION -ErrorAction SilentlyContinue
```

bash/zsh:
```bash
RUN_INTEGRATION=1 pytest -q -m integration
```

### Run E2E tests
PowerShell:
```powershell
$env:RUN_E2E="1"
pytest -q -m e2e
Remove-Item Env:RUN_E2E -ErrorAction SilentlyContinue
```

bash/zsh:
```bash
RUN_E2E=1 pytest -q -m e2e
```

### Notes
- By default, integration and e2e tests are skipped unless the corresponding environment variable is set.
- To see which tests were skipped and why:
```bash
pytest -q -rs
```

---

## Extending the checks

Add a new check by implementing `QACheck` (see `domain/ports.py`) and wiring it into `application/container.py`.

Ideas:
- Verify README presence and required sections (run/install/Inspector/examples)
- Verify tool `inputSchema` structure more strictly
- Add optional lint/format checks (kept separate from protocol checks)
- Export JSON report alongside text output

---

## License

MIT (or your preferred license).
