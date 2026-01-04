import pytest
from pathlib import Path

from infrastructure.reporters.report_writer import write_report_files


def test_write_report_files_creates_files_under_project(tmp_path: Path):
    r = write_report_files(
        project_path=str(tmp_path),
        output_dir=".qa-report",
        base_name="qa_report",
        include_timestamp=False,
        write_text=True,
        write_json=True,
        text_content="hello",
        json_content='{"x":1}',
    )
    assert r.text_path and r.json_path
    assert Path(r.text_path).read_text(encoding="utf-8") == "hello"
    assert Path(r.json_path).read_text(encoding="utf-8") == '{"x":1}'


def test_write_report_files_blocks_escape(tmp_path: Path):
    with pytest.raises(ValueError):
        write_report_files(
            project_path=str(tmp_path),
            output_dir="../evil",
            base_name="x",
            include_timestamp=False,
            write_text=True,
            write_json=False,
            text_content="x",
            json_content="",
        )
