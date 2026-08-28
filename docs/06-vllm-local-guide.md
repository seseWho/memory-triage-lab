# Local vLLM Execution Guide

## 1. Decision

The PoC will use vLLM as a local inference server and an OpenAI-compatible client inside the application. This separation keeps the experiment independent and allows the model to change without touching the domain, strategies, or metrics.

## 2. Practical Requirements

- Linux is recommended; on Windows, use WSL2 with a compatible Linux distribution.
- Compatible NVIDIA GPU, installed drivers, and sufficient memory for the chosen model.
- Python 3.11 or 3.12 for the application.
- A separate virtual environment for the PoC.

Install vLLM using the CUDA/PyTorch combination appropriate for the machine rather than blindly pinning a version in the application's environment. Therefore, separate:

- `.venv-app`: application, OpenAI client, validation, and tests.
- `.venv-vllm`: vLLM server and GPU dependencies.

## 3. Models Ordered by Fit

### 1. 4B–8B Instruct Model That Fits Comfortably on the GPU

This is the most suitable option for the PoC: it is capable of summarizing structured information, starts reasonably quickly, and allows the experiment to be repeated without excessive cost. An initial example is `Qwen/Qwen3-4B-Instruct-2507`.

**Final consideration:** leave VRAM headroom for the KV cache; a larger model does not necessarily improve the experiment if it forces a smaller context or causes instability.

### 2. Small 1B–3B Instruct Model

It makes the demo easier to run on limited hardware and may make information loss more visible.

**Final consideration:** formatting errors may be confused with the phenomenon under study; they must be counted separately.

### 3. Large Quantized Model

It may provide higher-quality compaction, but introduces more variables, execution time, and possible differences in the quantization backend.

**Final consideration:** reserve it for model comparisons after validating the protocol.

## 4. Recommended Startup

```bash
vllm serve Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000 \
  --served-model-name memory-cliff-model \
  --generation-config vllm
```

`--generation-config vllm` helps prevent the model's embedded configuration from silently changing experiment parameters. The application will explicitly send temperature, seed, and maximum tokens.

## 5. Server Check

```bash
curl http://127.0.0.1:8000/v1/models
```

Then:

```bash
python -m memory_cliff.cli health
python -m memory_cliff.cli run --strategies baseline triage --rounds 5
```

## 6. Reproducibility

Each run will save:

- modelo servido;
- versión de vLLM;
- semilla solicitada;
- temperature and output limits;
- presupuesto de compactación;
- hash del dataset;
- raw responses and per-round metrics.

Even with zero temperature and a seed, perfect determinism across GPUs, kernels, or versions must not be assumed. For comparable results, use the same machine and environment image and repeat at least three times.

## 7. Security and Isolation

- Listen only on `127.0.0.1`, not `0.0.0.0`, unless consciously required.
- Do not send real sensitive data: the dataset will be synthetic.
- Do not enable remote code downloads unless the model requires it and it has been reviewed.
- Do not introduce a real API key; for localhost, a fictional string is sufficient if the client requires one.

## 8. No-GPU Alternative

The `--offline` mode uses `FakeCompactor` and validates the application, policies, metrics, and reports. It does not demonstrate LLM behavior, but allows all unit tests to be developed and run without vLLM.

