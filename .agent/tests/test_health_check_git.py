#!/usr/bin/env python3
"""test_health_check_git.py - Tests for the git status check in health-check.sh"""

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
    os.makedirs(tmp_path / "docs")
    os.makedirs(tmp_path / "dump" / "inbox")
    os.makedirs(tmp_path / ".agent" / "dump" / "inbox")

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

def setup_script(tmp_path):
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"
    shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
    shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

def test_health_check_not_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        setup_script(tmp_path)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "Not a git repository or git not available" in result.stdout

def test_health_check_git_detached_head():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        setup_script(tmp_path)

        subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)

        # Get hash and checkout to detach head
        result_hash = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=tmpdir, check=True)
        commit_hash = result_hash.stdout.strip()
        subprocess.run(["git", "checkout", commit_hash], cwd=tmpdir, check=True, capture_output=True)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        # Check that we detect the detached HEAD correctly
        assert "detached HEAD" in result.stdout
        assert "On a detached HEAD — no branch" in result.stdout

def test_health_check_git_release_branch():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        setup_script(tmp_path)

        subprocess.run(["git", "init", "-b", "release"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "Currently on RELEASE branch" in result.stdout

def test_health_check_git_dev_branch():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        setup_script(tmp_path)

        subprocess.run(["git", "init", "-b", "dev"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "On development branch (dev)" in result.stdout

def test_health_check_git_uncommitted_changes():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        create_mock_repo(tmp_path)
        setup_script(tmp_path)

        subprocess.run(["git", "init", "-b", "main"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)

        # Modify a file
        Path(tmp_path / "README.md").write_text("modified")

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert "Uncommitted changes detected" in result.stdout
