#!/usr/bin/env python3
"""test_lock_manager.py - Tests for the lock-manager.sh script"""

import pytest
import subprocess
import json
import os
import shutil
import tempfile
from pathlib import Path

def test_lock_manager_lock_validation():
    # To test the bash function `cmd_lock()`, we can just call it via bash.
    script_path = Path(__file__).parent.parent / "scripts" / "lock-manager.sh"

    # We create a temporary environment
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create expected directory structure
        os.makedirs(tmp_path / ".agent" / "locks")
        os.makedirs(tmp_path / ".agent" / "scripts")

        # Copy script to the temporary directory so its REPO_ROOT points to tmpdir
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "lock-manager.sh")
        colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        lock_file.write_text('{"locks": []}')

        # In the script, it relies on being run from the current working directory because
        # of how python opens `.agent/locks/.locked`.
        # So we MUST change the cwd to the temp directory when running subprocess.

        # Test invalid lock type
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "INVALID", "agent1", "reason"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Invalid lock type: INVALID" in result.stdout

        # Test valid lock type
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "SOFT", "agent1", "reason"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Lock acquired" in result.stdout

        # Verify the lock file
        data = json.loads(lock_file.read_text())
        assert len(data["locks"]) == 1
        assert data["locks"][0]["file_or_folder"] == "test/path"
        assert data["locks"][0]["type"] == "SOFT"
        assert data["locks"][0]["locked_by"] == "agent1"
        assert data["locks"][0]["reason"] == "reason"


def test_lock_manager_lock_conflicts():
    script_path = Path(__file__).parent.parent / "scripts" / "lock-manager.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agent" / "locks")
        os.makedirs(tmp_path / ".agent" / "scripts")
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "lock-manager.sh")
        colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"

        # Test conflict with HARD lock
        lock_file.write_text(json.dumps({
            "locks": [{
                "id": "lock-hard1",
                "file_or_folder": "test/path",
                "type": "HARD",
                "locked_by": "human"
            }]
        }))
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "SOFT", "agent1", "reason"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "HARD lock on test/path \u2014 cannot acquire" in result.stdout

        # Test conflict with SOFT lock from another agent
        lock_file.write_text(json.dumps({
            "locks": [{
                "id": "lock-soft1",
                "file_or_folder": "test/path",
                "type": "SOFT",
                "locked_by": "agent2"
            }]
        }))
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "SOFT", "agent1", "reason"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "File locked by agent2" in result.stdout

def test_lock_manager_invalid_arguments():
    script_path = Path(__file__).parent.parent / "scripts" / "lock-manager.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agent" / "locks")
        os.makedirs(tmp_path / ".agent" / "scripts")
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "lock-manager.sh")
        colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        lock_file.write_text('{"locks": []}')

        # Missing reason
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "SOFT", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Lock Manager \u2014 Usage" in result.stdout

def test_lock_manager_status():
    script_path = Path(__file__).parent.parent / "scripts" / "lock-manager.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agent" / "locks")
        os.makedirs(tmp_path / ".agent" / "scripts")
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "lock-manager.sh")
        colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"

        # Test status with no locks
        lock_file.write_text(json.dumps({
            "locks": [],
            "last_updated": "2023-10-27T10:00:00+00:00"
        }))

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "status"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Current Lock State" in result.stdout
        assert "No active locks" in result.stdout
        assert "Last updated: 2023-10-27T10:00:00+00:00" in result.stdout

        # Test status with active locks
        lock_file.write_text(json.dumps({
            "locks": [
                {
                    "id": "lock-hard1",
                    "file_or_folder": "test/hard/path",
                    "type": "HARD",
                    "locked_by": "human",
                    "expires_at": "never"
                },
                {
                    "id": "lock-soft1",
                    "file_or_folder": "test/soft/path",
                    "type": "SOFT",
                    "locked_by": "agent1",
                    "expires_at": "2099-12-31T23:59:59+00:00"
                }
            ],
            "last_updated": "2023-10-27T10:05:00+00:00"
        }))

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "status"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Current Lock State" in result.stdout
        assert "ID" in result.stdout
        assert "Type" in result.stdout
        assert "File" in result.stdout
        assert "Agent" in result.stdout
        assert "Expires" in result.stdout

        # Check if lock details are present
        assert "lock-hard1" in result.stdout
        assert "test/hard/path" in result.stdout
        assert "HARD" in result.stdout
        assert "human" in result.stdout

        assert "lock-soft1" in result.stdout
        assert "test/soft/path" in result.stdout
        assert "SOFT" in result.stdout
        assert "agent1" in result.stdout
        assert "2099-12-31T23:59:59+00:00" in result.stdout

        assert "Last updated: 2023-10-27T10:05:00+00:00" in result.stdout
