🧹 [Code Health] Remove unused sys import in test_script2.py

🎯 **What:**
Removed the unused `sys` module import in `test_script2.py`.

💡 **Why:**
The script was only opening and reading a file and printing some of its content. `sys` was completely unused. Removing unused imports helps reduce visual noise and improves the overall readability of the code, and is good practice.

✅ **Verification:**
- Ran the script manually to ensure it still prints the last 500 characters of the health check script.
- Ran the agent tests (`pytest .agent/tests/`) to ensure no regressions were introduced.
- Verified diff to ensure only the import was removed.

✨ **Result:**
Cleaner code in `test_script2.py` with no unused dependencies.
