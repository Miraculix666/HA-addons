# LLM Stack Master Requirements, Hardware & Home Assistant Integration Specification

**Target Repository**: `agents_and_prompts/LLM_STACK_MASTER_REQUIREMENTS.md`  
**Cross-Referenced Repositories**:
- 📦 **`llm_stack_core`**: Inference engines, Docker/LXC templates, Reasonix orchestrator, mesh-grid protocols.
- ⚙️ **`llm_stack_config`**: Private host parameters (`global/` and `hosts/`), API keys, user credentials.
- 💾 **`llm_stack_backup`**: Vector database dumps, model weights, benchmark logs.
- 🛠️ **`homelab_infra`**: Proxmox LXC 600 playbooks, Traefik reverse proxy, DNS setup.
- 🏠 **`ha_config`**: Home Assistant active configuration, custom components (`llmvision`, `ollama_vision`, `openai_stt`).
- 🧩 **`ha_addons_ext`**: HACS custom components (`Obico-HA-addon`, `tariffwise`, `updateall`).
- 🧠 **`agents_and_prompts`**: Central agent prompts, system standards, Jules directives.

---

## 1. Core LLM Stack Services vs. External Integrations

To maintain clean architecture, **Obico** and **Home Assistant Integrations** are **NOT core components of the LLM Stack**, but external consumers that connect via API.

