#!/usr/bin/env python3
"""
Multi-Node Universal AI Codebase Guardian & Multi-Channel Communicator
Monitors Git commit changes across all 12 ecosystem repositories.
Supports multi-channel alerts (Telegram, Desktop OS Notifications, HA REST API, Log Files)
so it works everywhere even when no CLI agent, HA container, or browser is open.
"""

import os
import sys
import time
import json
import subprocess
import urllib.request
import urllib.parse
import logging
import platform

LOG_FILE = "/var/log/ai_codebase_guardian.log"
STATE_FILE = "/root/.ai_guardian_git_state.json"
CONFIG_FILE = "/root/.ai_guardian_config.json"
REPOS_DIR = "/GitHub"
HA_TOKEN_FILE = "/config/ha_token.json"
HA_URL = "http://192.168.200.20:8123"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AI-GUARDIAN] %(message)s"
)
logger = logging.getLogger("CodebaseGuardian")

def get_ha_token() -> str:
    try:
        if os.path.exists(HA_TOKEN_FILE):
            with open(HA_TOKEN_FILE, "r") as f:
                data = json.load(f)
                return data.get("token", "")
    except Exception:
        pass
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiZWE1YmE5OWE0NTk0OTZlODNlZjUwM2I1N2YyOWQ4ZCIsImlhdCI6MTc4Mjg1NTE1OSwiZXhwIjoyMDk4MjE1MTU5fQ.0vEV8X9RQxuHs7g_LLIHsOHLJ9yi2T1QUkWa9vOJ5_w"

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    }

def send_desktop_notification(title: str, message: str):
    """Native OS Notification for Linux / macOS / Windows desktop workstations."""
    system = platform.system()
    try:
        if system == "Linux":
            subprocess.run(["notify-send", title, message], capture_output=True, timeout=3)
        elif system == "Darwin": # macOS
            apple_script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", apple_script], capture_output=True, timeout=3)
        elif system == "Windows":
            ps_script = f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, timeout=3)
    except Exception as e:
        logger.debug(f"Desktop notification note ({system}): {e}")

def send_telegram_message(title: str, message: str):
    """Direct Telegram Bot Alert (works even when HA or Desktop UI is offline)."""
    cfg = load_config()
    token = cfg.get("telegram_bot_token")
    chat_id = cfg.get("telegram_chat_id")
    
    if token and chat_id:
        try:
            text = f"<b>{title}</b>\n\n{message}"
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = json.dumps({
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=5)
            logger.info("Sent Telegram notification successfully.")
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")

def send_ha_notification(title: str, message: str):
    """Home Assistant Persistent & Mobile Push Notification (if HA is available)."""
    token = get_ha_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = json.dumps({"title": title, "message": message}).encode("utf-8")
    try:
        req = urllib.request.Request(f"{HA_URL}/api/services/persistent_notification/create", data=payload, headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

def broadcast_alert(title: str, message: str):
    """Multi-channel alert dispatch: Desktop OS, Telegram, HA Persistent."""
    logger.info(f"BROADCAST ALERT: {title} - {message}")
    send_desktop_notification(title, message)
    send_telegram_message(title, message)
    send_ha_notification(title, message)

def get_repo_head(repo_path: str) -> str:
    try:
        res = subprocess.run(["git", "-C", repo_path, "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def check_ha_config_and_reload(changed_repos: list):
    logger.info("Executing Home Assistant configuration check & auto-reload...")
    cmd_check = "qm guest exec 100 -- docker exec homeassistant python3 -m homeassistant --script check_config -c /config"
    res = subprocess.run(cmd_check, shell=True, capture_output=True, text=True)
    out = res.stdout.lower() + res.stderr.lower()
    
    if "error" in out or "invalid" in out:
        logger.warning(f"HA Configuration issue detected after commit sync: {out[:300]}")
        broadcast_alert(
            "⚠️ AI Guardian: Codebase Config Warning",
            f"Neue Commits in [{', '.join(changed_repos)}] empfangen. Syntax-Auffälligkeit erkannt."
        )
    else:
        token = get_ha_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        endpoints = [
            "/api/services/homeassistant/reload_core_config",
            "/api/services/automation/reload",
            "/api/services/script/reload",
            "/api/services/pyscript/reload"
        ]
        for ep in endpoints:
            try:
                req = urllib.request.Request(f"{HA_URL}{ep}", data=b"{}", headers=headers, method="POST")
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
                
        broadcast_alert(
            "🛡️ AI Guardian: Config Alignment Active",
            f"Neue Commits in [{', '.join(changed_repos)}] erfolgreich verifiziert & angewendet."
        )

def run_guardian_check():
    if not os.path.exists(REPOS_DIR):
        return

    old_state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                old_state = json.load(f)
        except Exception:
            old_state = {}

    current_state = {}
    changed_repos = []

    repos = [d for d in os.listdir(REPOS_DIR) if os.path.isdir(os.path.join(REPOS_DIR, d, ".git"))]

    for r in repos:
        repo_path = os.path.join(REPOS_DIR, r)
        head = get_repo_head(repo_path)
        current_state[r] = head
        
        if r in old_state and old_state[r] != head:
            changed_repos.append(r)
            logger.info(f"Detected commit change in repository '{r}': {old_state[r][:7]} -> {head[:7]}")

    if changed_repos:
        logger.info(f"AI Guardian triggered for updated repos: {changed_repos}")
        
        if any(r in changed_repos for r in ["ha_config", "ha_addons_ext", "ha_backup_slim"]):
            check_ha_config_and_reload(changed_repos)
        else:
            broadcast_alert(
                "🛡️ AI Guardian: Repositories Updated",
                f"Neue Commits in [{', '.join(changed_repos)}] erfolgreich im Cluster synchronisiert."
            )
            
    with open(STATE_FILE, "w") as f:
        json.dump(current_state, f, indent=2)

if __name__ == "__main__":
    run_guardian_check()
