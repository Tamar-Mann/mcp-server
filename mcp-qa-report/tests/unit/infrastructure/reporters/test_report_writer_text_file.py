import pytest
from pathlib import Path

from infrastructure.reporters.report_writer import write_text_file

import asyncio


@pytest.mark.asyncio
async def test_write_text_file_writes_exact_path_under_project(tmp_path: Path):
    p = await write_text_file(
        project_path=str(tmp_path),
        output_file="out/custom.md",
        text_content="hello",
    )
    assert Path(p).read_text(encoding="utf-8") == "hello"
    assert Path(p) == tmp_path / "out" / "custom.md"


@pytest.mark.asyncio
async def test_write_text_file_blocks_escape(tmp_path: Path):
    with pytest.raises(ValueError):
        await write_text_file(
            project_path=str(tmp_path),
            output_file="../evil.txt",
            text_content="x",
        )
