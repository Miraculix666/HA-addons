import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def setup_mock_repo(tmp_path: Path):
    os.makedirs(tmp_path / ".agent" / "scripts")
    repo_root = Path(__file__).parent.parent.parent
    script_path = repo_root / ".agent" / "scripts" / "dump-processor.sh"
    colors_path = repo_root / ".agent" / "scripts" / "colors.sh"

    shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
    shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

    os.makedirs(tmp_path / "dump" / "inbox")
    os.makedirs(tmp_path / "dump" / "processed")

def test_empty_inbox():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_repo(tmp_path)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Dump inbox is empty" in result.stdout

def test_files_inbox():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_repo(tmp_path)

        (tmp_path / "dump" / "inbox" / "test_file.txt").write_text("dummy content")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Found 1 file(s)" in result.stdout
        assert "test_file.txt" in result.stdout
        assert "HUMAN CONFIRMATION REQUIRED" in result.stdout

def test_auto_list_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_repo(tmp_path)

        (tmp_path / "dump" / "inbox" / "file1.txt").write_text("content 1")
        (tmp_path / "dump" / "inbox" / "file2.txt").write_text("content 2")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--auto-list"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Found 2 file(s)" in result.stdout
        assert "file1.txt" in result.stdout
        assert "file2.txt" in result.stdout
        assert "Running in --auto-list mode" in result.stdout

def test_process_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_repo(tmp_path)

        (tmp_path / "dump" / "inbox" / "code.py").write_text("print('hello')")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--process"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Processing mode active" in result.stdout
        assert "Staged to:" in result.stdout

        processed_files = list((tmp_path / "dump" / "processed").glob("*"))
        assert len(processed_files) == 1
        processed_content = processed_files[0].read_text()

        assert "DUMP ANALYSIS — code.py" in processed_content
        assert "print('hello')" in processed_content
