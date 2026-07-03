#!/usr/bin/env python3
"""test_health_check.py - Tests for the health-check.sh script"""

import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def test_health_check_required_files():
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create expected directory structure
        os.makedirs(tmp_path / ".agent" / "scripts")

        # Copy scripts to the temporary directory
        shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
        shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

        # We need to create dummy files for the REQUIRED_FILES in health-check.sh
        required_files = [
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

        # Test 1: Missing required files
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 1 # Expecting failure due to missing files
        assert "MISSING: README.md" in result.stdout

        # Create all required files
        for f in required_files:
            file_path = tmp_path / f
            os.makedirs(file_path.parent, exist_ok=True)
            file_path.touch()

        # Also need a valid locks file for the other checks to not completely fail
        lock_file = tmp_path / ".agent" / "locks" / ".locked"
        lock_file.write_text('{"locks": []}')

        # Context file for consolidation check
        context_file = tmp_path / ".agent" / "memory" / "CONTEXT.md"
        context_file.write_text("Sessions Since Last Consolidation Review: 1")

        # Header fields in docs
        for doc in ["docs/CHANGELOG.md", "docs/DEPENDENCIES.md", "docs/TESTS.md"]:
            doc_path = tmp_path / doc
            doc_path.write_text("# LAST MODIFIED")

        # Create dump/inbox dir to avoid errors
        os.makedirs(tmp_path / "dump" / "inbox", exist_ok=True)

        # Note: git repo tests are skipped if not a git repo, which is fine

        # Test 2: All files exist
        result2 = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        # Should contain check marks for the required files
        assert "✅ README.md" in result2.stdout
        assert "✅ .agent/MASTER_INSTRUCTIONS.md" in result2.stdout
        # The script checks pass and fail counts at the end to exit 0 or 1
        # Since this test is only about required files, we don't assert return code 0 here
        # because other checks might fail (like git repo checks).
        # We just verify the required files section.
