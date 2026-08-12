#!/usr/bin/env python3
"""test_health_check_dump.py - Tests for the dump inbox check in health-check.sh"""

import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def create_mock_repo(tmp_path):
    os.makedirs(tmp_path / ".agent" / "locks")
    os.makedirs(tmp_path / ".agent" / "scripts")
    os.makedirs(tmp_path / ".agent" / "config")
    os.makedirs(tmp_path / ".agent" / "roles")
    os.makedirs(tmp_path / ".agent" / "memory")
    os.makedirs(tmp_path / ".agent" / "dump" / "inbox")
    os.makedirs(tmp_path / "docs")
    os.makedirs(tmp_path / "dump" / "inbox")

    files_to_create = [
        "README.md",
        ".agent/MASTER_INSTRUCTIONS.md",
        ".agent/config/agent.config.md",
        ".agent/config/locking.config.md",
        ".agent/config/branches.config.md",
        ".agent/config/prompts.config.md",
        ".agent/roles/roles.md",
        ".agent/locks/.locked",
        ".agent/locks/HANDOVER.md",
        ".agent/locks/LOCK_REGISTRY.md",
        ".agent/memory/CONTEXT.md",
        ".agent/memory/DECISIONS.md",
        "docs/CHANGELOG.md",
        "docs/DEPENDENCIES.md",
        "docs/TESTS.md",
        "docs/ARCHITECTURE.md",
        "docs/SOURCES.md",
        "dump/README.md"
    ]
    for f in files_to_create:
        Path(tmp_path / f).write_text("mock content")

    Path(tmp_path / ".agent" / "locks" / ".locked").write_text('{"locks": []}')


def test_health_check_empty_dump_inbox():
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)

        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "Dump inbox is empty" in result.stdout
        assert "awaiting processing" not in result.stdout

def test_health_check_non_empty_dump_inbox():
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)

        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        # Create a file in the dump inbox
        (tmp_path / ".agent" / "dump" / "inbox" / "file1.txt").write_text("dump 1")
        (tmp_path / ".agent" / "dump" / "inbox" / "file2.txt").write_text("dump 2")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "Dump inbox has 2 file(s) awaiting processing" in result.stdout
        assert "Run: bash scripts/dump-processor.sh" in result.stdout
        assert "Dump inbox is empty" not in result.stdout
