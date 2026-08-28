# Compaction Cliff PoC

Pequeña aplicación Python para demostrar que una memoria de agente tratada como un único bloque pierde información crítica tras compactaciones sucesivas, y que una memoria tipada con políticas diferenciadas la conserva mejor.

Es una PoC **independiente y autocontenida**. No importa código de otros proyectos. Ejecuta el modelo localmente mediante **vLLM**, exponiendo su API compatible con OpenAI en `http://localhost:8000/v1`.

## Pregunta experimental

> ¿Conserva una estrategia de `Knowledge Triage` más restricciones críticas que una compactación convencional, usando los mismos elementos, modelo, presupuesto de salida y número de rondas?

Este repositorio guía un experimento, no intenta reproducir íntegramente el paper ni construir una plataforma de memoria empresarial.

## Documentos

1. [01-product-requirements.md](01-product-requirements.md): objetivo, alcance, requisitos y criterios de aceptación.
2. [02-architecture.md](02-architecture.md): arquitectura, modelo de datos y decisiones priorizadas.
3. [03-experiment-protocol.md](03-experiment-protocol.md): dataset, procedimiento, métricas y controles.
4. [04-implementation-plan.md](04-implementation-plan.md): estructura del proyecto, tareas y orden de ejecución.
5. [05-test-plan.md](05-test-plan.md): estrategia de pruebas y casos esenciales.
6. [06-vllm-local-guide.md](06-vllm-local-guide.md): instalación, selección del modelo y ejecución local.

## Resultado esperado

La aplicación ejecutará dos brazos:

- **Baseline**: todos los elementos se serializan como texto y se compactan con el LLM en cada ronda.
- **Knowledge Triage**: las restricciones se fijan sin compresión; los episodios se compactan; el conocimiento queda disponible para recuperación selectiva.

Tras cada ronda se evaluará cada elemento mediante identificadores y afirmaciones verificables. La salida será `results.json` y un resumen de consola con recall por tipo, recall de restricciones, tamaño aproximado del contexto y fallos observados.

## Decisión de éxito del PoC

Se considerará demostrada la hipótesis si, después de cinco rondas:

- Triage conserva el 100 % de las restricciones críticas por construcción.
- El baseline pierde al menos una restricción en alguna ejecución o muestra menor recall medio.
- Los resultados son repetibles mediante semilla, dataset versionado y configuración registrada.

Si el baseline no pierde restricciones, el experimento sigue siendo válido: deberá repetirse con más presión de compresión, sin cambiar las reglas entre estrategias.

## Independencia

Los cuatro archivos Python aportados se han revisado únicamente como referencia. No formarán parte del proyecto ni serán necesarios para instalarlo o ejecutarlo. El nuevo cliente será mínimo, interno a la PoC y específico para vLLM/OpenAI-compatible.
