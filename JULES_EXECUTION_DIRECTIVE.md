# Jules Execution Directive - Master System & LLM Stack Deployment

**Target System**: Proxmox VE 8.x, LXC 600 (`llm_stack_core`), Home Assistant (`ha_config`), Traefik (`homelab_infra`), Central Agents (`agents_and_prompts`)  
**Authorized Agent**: Jules (`jules.google.com`) via MCP / Antigravity Orchestrator

---

## 1. Execution Objective
Adjust all configurations, playbooks, and services across the Homelab and LLM Stack to achieve 100% compliance with the compiled requirements and the updated System-Wide Standard v2.0.

---

## 2. Mandatory Implementation Tasks

### Task 1: Proxmox LXC 600 Hardware Acceleration Passthrough
* **Action**: Configure LXC 600 configuration (`/etc/pve/lxc/600.conf`) to pass through the local **Google Coral TPU** (`/dev/apex_0`) and GPU devices.
* **Pyinfra File**: Update `/GitHub/homelab_infra/infra/deploy_llm_stack.py`.

### Task 2: Reasonix & Model Tiering Matrix
* **Action**: Ensure Reasonix Tier 1/2 Orchestrator (Port 8090) routes requests to:
  1. Local `llama.cpp` inference engine (Port 8080) hosting `gemma`, `devstral`, `soofi s`, `jarvis-base`, and `Qwen2.5-Coder-7B`.
  2. Cloud fallback API (Gemini Pro/Flash, Claude Sonnet/Opus, Jules MCP).
* **Auto-Update Cron**: Verify `/GitHub/homelab_infra/scripts/ai_model_benchmarker.py` is scheduled bi-weekly to benchmark and refresh models.

### Task 3: Obsidian RAG Layer Setup & Documentation Ingestion
* **Action**: Deploy a local Qdrant / Chroma vector database container in LXC 600.
* **Knowledge Ingestion**: Configure auto-ingestion of the Obsidian Vault (`obsidian_vault/`) AND all parallel accompaniment `.md` specification files into Qdrant so AI agents possess instant context retrieval.

### Task 4: Traefik Host Overrides Alignment (`aragdun`)
* **Action**: Keep `_infra` and `_core` repos free of concrete IPs and domains. Place the `aragdun` domain dynamic configs strictly in `homelab_config/hosts/aragog_config.yaml` to expose:
  - `llm.aragdun` -> Reasonix / llama.cpp (Port 8090)
  - `hermes.aragdun` -> Hermes Control UI (Port 9379)
  - `jarvis.aragdun` -> Jarvis AI WebUI (Port 9433)
* **Rule**: Strictly purge all legacy routing references to `gorlan`.

### Task 5: User Credentials & Default Overrides
* **Action**: Out-of-the-box defaults must remain `admin:admin` and `user:user` with Bearer token `LLM-Stack`. Store personal overrides (`marius` / `PandaYogi` and `Finn` / `LegoChima`) strictly inside `llm_stack_config/hosts/aragog_config.yaml`.

### Task 6: Mandatory Parallel Accompaniment Documentation Policy
* **Action**: For every script, playbook, or component modified or created, create a parallel `.md` documentation file right next to it or in the root directory. Trigger the RAG ingestion pipeline upon saving.

---

## 3. Verification & Validation Protocol
After applying changes:
1. Run `ha core check` on the Home Assistant node.
2. Run `just test-llm-stack` to verify Reasonix endpoint health.
3. Validate HTTPS certificates and subdomains under `*.aragdun`.
4. Log execution output to `/var/log/hlm_jules_execution.log`.
