# DevOps Homelab Automation Justfile
# Powered by pyinfra & just

default:
    @just --list

# --- BACKUP TASKS ---

# Backup Home Assistant configuration from live VM 100 to Git mirror using pyinfra & auto-merge Jules PRs
backup-ha:
    @echo "Syncing running Home Assistant configuration to mirror via pyinfra..."
    pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/backup_ha.py
    @echo "Checking Jules PRs and pushing changes to Git..."
    python3 /GitHub/homelab_devops/scripts/auto_jules_sync.py

# Backup Proxmox Host configuration files to Git mirror using pyinfra
backup-pve:
    @echo "Collecting local Proxmox configs via pyinfra..."
    pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/backup_pve.py
    @echo "Pushing changes to Git..."
    bash /root/ghup.sh

# --- RESTORE & RECOVERY TASKS ---

# Restore Home Assistant configs from Git mirror back to VM 100 filesystem using pyinfra
restore-ha-config:
    @echo "Restoring Home Assistant configuration via pyinfra..."
    pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/restore_ha.py

# Recreate a VM/LXC configuration definition file from Git mirror config
recreate-vm-shell vmid:
    @echo "Analyzing Git mirror configs..."
    @if [ -f "/root/ha_git_mirror/proxmox/qemu-server/{{vmid}}.conf" ]; then \
        echo "Found Qemu VM configuration for {{vmid}}."; \
        cp "/root/ha_git_mirror/proxmox/qemu-server/{{vmid}}.conf" "/etc/pve/qemu-server/"; \
        echo "Recreated configuration shell for VM {{vmid}}."; \
    elif [ -f "/root/ha_git_mirror/proxmox/lxc/{{vmid}}.conf" ]; then \
        echo "Found LXC container configuration for {{vmid}}."; \
        cp "/root/ha_git_mirror/proxmox/lxc/{{vmid}}.conf" "/etc/pve/lxc/"; \
        echo "Recreated configuration shell for LXC {{vmid}}."; \
    else \
        echo "ERROR: Configuration file for VM/LXC {{vmid}} not found in Git mirror."; \
        exit 1; \
    fi

# Restore a VM/LXC container from a vzdump archive
restore-vm vmid archive_path:
    @echo "Restoring VM/LXC {{vmid}} from archive {{archive_path}}..."
    @if [[ "{{archive_path}}" == *.tar.zst || "{{archive_path}}" == *.tgz || "{{archive_path}}" == *.tar ]]; then \
        pct restore {{vmid}} {{archive_path}} --force; \
    else \
        qmrestore {{archive_path}} {{vmid}} --force; \
    fi
    @echo "Restored VM/LXC {{vmid}} successfully."

# --- CLONE & SYNC TASKS ---

# Clone Live VM 100 to DEV VM 1000 and setup Postgres DEV DB
clone-dev:
    @echo "Running DEV VM updates from live VM..."
    bash /GitHub/homelab_devops/scripts/update_dev_vm.sh

# Align parameters for emergency standby VM 2000
sync-standby:
    @echo "Syncing standby configuration parameters..."
    bash /GitHub/homelab_devops/scripts/ha_standby_sync.sh

# --- INFRASTRUCTURE DEPLOYMENT ---

# Deploy updated Traefik proxy configurations to VM 5000
deploy-traefik:
	@echo "Deploying Traefik configurations via pyinfra..."
	pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/deploy_traefik.py

# Deploy Komodo GitOps CI/CD stack via pyinfra
deploy-komodo:
	@echo "Deploying Komodo GitOps CI/CD Stack via pyinfra..."
	pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/deploy_komodo.py

# Deploy LLM Stack (Llama.cpp Vulkan + Reasonix)
deploy-llm-stack:
	@echo "Deploying LLM Stack via pyinfra..."
	pyinfra -y @local /GitHub/homelab_devops/infra/deploy_llm_stack.py

# Deploy Home Assistant Internal Backup Sync to Host
deploy-ha-backup-sync:
	@echo "Deploying HA Backup Sync via pyinfra..."
	pyinfra -y @local /GitHub/homelab_devops/infra/deploy_ha_backup_sync.py

# --- LLM STACK & AI NODE TASKS ---

# Run bi-weekly AI model benchmark and check for updated models/quantizations
model-autoupdate:
	@echo "Running bi-weekly AI model evaluation & benchmark..."
	python3 /root/ha_git_mirror/scripts/ai_model_benchmarker.py
	@echo "Syncing model manifest..."
	bash /root/ha_git_mirror/agents_and_prompts/scripts/refresh_models.sh
	@echo "Pushing configuration updates to Git..."
	bash /root/ghup.sh

# Build or refresh the Proxmox LXC LLM-Stack Container Template (llama.cpp + Reasonix + JARVIS)
build-llm-lxc-template vmid="600":
	@echo "Building LXC LLM Template on VMID {{vmid}}..."
	@if pct status {{vmid}} >/dev/null 2>&1; then \
		echo "LXC Container {{vmid}} exists."; \
	else \
		echo "Creating LXC Container {{vmid}} shell..."; \
	fi

# Test llama.cpp server and Reasonix orchestration pipeline
test-llm-stack:
	@echo "Testing Reasonix and llama.cpp endpoints..."
	python3 /root/ha_git_mirror/scripts/ai_model_benchmarker.py

# --- SYSTEM & HACS UPDATE TASKS ---

# Execute pyinfra update playbook for infrastructure, host, VMs, containers, and Home Assistant
update-pyinfra:
	pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/update_system.py

# Execute single-button master update pipeline for host, VMs, containers, and Home Assistant
updateall:
	pyinfra -y /GitHub/homelab_devops/infra/inventory.py /GitHub/homelab_devops/infra/update_system.py

