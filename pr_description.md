🧪 Handle find error in empty directory check

🎯 **What:** The `consolidate.sh` script checks for empty directories using the `find` command. Because the script uses `set -euo pipefail`, if `find` encounters a directory it doesn't have permission to read, it exits with a non-zero status code and the pipeline fails, causing the script to exit early instead of continuing and reporting the empty directories. This testing gap was addressed by appending `|| true` to the end of the empty directory check pipeline and related find pipelines.

📊 **Coverage:** A new test case `test_empty_directories_error_path` was added to `.agent/tests/test_consolidate.py`. It simulates an unreadable directory using `0o000` permissions. The test verifies that `find` correctly continues and the script still successfully detects empty directories and does not exit with a failure due to the error.

✨ **Result:** Test coverage for `consolidate.sh` has been improved, and the script's robustness when scanning repositories with varied permission profiles has increased.
