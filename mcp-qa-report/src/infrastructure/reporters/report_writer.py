"""
Writes QA report artifacts to disk asynchronously.

Supports writing either to a specific file path or to a directory.
Ensures output paths are resolved safely under the project root.
Uses asyncio.to_thread for non-blocking file I/O.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone

@dataclass(frozen=True)
class WriteResult:
    text_path: str | None
    json_path: str | None

def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")

def _safe_resolve_under_project(project_path: str, output_path: str) -> Path:
    root = Path(project_path).resolve()
    candidate = (root / output_path).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("output_path must be inside project_path")
    return candidate

def _write_text_sync(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

def _mkdir_sync(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

async def write_report_files(
    *,
    project_path: str,
    output_dir: str = ".qa-report",
    base_name: str = "qa_report",
    include_timestamp: bool = True,
    write_text: bool,
    write_json: bool,
    text_content: str,
    json_content: str,
) -> WriteResult:
    dir_path = _safe_resolve_under_project(project_path, output_dir)
    await asyncio.to_thread(_mkdir_sync, dir_path)

    suffix = f"_{_timestamp()}" if include_timestamp else ""
    base = dir_path / f"{base_name}{suffix}"

    text_path = None
    json_path = None

    if write_text:
        p = base.with_suffix(".txt")
        await asyncio.to_thread(_write_text_sync, p, text_content)
        text_path = str(p)

    if write_json:
        p = base.with_suffix(".json")
        await asyncio.to_thread(_write_text_sync, p, json_content)
        json_path = str(p)

    return WriteResult(text_path=text_path, json_path=json_path)

async def write_text_file(*, project_path: str, output_file: str, text_content: str) -> str:
    """
    Writes text_content to an explicit file path under project_path asynchronously.
    Blocks escaping outside project_path.
    Returns the written file path as string.
    """
    p = _safe_resolve_under_project(project_path, output_file)
    await asyncio.to_thread(_mkdir_sync, p.parent)
    await asyncio.to_thread(_write_text_sync, p, text_content)
    return str(p)
