from __future__ import annotations
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

def write_report_files(
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
    dir_path.mkdir(parents=True, exist_ok=True)

    suffix = f"_{_timestamp()}" if include_timestamp else ""
    base = dir_path / f"{base_name}{suffix}"

    text_path = None
    json_path = None

    if write_text:
        p = base.with_suffix(".txt")
        p.write_text(text_content, encoding="utf-8")
        text_path = str(p)

    if write_json:
        p = base.with_suffix(".json")
        p.write_text(json_content, encoding="utf-8")
        json_path = str(p)

    return WriteResult(text_path=text_path, json_path=json_path)

def write_text_file(*, project_path: str, output_file: str, text_content: str) -> str:
    """
    Writes text_content to an explicit file path under project_path.
    Blocks escaping outside project_path.
    Returns the written file path as string.
    """
    p = _safe_resolve_under_project(project_path, output_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text_content, encoding="utf-8")
    return str(p)
