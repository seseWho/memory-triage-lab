# Requisitos del producto

## 1. Propósito

Construir una aplicación de consola en Python que compare una memoria monolítica compactada por un LLM con una memoria tipada basada en `Knowledge Triage`.

## 2. Usuario objetivo

Arquitectos y desarrolladores que quieran comprender y demostrar el riesgo de degradar reglas, decisiones y conocimiento cuando el historial de un agente se resume repetidamente.

## 3. Alcance del MVP

La aplicación debe:

1. Cargar entre 30 y 50 elementos de memoria desde JSON.
2. Admitir cinco tipos: `constraint`, `decision`, `evidence`, `episode` y `preference`.
3. Ejecutar dos estrategias sobre copias idénticas del dataset.
4. Realizar cinco rondas de compactación.
5. Aplicar perturbaciones deterministas entre rondas para simular crecimiento de contexto.
6. Evaluar qué elementos siguen recuperables tras cada ronda.
7. Generar resultados estructurados y un resumen legible.

## 4. Fuera de alcance

- Interfaz web, base de datos, embeddings o vector database.
- Memoria multiusuario o distribuida.
- Evaluación semántica basada exclusivamente en otro LLM.
- Reproducción exacta de los porcentajes publicados en el paper.
- Integración con un framework agentic.

## 5. Requisitos funcionales

| ID | Requisito | Prioridad |
|---|---|---|
| FR-01 | Cargar y validar un dataset JSON versionado | Must |
| FR-02 | Ejecutar `baseline` y `triage` con igual configuración | Must |
| FR-03 | Fijar constraints en la estrategia triage | Must |
| FR-04 | Compactar episodios mediante LLM | Must |
| FR-05 | Mantener conocimiento/evidencia fuera del resumen y recuperarlo por consulta simple | Must |
| FR-06 | Ejecutar N rondas configurables, por defecto 5 | Must |
| FR-07 | Medir recall global y por tipo | Must |
| FR-08 | Registrar modelo, temperatura, límites y hashes de entrada | Must |
| FR-09 | Exportar `results.json` y `summary.md` | Should |
| FR-10 | Permitir ejecución sin API mediante un compactor falso determinista | Should |

## 6. Requisitos no funcionales

- Python 3.11 o superior.
- Ejecución del LLM en local mediante vLLM y API OpenAI-compatible.
- Proyecto instalable y ejecutable sin dependencias de otros repositorios.
- Sin secretos en código ni resultados.
- `temperature=0` cuando el proveedor lo permita.
- Timeout explícito y reintentos limitados.
- La lógica de dominio no dependerá de `requests` ni del proveedor LLM.
- Una ejecución fallida no se contará como pérdida de memoria: se registrará como error experimental.

## 7. Modelo mínimo

```text
MemoryItem
  id: str
  type: constraint | decision | evidence | episode | preference
  text: str
  criticality: critical | high | normal
  scope: str
  provenance: str
  retention_policy: pin | compact | retrieve
  check_terms: list[str]
```

`check_terms` contiene hechos canónicos breves necesarios para evaluar la conservación sin exigir coincidencia textual completa.

## 8. Criterios de aceptación

- La misma entrada alimenta ambos brazos sin mutación compartida.
- Ninguna restricción con política `pin` se envía al LLM para ser reescrita.
- Cada ronda produce métricas por estrategia y tipo.
- Se puede identificar qué ítem se perdió, no solo un porcentaje agregado.
- Los tests unitarios pueden ejecutarse sin conexión.
- La configuración secreta se carga desde variables de entorno.
- El modo offline de pruebas no requiere GPU ni servidor vLLM.

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El LLM devuelve texto no estructurado | Contrato JSON, parser defensivo y fallo explícito |
| Un verificador léxico penaliza paráfrasis válidas | `check_terms` normalizados y revisión manual de discrepancias |
| El resultado depende de azar/proveedor | Temperatura baja, varias repeticiones y configuración registrada |
| Comparación injusta por distinto presupuesto | Mismo límite de tokens y misma presión de compresión |
| El pinning “hace trampa” | Declararlo como política arquitectónica deliberada y medir también coste de contexto |
