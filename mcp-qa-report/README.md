# MCP QA Report (Local MCP Server)

A local **Model Context Protocol (MCP)** server that provides a single practical QA tool:

- **`qa_report`** — run sanity and protocol-level checks against an MCP project (this repo *or any other local MCP project*) and return a clear ✅/⚠️/❌ checklist report.

This project was built as an MCP implementation exercise and as a **general-purpose validator**
for quickly checking MCP servers during development, review, or automated validation.

Built with reviewers and coding agents in mind — because checking the same MCP basics over and over adds up.

Intended for MCP developers, reviewers, and tooling authors who want fast, deterministic protocol validation.

---

## What this MCP does

`qa_report()` runs a focused set of **runtime protocol checks**, for example:

- MCP server starts and responds over **STDIO**
- STDIO integrity (no non-JSON noise before `initialize`)
- Tools are registered and discoverable (`tools/list`)
- Tool metadata quality (description presence / minimal quality)
- Optional end-to-end tool invocation smoke test (`tools/call`), when a safe tool is available (e.g. `ping`)

The output is intentionally **a checklist**, not a score — designed for quick human and agent review.

This MCP focuses on **runtime protocol correctness**, not static project structure.

Example output:
```text
[PASS] MCP server starts and responds over stdio
[PASS] Tools are registered and discoverable
[WARN] Tool description is minimal
```

---

## Repository layout

The actual Python package lives under `mcp-qa-report/`:

```text
mcp-qa-report/
  pyproject.toml
  src/
    mcp_server/           # MCP server entrypoint + tool registration
    application/          # orchestration (runner, policies, container)
    domain/               # ports (protocols) + models
    infrastructure/       # checks, process runner, JSON-RPC client, reporters
  tests/                  # unit / integration / e2e
```

### Design highlights

- **Clear separation of concerns** between checks, orchestration, reporting, and stdio/JSON-RPC plumbing
- **Dependency inversion** via protocol-based abstractions (`QACheck`, `Reporter`, `StopPolicy`)
- **Extensible by design** — adding a new check requires implementing `QACheck` and wiring it in `application/container.py`

---

## Requirements

- Python **3.11+**
- Node.js (only for running the MCP Inspector UI)

---

## Environment variables (optional)

This project does **not** require a `.env` file and does not auto-load one.

All configuration can be provided via standard environment variables
(shell, CI, or Inspector configuration).

A tracked `./.env.example` is included **for documentation and future use only**.

```bash
cp .env.example .env
```

> Note: `.env` is **not auto-loaded** by the code.
> `.env.example` exists only as a reference template.
> A loader such as `python-dotenv` can be added explicitly in the future if needed.

### Supported variables

- `LOG_LEVEL` — logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`
- `RUN_INTEGRATION` — enable `@pytest.mark.integration` tests when set to `1`
- `RUN_E2E` — enable `@pytest.mark.e2e` tests when set to `1`

---

## Installation

### Install with uv (recommended)

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

Run the MCP server:

From the project root directory (`mcp-qa-report/`), run:

```bash
uv run python -m mcp_server.server
```

> Alternatively, after installation you may use the script entrypoint:
> `uv run qa-report-mcp`

---

### Install with venv + pip

#### Windows PowerShell
```powershell
cd mcp-qa-report
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .
pip install pytest
```

#### macOS / Linux
```bash
cd mcp-qa-report
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
pip install pytest
```

---

## Run the MCP server (stdio)

```bash
python -m mcp_server.server
```

Logs are written to **stderr** (stdout is reserved for MCP JSON-RPC).
Logging verbosity is controlled via `LOG_LEVEL`.

---

## Use with MCP Inspector

1) Start the Inspector:
```bash
npx @modelcontextprotocol/inspector
```

2) Create a **STDIO** server connection:

- **Command**: `python`
- **Args**: `-m mcp_server.server`
- **Working directory**: the `mcp-qa-report` folder (recommended)

3) Connect, then open **Tools** and call **`qa_report`**.

---

## `qa_report` tool inputs

All tool inputs are exposed via the MCP Inspector UI.

### `project_path` (string, default `"."`)
Path to the target project you want to validate.

### `command` (array of strings, optional)
Explicit start command for the target MCP server.

Auto-detection is attempted (best-effort) in the following order:
1) `.vscode/mcp.json` or `mcp.json`
2) `pyproject.toml` scripts
3) `package.json` scripts

Providing an explicit command is recommended for full reliability.

### `fail_fast` (bool, default `true`)
Stop on first failure if true.

### `output_path` (string, optional)
If provided, writes the report under `project_path`; otherwise returns the report inline.  
Paths are validated to prevent escaping outside `project_path`.

**Safety:** paths are forced to stay **under `project_path`** (escaping with `../` is blocked).

For detailed parameter behavior and edge cases, see the `qa_report` tool description exposed via MCP.

---

## Tests

This project uses **pytest** and groups tests into three levels:

- **Unit tests** — fast tests without subprocesses (default)
- **Integration tests** — real MCP server subprocess, core protocol calls
- **E2E tests** — full `tools/call` invocation flow (e.g. `ping`)

Run unit tests:
```bash
pytest -q
```

Run integration tests:
```bash
RUN_INTEGRATION=1 pytest -q -m integration
```

Run E2E tests:
```bash
RUN_E2E=1 pytest -q -m e2e
```

By default, integration and e2e tests are skipped unless explicitly enabled via environment variables.

---

## Concurrency & scalability note

This MCP server is intentionally implemented in a **synchronous** style.

The primary use-case is local, on-demand validation where simplicity,
debuggability, and deterministic behavior are preferred over throughput.

If higher throughput is required in the future, the design allows:
- migrating process handling and JSON-RPC I/O to asyncio
- running checks concurrently
- isolating checks into worker processes

---

## Possible future extensions

The current scope is intentionally limited to runtime MCP protocol validation.

Possible future extensions include:
- README / documentation presence and structure checks
- Deeper validation of tool input schemas
- Optional performance or startup-time checks

---

## Verification

Detailed Codex and MCP Inspector validation scenarios are documented in **VERIFICATION.md**.
