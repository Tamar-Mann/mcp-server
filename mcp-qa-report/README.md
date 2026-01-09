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
- uv
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

All commands below assume you are inside the project directory (`mcp-qa-report/`).

This project requires **[uv](https://docs.astral.sh/uv/)**.

```bash
cd mcp-qa-report
uv sync
uv pip install -e .
```

## Run the MCP Server (STDIO)

Always use `uv run` to ensure dependencies are loaded.

**Bash:**

```bash
uv run python -m mcp_server.server
```

---

## Use with MCP Inspector

1) Start the Inspector: `npx @modelcontextprotocol/inspector`

2) Create a **STDIO** server connection:
   - **Command**: `uv`
   - **Args**: `run`, `python`, `-m`, `mcp_server.server`
   - **Working directory**: [Absolute path to your mcp-qa-report folder]

3) Connect and open **Tools** to run `qa_report`.

---

## `qa_report` tool inputs

All tool inputs are exposed via the MCP Inspector UI.

### `project_path` (string, default `"."`)
Path to the target project you want to validate.

### `command` (array of strings, optional)
Explicit start command for the target MCP server.

**Internal Logic:**
If omitted, auto-detection is attempted. For Python projects, the tool **automatically wraps commands with `uv run`**. This ensures the target server runs in its own environment without conflicting with the QA tool.

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

Run the test suite using **uv** (standard across Windows, macOS, and Linux).

### Unit Tests (Fast)

```bash
uv run pytest tests/unit
```

### Integration & E2E Tests

To run the full test suite, you must explicitly enable the environment variables.

**Windows (PowerShell):**

```powershell
$env:RUN_INTEGRATION=1
$env:RUN_E2E=1
uv run pytest .
```

**macOS / Linux (Bash):**

```bash
RUN_INTEGRATION=1 RUN_E2E=1 uv run pytest .
```

> **Note:**  
> By default, integration and end-to-end tests are skipped to ensure fast feedback during development.

---

## Concurrency & Performance

This MCP server is fully **Asynchronous**, built on top of `asyncio`.

- **Non-blocking I/O:** The server manages target MCP processes using asynchronous subprocess calls, ensuring the main loop remains responsive.
- **Concurrent Checks:** Checks are executed asynchronously, with a fail-fast policy applied by default for deterministic feedback.  
  The architecture fully supports concurrent execution via alternative policies.
- **Async Resource Management:** Proper cleanup of subprocesses and streams is handled via async context managers.

---

The roadmap below outlines possible future directions and is not required for the current validation scope.

## Future Roadmap

The roadmap aims to evolve this tool from a local validator into a comprehensive **MCP Quality Gate**, aligning with the requirements for robust AI coding agent tooling:

### 1. Deep Validation & Intelligence (Core)
- **AI-Powered Semantic Auditing:** Integrating LLMs to verify that tool descriptions are not just present, but semantically optimized for Agentic reasoning (ensuring agents like Claude Code or Cursor know exactly when to trigger a tool).
- **Security Sandboxing:** Runtime monitoring to detect unauthorized file system access or suspicious network activity by target MCP servers.
- **Performance Benchmarking:** Measuring startup latency and resource consumption to ensure MCPs don't slow down the agent's context loop.

### 2. Ecosystem & Enterprise Operations (Integrations)
- **Nebius AI Infrastructure Integration:** Automated deployment and validation of MCP servers on Nebius AI cloud environments, leveraging GPU-accelerated infrastructure for high-performance AI tools.
- **Automated Scheduling:** Integration with **Google Calendar** or Cron services to trigger periodic health checks for production-grade MCP servers, ensuring 24/7 reliability for critical tools.
- **CI/CD GitHub Action:** A dedicated action to enforce protocol compliance automatically during the build process, preventing broken MCPs from reaching the team's coding agents.

---

## Verification

Detailed Codex and MCP Inspector validation scenarios are documented in **VERIFICATION.md**.
