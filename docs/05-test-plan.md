# Plan de pruebas

## 1. Enfoque

Separar pruebas del software de ejecuciones del experimento. Los tests verifican contratos e invariantes; no deben afirmar que un LLM concreto necesariamente olvidará una regla.

## 2. Pruebas unitarias prioritarias

| ID | Caso | Resultado esperado |
|---|---|---|
| UT-01 | Dataset válido | Se crean 30–50 `MemoryItem` con IDs únicos |
| UT-02 | Tipo o política inválida | Error de validación claro |
| UT-03 | Triage de constraint | Se asigna `pin` |
| UT-04 | Cinco rondas triage | Texto canónico de constraints permanece idéntico |
| UT-05 | Evaluación con todos los términos | Ítem recuperado |
| UT-06 | Falta un término | Ítem ambiguo/perdido según configuración |
| UT-07 | Métrica por tipo | Numerador y denominador correctos |
| UT-08 | Copias de estrategias | Una estrategia no muta la entrada de la otra |
| UT-09 | Fake compactor | Misma entrada y semilla producen misma salida |
| UT-10 | Error LLM | Se registra error; no se registra como olvido |

## 3. Pruebas de integración

- Adaptador HTTP envía `messages` a `/chat/completions`.
- Timeout y códigos 4xx/5xx producen errores tipados.
- Respuesta JSON cercada en Markdown se normaliza o rechaza de forma explícita.
- Una ejecución offline genera `results.json` y `summary.md` válidos.
- Una ejecución real registra modelo y parámetros sin incluir secretos.
- El smoke test consulta el modelo servido por vLLM en localhost.

## 4. Pruebas de aceptación

### AC-01: comparación completa

**Dado** un dataset de 40 elementos, **cuando** se ejecutan cinco rondas con ambos brazos, **entonces** existen métricas por ronda, tipo y estrategia.

### AC-02: constraint determinista

**Dada** una constraint crítica, **cuando** triage ejecuta cinco rondas, **entonces** su representación canónica conserva el mismo hash.

### AC-03: trazabilidad de pérdida

**Dado** que se pierde un elemento, **cuando** se crea el informe, **entonces** aparece su ID, tipo, ronda y estrategia.

### AC-04: igualdad experimental

**Cuando** comienza una ronda, **entonces** ambos brazos reciben el mismo dataset, ruido y presupuesto configurado.

## 5. Revisión de las pruebas adjuntas

Las suites adjuntas sirven como referencia de smoke tests, pero no se copiarán ni serán dependencia de la PoC:

- `test_response_time < 5s` es frágil en VPN, proxy o modelo local; medir y reportar latencia es preferible a fallar por un umbral fijo.
- El test de contexto con 100.000 caracteres depende del límite del modelo y puede no lanzar error.
- Las pruebas de temperatura y razonamiento son no deterministas.
- Hay dos suites parcialmente duplicadas.
- Instanciar el cliente validando red en `setUp` convierte tests unitarios en integración.

Recomendación: conservar una única prueba de integración del adaptador, marcada como `integration`, y crear tests unitarios con `FakeCompactor`.

## 6. Comandos objetivo

```bash
pytest -m "not integration"
pytest -m integration
python -m memory_cliff.cli run --offline
```

Las pruebas `integration` requieren que vLLM esté arrancado; el resto debe funcionar en una máquina sin GPU.

