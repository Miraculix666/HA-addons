import os
print("Test script successfully running")
content = open(".agent/scripts/health-check.sh").read()
print(content[-500:])
