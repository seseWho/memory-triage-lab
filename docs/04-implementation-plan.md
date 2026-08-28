# Plan de implementación

## 1. Estructura propuesta

```text
compaction-cliff-poc/
├── pyproject.toml
├── requirements-vllm.txt
├── .env.example
├── data/memory_items.json
├── src/memory_cliff/
│   ├── cli.py
│   ├── domain.py
│   ├── runner.py
│   ├── evaluation.py
│   ├── reporting.py
│   ├── strategies/baseline.py
│   ├── strategies/triage.py
│   └── llm/{port.py,http_client.py,fake.py}
├── tests/
│   ├── unit/
│   └── integration/
└── results/.gitkeep
```

## 2. Flujo de ejecución

```bash
python -m memory_cliff.cli run \
  --dataset data/memory_items.json \
  --rounds 5 \
  --strategies baseline triage \
  --target-words 700 \
  --output results/run-001
```

El servidor se inicia por separado:

```bash
vllm serve Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000 \
  --served-model-name memory-cliff-model \
  --generation-config vllm
```

El modelo es una propuesta inicial y debe ajustarse a la GPU disponible. El nombre servido, no el identificador del repositorio, será el valor de `LLM_MODEL`.

Debe existir también:

```bash
python -m memory_cliff.cli run --offline
pytest
```

## 3. Backlog ordenado

### 1. Dominio, dataset y evaluador determinista

Es la primera prioridad porque define qué significa “recordar” y permite probar todo sin red. Sin una medida estable, cualquier resultado del LLM sería anecdótico.

**Consideración final:** revisar manualmente los `check_terms`; son parte del instrumento de medida.

### 2. Runner y fake compactor

Permite cerrar un recorrido end-to-end reproducible antes de introducir variabilidad externa.

**Consideración final:** el fake debe eliminar elementos de manera predecible, no simular inteligencia.

### 3. Baseline LLM

Implementa la compactación monolítica con contrato JSON y presupuesto fijo.

**Consideración final:** guardar prompt y respuesta bruta por ronda para diagnosticar pérdidas.

### 4. Estrategia Knowledge Triage

Clasifica, fija constraints, compacta episodios y recupera conocimiento por metadatos/términos.

**Consideración final:** la clasificación inicial será declarada en el dataset; clasificación automática sería otro experimento.

### 5. Informes y repeticiones

Añade comparación por ronda, agregados y artefactos auditables.

**Consideración final:** priorizar JSON y Markdown; un dashboard no aporta valor todavía.

### 6. Extensiones opcionales

Tercer brazo con prompt reforzado, juez LLM, embeddings y UI.

**Consideración final:** solo incorporarlas después de obtener una línea base clara.

## 4. Estimación pequeña

| Bloque | Esfuerzo orientativo |
|---|---:|
| Dominio + dataset + evaluación | 2–3 h |
| Runner + fake | 1–2 h |
| Baseline + adaptación cliente | 2 h |
| Triage | 2–3 h |
| Informes + documentación de ejecución | 1–2 h |

Total estimado: 8–12 horas para un PoC limpio.

## 5. Configuración

```dotenv
LLM_API_KEY=
LLM_BASE_URL=http://127.0.0.1:8000/v1
LLM_MODEL=memory-cliff-model
LLM_TIMEOUT_SECONDS=60
LLM_MAX_TOKENS=1200
```

Nunca se incluirá un `.env` real en control de versiones.

En vLLM local, `LLM_API_KEY` puede fijarse a un valor no secreto como `local` si el cliente exige una cadena.

## 6. Definition of Done

- Tests offline en verde.
- Ejecución real completa con cinco rondas para ambas estrategias.
- Dataset y configuración identificables por hash.
- Resultados contienen pérdidas por ID y recall por tipo.
- Ninguna constraint fijada se modifica en triage.
- README incluye comando exacto y limitaciones observadas.
