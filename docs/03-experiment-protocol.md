# Protocolo experimental

## 1. Hipótesis

- **H1:** el recall de constraints del baseline disminuirá con compactaciones sucesivas.
- **H2:** el recall de constraints de triage permanecerá en 100 % porque se fijan de forma determinista.
- **H3:** triage tendrá mejor recall ponderado sin requerir mantener todo el historial en el contexto activo.

## 2. Dataset recomendado: 40 elementos

| Tipo | Cantidad | Ejemplo |
|---|---:|---|
| Constraints | 8 | “No ejecutar operaciones destructivas sin autorización explícita” |
| Decisions | 8 | “SQLite fue elegido para funcionamiento offline” |
| Evidence | 8 | “El test de integración T-17 falló con timeout” |
| Episodes | 10 | “Ayer el usuario ejecutó el backtest B-04” |
| Preferences | 6 | “El usuario prefiere respuestas claras antes de la teoría” |

Cada ítem tendrá ID estable (`C01`, `D01`, etc.), procedencia, criticidad y entre uno y tres `check_terms`.

## 3. Presión de compactación

Antes de cada ronda se añadirán cinco episodios de ruido deterministas. Después, cada estrategia deberá producir un contexto activo dentro del mismo presupuesto objetivo. Valor inicial recomendado: 700 palabras; si no aparece pérdida, reducir a 500 y después a 350.

No se cambiarán simultáneamente dataset, prompt y presupuesto durante una comparación.

## 4. Procedimiento

1. Validar y congelar el dataset; calcular su SHA-256.
2. Crear dos copias independientes.
3. Para las rondas 1 a 5:
   1. Añadir el mismo ruido a ambos brazos.
   2. Ejecutar compactación baseline.
   3. Ejecutar las políticas triage.
   4. Formular las mismas consultas de recuperación.
   5. Evaluar todos los ítems y guardar trazas.
4. Repetir el experimento al menos tres veces si el modelo no es determinista.
5. Comparar media, mínimo y dispersión.

## 5. Evaluación de conservación

Un elemento se considera recuperado cuando:

- su ID aparece en la representación estructurada; y
- todos sus `check_terms` normalizados aparecen en el texto recuperado.

Se generará además una lista `ambiguous_items` para revisión manual cuando exista el ID pero falte algún término. Esto evita convertir una paráfrasis dudosa en un falso fallo automático.

## 6. Métricas

### Recall por tipo

\[
Recall_t = \frac{elementos\ recuperados\ del\ tipo\ t}{elementos\ originales\ del\ tipo\ t}
\]

### Recall ponderado

Pesos iniciales: constraint crítica = 5, decisión crítica = 4, constraint normal = 3, evidencia = 2 y resto = 1.

\[
WeightedRecall = \frac{\sum_i peso_i \cdot recuperado_i}{\sum_i peso_i}
\]

También se registrarán:

- palabras/caracteres del contexto activo;
- latencia y llamadas LLM;
- errores de parseo o transporte;
- IDs perdidos por ronda;
- coste, si el endpoint devuelve uso de tokens.

## 7. Matriz mínima de ejecuciones

| Escenario | Estrategia | Rondas | Repeticiones | Objetivo |
|---|---|---:|---:|---|
| E1 | Baseline | 5 | 3 | Observar degradación acumulada |
| E2 | Triage | 5 | 3 | Verificar constraints fijadas |
| E3 | Fake deterministic | 5 | 1 | Validar runner y métricas offline |

## 8. Interpretación

- No comparar directamente los resultados locales con los porcentajes divulgados del paper sin replicar su configuración.
- Un 100 % de constraints en triage demuestra la política, no que toda la memoria sea perfecta.
- Si aumenta mucho el contexto activo, se debe reportar el coste junto al recall.
- Los fallos de API quedan fuera del denominador y se presentan separadamente.

## 9. Salida JSON mínima

```json
{
  "run_id": "2026-08-28T150000Z",
  "dataset_hash": "...",
  "model": "...",
  "settings": {"rounds": 5, "target_words": 700},
  "rounds": [
    {
      "round": 1,
      "strategies": {
        "baseline": {"constraint_recall": 0.875, "lost_ids": ["C07"]},
        "triage": {"constraint_recall": 1.0, "lost_ids": []}
      }
    }
  ]
}
```

