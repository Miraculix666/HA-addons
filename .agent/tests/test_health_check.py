import pytest
import subprocess
import os
import shutil
import tempfile
from pathlib import Path

def setup_mock_repo(tmp_path):
    # Mocking structure so the health check can execute without unrelated file-not-found errors
    os.makedirs(tmp_path / ".agent" / "scripts")
    os.makedirs(tmp_path / ".agent" / "locks")
    os.makedirs(tmp_path / ".agent" / "memory")

    # Copy the script and colors.sh
    script_path = Path(__file__).parent.parent / "scripts" / "health-check.sh"
    colors_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    shutil.copy(script_path, tmp_path / ".agent" / "scripts" / "health-check.sh")
    shutil.copy(colors_path, tmp_path / ".agent" / "scripts" / "colors.sh")

    lock_file = tmp_path / ".agent" / "locks" / ".locked"
    return lock_file

def test_health_check_valid_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        lock_file = setup_mock_repo(tmp_path)

        # Write valid JSON
        lock_file.write_text('{"locks": []}')

        # Execute health-check.sh to see if it correctly prints the validation message
        # Since health-check.sh ALREADY prints ".locked is valid JSON" if it succeeds
        # (Looking at health-check.sh around line 55: pass ".locked is valid JSON")
        # And "fail .locked is NOT valid JSON" if it fails.
        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert ".locked is valid JSON" in result.stdout
        assert ".locked is NOT valid JSON" not in result.stdout

def test_health_check_invalid_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        lock_file = setup_mock_repo(tmp_path)

        # Write invalid JSON
        lock_file.write_text('{invalid_json: 123,')

        result = subprocess.run(
            ["bash", str(tmp_path / ".agent" / "scripts" / "health-check.sh")],
            capture_output=True, text=True, cwd=tmpdir
        )

        assert ".locked is NOT valid JSON" in result.stdout
        assert ".locked is valid JSON" not in result.stdout
