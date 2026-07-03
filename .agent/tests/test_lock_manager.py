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
        shutil.copy(Path(__file__).parent.parent / "scripts" / "colors.sh", tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        registry_file = tmp_path / ".agent" / "locks" / "LOCK_REGISTRY.md"
        registry_file.write_text("")
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
        shutil.copy(Path(__file__).parent.parent / "scripts" / "colors.sh", tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        registry_file = tmp_path / ".agent" / "locks" / "LOCK_REGISTRY.md"
        registry_file.write_text("")

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
        shutil.copy(Path(__file__).parent.parent / "scripts" / "colors.sh", tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        registry_file = tmp_path / ".agent" / "locks" / "LOCK_REGISTRY.md"
        registry_file.write_text("")
        lock_file.write_text('{"locks": []}')

        # Missing reason
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "lock", "test/path", "SOFT", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Lock Manager \u2014 Usage" in result.stdout

def test_lock_manager_release():
    script_path = Path(__file__).parent.parent / "scripts" / "lock-manager.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.makedirs(tmp_path / ".agent" / "locks")
        os.makedirs(tmp_path / ".agent" / "scripts")
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "lock-manager.sh")
        shutil.copy(Path(__file__).parent.parent / "scripts" / "colors.sh", tmp_path / ".agent" / "scripts" / "colors.sh")

        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        registry_file = tmp_path / ".agent" / "locks" / "LOCK_REGISTRY.md"
        registry_file.write_text("")

        # Create a mock lock file
        initial_locks = {
            "locks": [
                {
                    "id": "lock-soft1",
                    "file_or_folder": "test/path1",
                    "type": "SOFT",
                    "locked_by": "agent1",
                    "locked_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "lock-hard1",
                    "file_or_folder": "test/path2",
                    "type": "HARD",
                    "locked_by": "human",
                    "locked_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
        lock_file.write_text(json.dumps(initial_locks))

        # Test successful release
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "release", "lock-soft1", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
        assert "Lock lock-soft1 released and logged to registry" in result.stdout

        # Verify lock was removed
        data = json.loads(lock_file.read_text())
        assert len(data["locks"]) == 1
        assert data["locks"][0]["id"] == "lock-hard1"

        # Verify registry entry
        registry_content = registry_file.read_text()
        assert "Lock ID | lock-soft1" in registry_content
        assert "Released by agent1" in registry_content

        # Test release non-existent lock
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "release", "lock-nonexistent", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Lock lock-nonexistent not found" in result.stdout

        # Test release HARD lock
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "release", "lock-hard1", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Cannot release HARD lock \u2014 requires human" in result.stdout

        # Test release lock owned by different agent
        lock_file.write_text(json.dumps({
            "locks": [
                {
                    "id": "lock-soft2",
                    "file_or_folder": "test/path3",
                    "type": "SOFT",
                    "locked_by": "agent2",
                    "locked_at": "2024-01-01T00:00:00Z"
                }
            ]
        }))
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "lock-manager.sh"), "release", "lock-soft2", "agent1"],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1
        assert "Lock owned by agent2 \u2014 use handover protocol" in result.stdout
