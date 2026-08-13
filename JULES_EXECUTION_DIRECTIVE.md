# General System Execution Directive (Non-LLM Repositories)

**Target System**: General Homelab Infrastructure, Home Assistant, Microservices & Addons  
**Authorized Agent**: Jules (`jules.google.com`) / Antigravity IDE & Peer Agents

---

## 1. Execution Objective
Enforce the universal system-wide standards across all non-LLM repositories (`ha_core`, `ha_config`, `ha_backup_full`, `ha_backup_slim`, `ha_addons_ext`, `homelab_infra`, `homelab_config`, `proxmox_host_backup`).

---

## 2. Mandatory Rules for Non-LLM Repositories

### 1. Strict Configuration & Host Data Separation (Repo-Level Split)
* **Code & Core Repos (`_core`, `_infra`, `_ext`)**: Must remain 100% free of concrete host IPs, Proxmox VMIDs, PIDs, private domains, and credentials.
* **Config Repos (`_config`)**: All environmental specifics (e.g., IPs, VMIDs, credentials, Traefik domain overrides) must be stored strictly inside `_config/hosts/{hostname}_config.yaml` or `_config/global/general_config.yaml`.
* **Backup Repos (`_backup_*`)**: Must remain read-only archives with explicit warning notices.

### 2. Mandatory Parallel Accompaniment Documentation
* Every new or modified script, playbook, component, or configuration MUST have a corresponding parallel `.md` documentation file right next to it or in `docs/`.
* The accompaniment documentation is automatically ingested into the central vector database (Obsidian Knowledge Base) for AI agent retrieval.

### 3. Out-of-the-Box Defaults
* Out-of-the-box defaults must remain `admin:admin` and `user:user`. Personal credentials (e.g. `marius` / `Finn`) belong exclusively in host-specific override files.

---

## 3. Verification & Validation Protocol
After applying changes in this repository:
1. Run syntax validation (`ha core check` for HA, `pyinfra --syntax` for infra).
2. Ensure no uncommitted diffs remain.
3. Log results to `/var/log/hlm_jules_general_execution.log`.
