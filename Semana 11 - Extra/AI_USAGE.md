# Tabla de uso de IA — Semana 11 extra

Convención: “agente” = asistente de código usado en esta sesión. Todas las salidas son reales; los comandos se ejecutaron desde la raíz del repo salvo que se indique `cd`.

| # | Qué se pidió | Qué respondió | Aceptado / Rechazado | Por qué | Evidencia (comando y salida) |
|---|---|---|---|---|---|
| 1 | Localizar la plantilla oficial del laboratorio extra y preparar el proyecto sin tocar el contrato. | Encontró `Hellscythe25/dae-s11-hooks-del-agente`, la copió en `Semana 11 - Extra/` sin `.git`, ejecutó `npm install` y tomó las líneas base. | **Aceptado** | Es el repo enlazado en el módulo; la guía y los scripts coinciden con el README de la plantilla. | `npm test` → `Tests 40 failed / 17 passed (57)`; `npm run test:ai` → `Tests 20 failed / 37 passed (57)`. Ver `evidence/test-*-antes.txt`. |
| 2 | Implementar `useDebounce` con el valor inicial correcto y temporizador cancelable. | `useState(value)` + un único `useEffect([value, delay])` con `clearTimeout` en la limpieza. | **Aceptado** | El input debe mostrar lo escrito al instante y la lista reaccionar a los 300 ms sin cambio. | `npm test -- useDebounce` → `Tests 10 passed (10)`. Antes: 4 pasaban / 6 fallaban. |
| 3 | Implementar `usePlans` con tres estados, `reload` estable e ignoro de respuestas viejas. | `requestRef` con id por petición, `useCallback([fetchPlans])` y limpieza que invalida el id. | **Aceptado** | Cubre error, carreras y StrictMode sin modificar pruebas ni cambiar la firma del hook. | `npm test -- usePlans` → `Tests 12 passed (12)`. Antes: 1 pasaba / 11 fallaban. |
| 4 | Implementar `useAgentRun` como máquina de estados con barrera R2 y aborto. | Un solo objeto de estado + refs, `AbortController`, R2 → `awaiting_approval`, `approve()` solo desde ahí, limpieza al desmontar. | **Aceptado** | Mantiene los hooks incondicionales aunque `runAgent` aparezca tarde, y evita el `done` accidental. | `npm test -- useAgentRun` → `Tests 18 passed (18)`. Antes: 4 pasaban / 14 fallaban. |
| 5 | Congelar la versión original de `src/ai/` antes de tocarla y generar el diff de comparación. | Commit dedicado `136638c` y diff `136638c..fe04a31` guardado como evidencia. | **Aceptado** | La rúbrica pide explícitamente el commit del estado original. | `git log --oneline` → `136638c chore(s11-extra): guardar version original de los hooks escritos por la IA`. |
| 6 | **Rechazar la versión de la IA** y proponer arreglos para sus seis fallos. | La IA devolvió hooks que “compilaban” pero: limpieza mal puesta, error no propagado, carreras, hooks condicionales, R2 sin aprobación y sin aborto al desmontar. | **Rechazada la versión original; aceptado el plan de corrección** | Rompía reglas de hooks y, lo más grave, permitía ejecutar R2 sin confirmación real. | Antes: `npm run test:ai` → `20 failed / 37 passed`. Después: `57 passed`. Diff del rechazo: `evidence/ai-rechazo-useAgentRun.diff`. |
| 7 | Corregir los seis fallos de `src/ai/` sin modificar pruebas ni la interfaz de los hooks. | Se reescribieron los tres archivos: cleanup en el mismo efecto, `cancelled`/id por petición, refs para `runAgent`, R2 → `awaiting_approval` y aborto en desmontaje. | **Aceptado** | 20 fallos desaparecen y el comportamiento queda alineado con los hooks propios. | `npm run test:ai` → `Test Files 5 passed (5)`, `Tests 57 passed (57)`. Ver `evidence/test-ai-despues.txt`. |
| 8 | Redactar el entregable con las 12 respuestas de revisión, conteos, árbol y explicación de seguridad; y esta tabla. | Documento `ENTREGABLE.md` + versión Word `ENTREGABLE.docx` + esta tabla. | **Aceptado** | Cubre los tres bloques pedidos y deja la bitácora de decisiones dentro del repo. | `git status --short` tras el commit final; `npm test` y `npm run test:ai` siguen en 57/57. |

## Diff del rechazo (extracto)

Archivo completo: `evidence/ai-rechazo-useAgentRun.diff`. Comando usado:

```bash
git diff 136638c..fe04a31 -- "Semana 11 - Extra/src/ai/useAgentRun.js"
```

Cambio crítico (la IA permitía `done` directo y hooks condicionales):

```diff
-  if (!runAgent) return { status: "idle", start() {}, approve() {}, reject() {} };
+  const runAgentRef = useRef(runAgent);
+  runAgentRef.current = runAgent;
...
-      update({ status: "done", plan, result, error: null });
+      update({
+        status: plan.risk === "R2" ? "awaiting_approval" : "done",
+        plan,
+        result,
+        error: null,
+      });
...
+  useEffect(() => () => {
+    controller.current?.abort();
+    controller.current = null;
+  }, []);
```

Nota: el estado original sigue recuperable con `git show 136638c:Semana\ 11\ -\ Extra/src/ai/useAgentRun.js`.
