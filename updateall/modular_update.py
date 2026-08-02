#!/usr/bin/env python3
import sys
import subprocess
import time
import json

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def update_host():
    print("Updating Proxmox Host...")
    run_cmd("apt-get update -qq && apt-get dist-upgrade -y")
    print("Host updated.")

def start_and_wait_lxc(vmid):
    print(f"Starting LXC {vmid}...")
    run_cmd(f"pct start {vmid}")
    time.sleep(5)

def update_lxc(vmid):
    print(f"Updating LXC {vmid}...")
    run_cmd(f"pct exec {vmid} -- sh -c 'if command -v apt-get >/dev/null; then apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y; elif command -v apk >/dev/null; then apk update -q && apk upgrade; fi'")

def stop_lxc(vmid):
    print(f"Stopping LXC {vmid}...")
    run_cmd(f"pct stop {vmid}")

def start_and_wait_vm(vmid):
    print(f"Starting VM {vmid}...")
    run_cmd(f"qm start {vmid}")
    agent_up = False
    for i in range(30):
        res = subprocess.run(f"qm guest cmd {vmid} ping", shell=True, capture_output=True)
        if res.returncode == 0:
            agent_up = True
            break
        time.sleep(2)
    return agent_up

def update_vm(vmid):
    print(f"Updating VM {vmid}...")
    run_cmd(f"qm guest exec {vmid} -- sh -c 'if command -v apt-get >/dev/null; then apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y; elif command -v apk >/dev/null; then apk update -q && apk upgrade; fi'")

def stop_vm(vmid):
    print(f"Stopping VM {vmid}...")
    run_cmd(f"qm shutdown {vmid}")

def is_lxc_running(vmid):
    out = subprocess.run(f"pct status {vmid}", shell=True, capture_output=True, text=True).stdout
    return "running" in out

def is_vm_running(vmid):
    out = subprocess.run(f"qm status {vmid}", shell=True, capture_output=True, text=True).stdout
    return "running" in out

def update_docker_containers():
    print("Updating Docker containers in VMs and LXCs...")
    print("SUCCESS: Docker container lifecycle is entirely managed by Komodo GitOps CI/CD.")
    print("Manual Watchtower executions have been deprecated and removed in favor of Komodo's autonomous registry polling / webhook triggers.")

def process_target(target):
    if target == "proxmox-host":
        update_host()
        return
        
    if target == "docker":
        update_docker_containers()
        return

    if target == "lxcs":
        lxc_out = subprocess.run("pct list | awk 'NR>1 {print $1}'", shell=True, capture_output=True, text=True).stdout
        for vmid in lxc_out.splitlines():
            if vmid.strip():
                process_target(vmid.strip())
        return

    if target == "vms":
        vm_out = subprocess.run("qm list | awk 'NR>1 {print $1}'", shell=True, capture_output=True, text=True).stdout
        for vmid in vm_out.splitlines():
            if vmid.strip() and vmid.strip() not in ["100", "1000", "2000"]:
                process_target(vmid.strip())
        return

    # Try to find target by ID or name
    # Check LXCs
    lxc_out = subprocess.run("pct list | awk 'NR>1 {print $1, $3}'", shell=True, capture_output=True, text=True).stdout
    for line in lxc_out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            vmid = parts[0]
            name = parts[1]
            if target == vmid or target.lower() in name.lower():
                was_running = is_lxc_running(vmid)
                if not was_running:
                    start_and_wait_lxc(vmid)
                update_lxc(vmid)
                if not was_running:
                    stop_lxc(vmid)
                return

    # Check VMs
    vm_out = subprocess.run("qm list | awk 'NR>1 {print $1, $2}'", shell=True, capture_output=True, text=True).stdout
    for line in vm_out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            vmid = parts[0]
            name = parts[1]
            if target == vmid or target.lower() in name.lower():
                was_running = is_vm_running(vmid)
                if not was_running:
                    if not start_and_wait_vm(vmid):
                        print(f"Failed to start/agent not found for VM {vmid}")
                        return
                update_vm(vmid)
                if not was_running:
                    stop_vm(vmid)
                return
    
    print(f"Target '{target}' not found!")

def main():
    if len(sys.argv) < 2:
        print("Usage: modular_update.py <target1> <target2> ... (use 'all' for everything)")
        sys.exit(1)
        
    targets = sys.argv[1:]
    
    if "all" in targets:
        print("Updating ALL systems!")
        update_host()
        
        lxc_out = subprocess.run("pct list | awk 'NR>1 {print $1}'", shell=True, capture_output=True, text=True).stdout
        for vmid in lxc_out.splitlines():
            if vmid.strip():
                process_target(vmid.strip())
                
        vm_out = subprocess.run("qm list | awk 'NR>1 {print $1}'", shell=True, capture_output=True, text=True).stdout
        for vmid in vm_out.splitlines():
            if vmid.strip():
                process_target(vmid.strip())
                
        update_docker_containers()
    else:
        for target in targets:
            process_target(target)
            
    # Send done notification to HA
    try:
        msg = f"Update für {', '.join(targets)} erfolgreich abgeschlossen."
        payload = {"message": msg, "title": "Update Status"}
        subprocess.run(f"curl -s -X POST -H 'Content-Type: application/json' -d '{json.dumps(payload)}' http://192.168.200.20:8123/api/webhook/proxmox_update_status", shell=True)
    except:
        pass

if __name__ == '__main__':
    main()
