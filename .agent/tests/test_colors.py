#!/usr/bin/env python3
"""test_colors.py - Tests for the colors.sh script"""

import pytest
import subprocess
from pathlib import Path

def test_colors_evaluation():
    script_path = Path(__file__).parent.parent / "scripts" / "colors.sh"

    check_script = f"""
    source {script_path}
    echo -n "${{RED}}|${{YELLOW}}|${{GREEN}}|${{BLUE}}|${{CYAN}}|${{BOLD}}|${{NC}}"
    """

    result = subprocess.run(["bash", "-c", check_script], capture_output=True, text=True)
    assert result.returncode == 0

    expected_output = "\\033[0;31m|\\033[1;33m|\\033[0;32m|\\033[0;34m|\\033[0;36m|\\033[1m|\\033[0m"
    assert result.stdout == expected_output
