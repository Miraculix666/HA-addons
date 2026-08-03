#!/usr/bin/env python3
"""test_dump_processor.py - Tests for the dump-processor.sh script"""

import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def create_mock_repo(tmp_path):
    os.makedirs(tmp_path / ".agent" / "scripts")
    os.makedirs(tmp_path / ".agent" / "dump" / "inbox")
    os.makedirs(tmp_path / ".agent" / "dump" / "processed")

def test_dump_processor_empty():
    script_path = Path(__file__).parent.parent / "scripts" / "dump-processor.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Dump inbox is empty" in result.stdout

def test_dump_processor_no_args_with_files():
    script_path = Path(__file__).parent.parent / "scripts" / "dump-processor.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        test_file = tmp_path / ".agent" / "dump" / "inbox" / "test_snippet.js"
        test_file.write_text("console.log('hello');")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Found 1 file(s) in dump/inbox/" in result.stdout
        assert "HUMAN CONFIRMATION REQUIRED" in result.stdout

def test_dump_processor_auto_list():
    script_path = Path(__file__).parent.parent / "scripts" / "dump-processor.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        test_file = tmp_path / ".agent" / "dump" / "inbox" / "test_snippet.js"
        test_file.write_text("console.log('hello');")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--auto-list"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Found 1 file(s) in dump/inbox/" in result.stdout
        assert "test_snippet.js" in result.stdout
        assert "--auto-list mode" in result.stdout

def test_dump_processor_process():
    script_path = Path(__file__).parent.parent / "scripts" / "dump-processor.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "dump-processor.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        test_file = tmp_path / ".agent" / "dump" / "inbox" / "test_snippet.js"
        test_file.write_text("console.log('hello');")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "dump-processor.sh"), "--process"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Processing mode active" in result.stdout

        processed_files = list((tmp_path / ".agent" / "dump" / "processed").glob("*"))
        assert len(processed_files) == 1
        processed_file = processed_files[0]

        assert "test_snippet-processed-" in processed_file.name
        content = processed_file.read_text()
        assert "DUMP ANALYSIS \u2014 test_snippet.js" in content
        assert "console.log('hello');" in content
