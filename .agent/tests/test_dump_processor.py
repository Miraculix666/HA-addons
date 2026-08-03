import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def setup_mock_env(tmp_path):
    # Based on the script's REPO_ROOT definition:
    # REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    # If the script is placed at {tmp_path}/.agent/scripts/dump-processor.sh
    # then REPO_ROOT evaluates to {tmp_path}/.agent.
    # So the script looks for INBOX at {tmp_path}/.agent/dump/inbox
    # We must construct the directories where the script expects them.
    os.makedirs(tmp_path / ".agent" / "scripts")
    os.makedirs(tmp_path / ".agent" / "dump" / "inbox")
    os.makedirs(tmp_path / ".agent" / "dump" / "processed")
    os.makedirs(tmp_path / ".agent" / "config")

    script_path = Path(".agent/scripts/dump-processor.sh").absolute()
    colors_path = Path(".agent/scripts/colors.sh").absolute()

    shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
    shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

    # Create mock prompts.config.md
    (tmp_path / ".agent" / "config" / "prompts.config.md").write_text("Mock prompts config")

def test_dump_processor_empty_inbox():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_env(tmp_path)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert result.returncode == 0
        assert "Dump inbox is empty" in result.stdout

def test_dump_processor_auto_list_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_env(tmp_path)

        # Create a mock file in the inbox
        (tmp_path / ".agent" / "dump" / "inbox" / "test_file.txt").write_text("Hello World")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--auto-list"],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert result.returncode == 0
        assert "Running in --auto-list mode" in result.stdout
        assert "test_file.txt" in result.stdout

def test_dump_processor_process_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        setup_mock_env(tmp_path)

        # Create a mock file in the inbox
        (tmp_path / ".agent" / "dump" / "inbox" / "test_file.txt").write_text("Hello World")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--process"],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert result.returncode == 0
        assert "Processing mode active..." in result.stdout
        assert "test_file.txt" in result.stdout
        assert "Staged to:" in result.stdout

        # Verify the file was created in the processed directory
        processed_files = list((tmp_path / ".agent" / "dump" / "processed").glob("*test_file*-processed-*.md"))
        assert len(processed_files) == 1

        content = processed_files[0].read_text()
        assert "DUMP ANALYSIS \u2014 test_file.txt" in content
        assert "Hello World" in content
