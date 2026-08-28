# vLLM Docker Reference Profile

## Status

This profile is derived from a setup validated on another local project on 25 August 2026. It is the preferred starting point for Memory Triage Lab, but it remains **unvalidated for this repository** until the project smoke test and first real compaction run are recorded.

## Reference hardware

- Windows host with Docker Desktop and WSL2.
- NVIDIA GeForce RTX 3060 with 12,288 MiB VRAM.
- NVIDIA driver 576.52.
- Docker Desktop engine 29.7.2.
- 12 CPUs and approximately 31 GiB RAM assigned to Docker.

## Selected profile

| Setting | Value | Reason |
|---|---|---|
| Image | `vllm/vllm-openai:v0.8.5` | Previously validated reference image |
| Model | `Qwen/Qwen3-8B-AWQ` | Fits a 12 GiB GPU while leaving KV-cache capacity |
| Served name | `qwen3-8b-awq` | Stable application-facing identifier |
| Quantization | `awq_marlin` | Matches the selected AWQ model |
| Data type | `half` | Validated with the reference setup |
| Maximum context | `16384` | Supports repeated compaction experiments |
| GPU utilization | `0.85` | Left approximately 1.38 GiB VRAM free in the reference run |
| Maximum sequences | `1` | The experiment is sequential and prioritizes context capacity |
| Prefix caching | enabled | Reuses shared prompt prefixes across repeated calls |

## Setup

Copy the example environment file and adjust only host-specific values:

```powershell
Copy-Item .env.example .env
New-Item -ItemType Directory -Force -Path "D:\_models\huggingface"
```

Keep Docker's disk image and the Hugging Face cache in separate directories. Moving the cache does not move Docker images or writable layers.

Verify GPU access before downloading the vLLM image or model:

```powershell
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## Start and verify

```powershell
docker compose up -d vllm
docker compose logs -f vllm
```

After the API server reports that it is ready:

```powershell
./scripts/check-vllm.ps1
docker stats memory-triage-vllm --no-stream
docker exec memory-triage-vllm nvidia-smi
```

Stop cleanly without deleting the model cache:

```powershell
docker compose down
```

## Memory fallback order

If initialization runs out of GPU memory, apply one change at a time:

1. Reduce `VLLM_MAX_MODEL_LEN` from `16384` to `12288`.
2. Reduce it from `12288` to `8192`.
3. Only if no other GPU workload is active, try utilization `0.90`.

The first option is safest because it releases KV-cache pressure without making vLLM reserve a larger fraction of total VRAM.

## Structured output caveat

The reference environment successfully returned a direct JSON object using `response_format={"type":"json_object"}`. Qwen3 can nevertheless emit `<think>` content in some configurations. Any reasoning text outside the JSON object is a contract failure and must be recorded separately from memory loss.

## Safety considerations

- Do not commit `.env`, Hugging Face tokens, or credentials.
- Review `docker system df -v` before removing Docker data.
- Never run broad pruning commands without identifying affected resources.
- Bind the host port only where needed; the experiment client uses localhost.

