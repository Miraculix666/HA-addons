from pathlib import Path
content = Path(".agent/scripts/health-check.sh").read_text()
print(f"Length: {len(content)}")
