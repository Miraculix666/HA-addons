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
    os.makedirs(tmp_path / ".agent" / "docs")
    os.makedirs(tmp_path / ".agent" / "dump" / "inbox", exist_ok=True)

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
        ".agent/docs/CHANGELOG.md",
        ".agent/docs/DEPENDENCIES.md",
        ".agent/docs/TESTS.md",
        ".agent/docs/ARCHITECTURE.md",
        ".agent/docs/SOURCES.md",
        ".agent/dump/README.md"
    ]
    for f in files_to_create:
        Path(tmp_path / f).write_text("mock content")

def test_health_check_all_required_files_exist():
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

        assert "MISSING:" not in result.stdout

def test_health_check_missing_required_files():
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)

        # Remove one required file
        os.remove(tmp_path / "README.md")

        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "MISSING: README.md" in result.stdout
