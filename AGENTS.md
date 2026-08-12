# Home Assistant Addons Agent Guidelines (HA-addons)

> **Inheritance Notice:** This sub-project inherits all global rules from the Master Standards in `/root/homelab/AGENTS.md` and `/root/AGENTS.md`.

## Sub-Project Specific Rules (HA Addons)
1. Addon manifests (`config.yaml`) MUST comply with Home Assistant Supervisor addon specifications.
2. Build scripts and Dockerfiles MUST run non-interactively without prompting for input.
