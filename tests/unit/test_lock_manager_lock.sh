#!/usr/bin/env bash

# Test lock acquisition in lock-manager.sh

set -euo pipefail

# Setup test environment
TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' 0

mkdir -p "$TEST_DIR/.agent/scripts"
mkdir -p "$TEST_DIR/.agent/locks"

# Copy the script to test dir so REPO_ROOT resolves correctly
cp .agent/scripts/lock-manager.sh "$TEST_DIR/.agent/scripts/"
LOCK_MGR="$TEST_DIR/.agent/scripts/lock-manager.sh"
LOCK_FILE="$TEST_DIR/.agent/locks/.locked"

# Utility for testing
test_failed=0
run_test() {
  local name="$1"
  shift

  # Reset state before each test
  cat << 'JSON' > "$LOCK_FILE"
{
  "format_version": "1.0",
  "locks": []
}
JSON

  echo -n "Running test: $name ... "
  if "$@"; then
    echo -e "\033[0;32mPASS\033[0m"
  else
    echo -e "\033[0;31mFAIL\033[0m"
    test_failed=1
  fi
}

assert_exit_code() {
  local expected="$1"
  shift
  set +e
  "$@" >/dev/null 2>&1
  local code=$?
  set -e
  if [[ "$code" -ne "$expected" ]]; then
    echo -e "\n  Expected exit code $expected, got $code for command: $*"
    return 1
  fi
  return 0
}

assert_lock_exists() {
  local path="$1"
  local type="$2"
  local agent="$3"

  local count
  count=$(python3 -c "
import json, sys
with open('$LOCK_FILE') as f:
    data = json.load(f)
found = sum(1 for l in data.get('locks', []) if l.get('file_or_folder') == '$path' and l.get('type') == '$type' and l.get('locked_by') == '$agent')
print(found)
")
  if [[ "$count" == "0" ]]; then
    echo -e "\n  Lock not found for $path, $type, $agent in $LOCK_FILE"
    cat "$LOCK_FILE"
    return 1
  fi
  return 0
}

# Change to test directory since lock-manager.sh uses relative paths for Python
cd "$TEST_DIR"

# ================== TESTS ==================

test_invalid_type() {
  assert_exit_code 1 bash "$LOCK_MGR" lock "some/file.txt" "INVALID" "agent1" "Testing invalid type"
}

test_valid_soft_lock() {
  assert_exit_code 0 bash "$LOCK_MGR" lock "some/file.txt" "SOFT" "agent1" "Testing soft lock"
  assert_lock_exists "some/file.txt" "SOFT" "agent1"
}

test_conflict_hard_lock() {
  # Inject a HARD lock
  python3 -c "
import json
with open('$LOCK_FILE') as f: data = json.load(f)
data['locks'].append({'id': 'hard1', 'file_or_folder': 'hard/file.txt', 'type': 'HARD', 'locked_by': 'human'})
with open('$LOCK_FILE', 'w') as f: json.dump(data, f)
"
  # Try to lock
  assert_exit_code 1 bash "$LOCK_MGR" lock "hard/file.txt" "SOFT" "agent1" "Try to override hard"
}

test_conflict_soft_lock_other_agent() {
  # Pre-lock file with agent1
  bash "$LOCK_MGR" lock "some/file.txt" "SOFT" "agent1" "Testing soft lock" >/dev/null 2>&1
  # Try to lock with agent2
  assert_exit_code 1 bash "$LOCK_MGR" lock "some/file.txt" "SOFT" "agent2" "Try to override other agent soft"
}

test_same_agent_re_lock() {
  # Pre-lock file with agent1
  bash "$LOCK_MGR" lock "some/file.txt" "SOFT" "agent1" "Testing soft lock" >/dev/null 2>&1
  # It should allow same agent to lock again or basically not exit 1 due to conflict
  assert_exit_code 0 bash "$LOCK_MGR" lock "some/file.txt" "SOFT" "agent1" "Relock same file"
}

run_test "Invalid lock type" test_invalid_type
run_test "Valid SOFT lock" test_valid_soft_lock
run_test "Conflict with HARD lock" test_conflict_hard_lock
run_test "Conflict with other agent SOFT lock" test_conflict_soft_lock_other_agent
run_test "Same agent re-lock" test_same_agent_re_lock

if [[ "$test_failed" -ne 0 ]]; then
  echo "Tests failed"
  # Instead of exit 1, use a non-blocking way to report failure since this is run by run_in_bash_session.
  # We will just print tests failed and use `false` to set non-zero status at the end.
  false
fi
echo "All cmd_lock tests passed."
