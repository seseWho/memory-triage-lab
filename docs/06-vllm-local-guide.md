# Guía de ejecución local con vLLM

## 1. Decisión

La PoC usará vLLM como servidor de inferencia local y un cliente OpenAI-compatible dentro de la aplicación. Esta separación mantiene el experimento independiente y permite cambiar de modelo sin tocar dominio, estrategias ni métricas.

## 2. Requisitos prácticos

- Linux es la opción recomendada; en Windows, usar WSL2 con una distribución Linux compatible.
- GPU NVIDIA compatible, drivers instalados y memoria suficiente para el modelo elegido.
- Python 3.11 o 3.12 para la aplicación.
- Un entorno virtual separado para la PoC.

Conviene instalar vLLM siguiendo la combinación CUDA/PyTorch adecuada para la máquina en vez de fijar a ciegas una versión en el mismo entorno de la aplicación. Por eso se propone separar:

- `.venv-app`: aplicación, cliente OpenAI, validación y tests.
- `.venv-vllm`: servidor vLLM y dependencias GPU.

## 3. Modelos ordenados por adecuación

### 1. Instruct de 4B–8B que quepa holgadamente en la GPU

Es la opción más adecuada para el PoC: tiene capacidad suficiente para resumir información estructurada, arranca razonablemente rápido y permite repetir el experimento sin un coste excesivo. Un ejemplo inicial es `Qwen/Qwen3-4B-Instruct-2507`.

**Consideración final:** dejar margen de VRAM para KV cache; un modelo más grande no hace necesariamente mejor el experimento si obliga a reducir contexto o provoca inestabilidad.

### 2. Instruct pequeño de 1B–3B

Facilita ejecutar la demo con hardware limitado y puede hacer más visible la pérdida de información.

**Consideración final:** sus errores de formato pueden confundirse con el fenómeno estudiado; deben contabilizarse por separado.

### 3. Modelo grande cuantizado

Puede ofrecer una compactación de mayor calidad, pero introduce más variables, tiempos de ejecución y posibles diferencias del backend de cuantización.

**Consideración final:** reservarlo para comparar modelos después de validar el protocolo.

## 4. Arranque recomendado

```bash
vllm serve Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000 \
  --served-model-name memory-cliff-model \
  --generation-config vllm
```

`--generation-config vllm` ayuda a que la configuración embebida del modelo no cambie silenciosamente parámetros del experimento. La aplicación enviará temperatura, semilla y máximo de tokens de forma explícita.

## 5. Comprobación del servidor

```bash
curl http://127.0.0.1:8000/v1/models
```

Después:

```bash
python -m memory_cliff.cli health
python -m memory_cliff.cli run --strategies baseline triage --rounds 5
```

## 6. Reproducibilidad

Cada ejecución guardará:

- modelo servido;
- versión de vLLM;
- semilla solicitada;
- temperatura y límites de salida;
- presupuesto de compactación;
- hash del dataset;
- respuestas brutas y métricas por ronda.

Aunque se use temperatura cero y semilla, no debe asumirse determinismo perfecto entre GPUs, kernels o versiones. Para resultados comparables, usar la misma máquina e imagen de entorno y repetir al menos tres veces.

## 7. Seguridad y aislamiento

- Escuchar solo en `127.0.0.1`, no en `0.0.0.0`, salvo necesidad consciente.
- No enviar datos sensibles reales: el dataset será sintético.
- No habilitar descarga de código remoto salvo que el modelo lo requiera y se haya revisado.
- No introducir una API key real; para localhost basta una cadena ficticia si el cliente la exige.

## 8. Alternativa sin GPU

El modo `--offline` usa `FakeCompactor` y valida aplicación, políticas, métricas e informes. No demuestra comportamiento de un LLM, pero permite desarrollar y ejecutar todos los tests unitarios sin vLLM.