### 1.1 Core LLM Stack Services Manifest
| Service Name | Default Port | Source / Repository URL | Description / Purpose |
| :--- | :--- | :--- | :--- |
| **llama.cpp Engine** | `8080` | [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) | High-performance GGUF local C/C++ inference engine. |
| **Reasonix Orchestrator** | `8090` | [reasonix.ai](https://reasonix.ai) | Central Tier 1/2 Orchestrator managing model routing and subagent delegation. |
| **Qdrant Vector DB** | `6333` | [qdrant.tech](https://qdrant.tech) | High-performance vector database for Obsidian Vault RAG context storage. |
| **Hermes Control Deck** | `9379` | [hermes-agent.org](https://hermes-agent.org) | Agent dashboard, chat WebUI, and control interface for Hermes CLI. |
| **Jarvis Server & WebUI** | `9433` | Internal (`llm_stack_core`) | OpenJarvis AI server, Kanban board, chat, speech (STT/TTS) & HUD display. |
| **OpenGPT WebUI** | `3000` | [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm) | Open-source web UI frontend for general LLM interactions. |
| **Traefik Proxy (OPTIONAL)** | `80 / 443` | [traefik.io](https://traefik.io) | **Optional** reverse proxy for direct remote access (`*.aragdun`). |

### 1.2 Connected External Services & Integrations (On-Demand)
* **Obico 3D Printer AI** (`ha_addons_ext/Obico-HA-addon` / Port `8088`):
  - Connects on-demand to `http://<llm_ip>:8090/v1` for Mercury 3D printer print-failure AI detection.
* **HA LLM Vision** (`ha_config/homeassistant/custom_components/llmvision`):
  - Home Assistant integration sending camera snapshots to `http://<llm_ip>:8090/v1` for AI event analysis.
* **Ollama Vision & OpenAI STT** (`ha_config/homeassistant/custom_components/`):
  - Local STT and Vision integrations configured via Home Assistant UI or `configuration.yaml`.

---

## 2. Hardware Acceleration & CPU/GPU/TPU/OS Matrix

The LLM Stack automatically detects and utilizes available hardware acceleration across all supported platforms.

### 2.1 CPU & Architecture Matrix
* **Apple Mac (Intel x86_64)**:
  - Supports Intel Core i5/i7/i9 Macs. Automatically compiles with `AVX2` / `AVX512` instruction sets. Uses host CPU RAM or eGPU (AMD Radeon via `GGML_HIPBLAS`).
* **Apple Mac (Apple Silicon M1/M2/M3/M4 ARM64)**:
  - Offloads 100% of LLM layers directly to Apple Metal Unified Memory (`-ngl 99` / `GGML_METAL=on`).
* **x86_64 Linux / Windows (Intel & AMD CPUs)**:
  - Vector acceleration via `AVX2`, `AVX512`, and `AMX`.
* **ARM64 Linux (Raspberry Pi 4/5, Nvidia Jetson)**:
  - Vector acceleration via ARM `NEON` and FP16 operations.

### 2.2 GPU & TPU Acceleration Matrix
* **NVIDIA GPU (CUDA / TensorRT)**: `GGML_CUDA=on` / cuBLAS VRAM offloading.
* **AMD GPU (ROCm / HIP)**: `GGML_HIPBLAS=on` via `/dev/kfd` and `/dev/dri`.
* **Intel GPU & NPU (oneAPI / OpenVINO / Arc)**: `GGML_SYCL=on` or OpenVINO provider for Intel Arc GPUs & Core Ultra NPUs.
* **Google Coral TPU (Edge Acceleration)**: `/dev/apex_0` passthrough (`c 120:* rwm`).

---

## 3. Home Assistant & LLM Addon Connection Guide

### 3.1 Connecting HA Extended Conversation & LLM Vision to the Stack
In Home Assistant (`ha_config`), navigate to **Settings -> Devices & Services -> Add Integration**:

1. **Extended OpenAI Conversation**:
   - **API Key**: `LLM-Stack`
   - **API Base**: `http://192.168.80.60:8090/v1`
   - **Model**: `reasonix-orchestrator` (or `Qwen2.5-Coder-7B-Instruct-Home-Assistant`)
2. **LLM Vision (`custom_components/llmvision`)**:
   - **Provider**: Custom OpenAI Compatible
   - **Endpoint**: `http://192.168.80.60:8090/v1`
   - **Model**: `gemma` / `llmvision-base`

### 3.2 Connecting Obico (Mercury 3D Printer AI)
In Obico Server settings (`ha_addons_ext/Obico-HA-addon`):
- Set AI Inference Endpoint: `http://192.168.80.60:8090/v1`
- Model Provider: `Reasonix Dynamic Router`

---

## 4. Configuration Separation: Universal Defaults vs. Host-Specific (`aragdun`)

To keep `llm_stack_core` 100% universal and open-source ready, all private IPs, domains, and secrets are stored in `llm_stack_config`.

### 4.1 Universal Defaults (`global/general_config.yaml`)
- **Domain Template**: `*.local` / `http://localhost:<port>`
- **Default Credentials**: `admin:admin` and `user:user`
- **Default Bearer Token**: `LLM-Stack`

### 4.2 Host Overrides Example (`hosts/aragog_config.yaml`)
```yaml
# File: llm_stack_config/hosts/aragog_config.yaml
host_info:
  hostname: "aragog"
  ip: "192.168.80.60"
  domain: "aragdun"  # Personal host domain override

traefik_overrides:
  enabled: true
  rules:
    - service: "llm"
      rule: "Host(`llm.aragdun`)"
    - service: "hermes"
      rule: "Host(`hermes.aragdun`)"

auth_overrides:
  admin_user: "marius"
  admin_password_hash: "$2b$12$..."
  user_user: "Finn"
  user_password_hash: "$2b$12$..."
  api_bearer_token: "LLM-Stack-Personal-Secure-Token"
```

---

## 5. Extended Dedicated Model & Speech/Inference Engine Matrix

### 5.1 LLM & Code Reasoning Models
- **`reasonix-orchestrator`**: Primary orchestrator model (Tier 1).
- **`devstral`**: Specialized coding, refactoring, and DevOps model.
- **`soofi s`**: Fast, lightweight subagent model.
- **`gemma`**: Google Gemma model (native for Gemini CLI & AGY local fallback).
- **`jarvis-base`**: Voice-optimized model for Jarvis speech synthesis.
- **`Qwen2.5-Coder-7B-Instruct-Home-Assistant`**: Tier-2 model for HA YAML & automation repairs.
- **`opengpt`**: General task solver.
- **`DeepSeek-R1` / `DeepSeek-Coder`**: High-level reasoning & code generation.
- **`Phi-3.5` / `Llama-3.1-8B`**: Compact local models.
- **Cloud Fallbacks**: Gemini 3.6 Flash/Pro, Claude 3.7 Thinking/Sonnet/Opus, Codestral.

### 5.2 Speech & Audio Processing Engines (STT / TTS / WakeWord)
- **`Whisper` / `faster-whisper`** (STT - Speech-to-Text):
  - Local real-time CTranslate2/faster-whisper speech recognition engine (`openai/whisper-large-v3`, `whisper-base.en`).
  - Integrated via Wyoming Protocol (`core-whisper` / `stt.faster_whisper`) and Jarvis Voice Pipeline (`WHISPER_STT_URL` / Port `8000`).
- **`Piper` / `Edge-TTS`** (TTS - Text-to-Speech):
  - Local neural voice synthesis engine (`de_DE-thorsten-medium` voice model).
  - Integrated via `PIPER_TTS_URL` (Port `5000`) for instant local audio generation.
- **`openWakeWord`** (Wake-Word Detection):
  - Local ONNX-based wake-word detection engine (`hey_jarvis`, `alexa`, `ok_google`).
- **`Silero VAD`** (Voice Activity Detection):
  - Ultra-fast local voice activity filtering for low-latency audio chunk processing.

### 5.3 High-Throughput & Specialized Inference Backends
- **`vLLM Engine` / `Qwen-ASR (vLLM)`**:
  - High-throughput PagedAttention inference backend for serving large concurrency requests.
- **`CTranslate2`**:
  - C++ inference engine for fast transformer execution of STT/TTS models.

---

## 6. Master Execution Directive for Jules (@jules)

<!-- @jules send to jules.google.com -->
> **JULES MASTER EXECUTION DIRECTIVE:**  
> `@jules: Read 'agents_and_prompts/LLM_STACK_MASTER_REQUIREMENTS.md'. Execute complete configuration and adjustment across all repositories ('llm_stack_core', 'llm_stack_config', 'homelab_infra', 'ha_config', 'ha_addons_ext'). Deploy core services (llama.cpp, Reasonix, Qdrant, Hermes Control Deck, Jarvis, OpenGPT WebUI). Keep Obico and HA LLM Vision as connected external API consumers. Universal defaults must remain admin:admin and user:user with token 'LLM-Stack'. Personal domains like 'aragdun' stay strictly in host overrides. Configure complete hardware matrix including Mac Intel (AVX2/AVX512), Mac Apple Silicon (Metal), NVIDIA CUDA, AMD ROCm, Intel OpenVINO/Arc, and Coral TPU. Pre-configure Home Assistant connection guide for Extended OpenAI Conversation and LLM Vision. Enforce Repository-Level Split (no secrets in _core repos). Log all results to '/var/log/hlm_jules_master_execution.log'.`
