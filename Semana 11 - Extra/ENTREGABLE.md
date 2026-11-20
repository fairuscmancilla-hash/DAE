# Laboratorio extra — Semana 11: Los hooks del agente

**Repositorio del equipo:** https://github.com/fairuscmancilla-hash/DAE.git
**Rama:** `main` · **Carpeta:** `Semana 11 - Extra/` · **Plantilla:** https://github.com/Hellscythe25/dae-s11-hooks-del-agente

## 0. Cómo ejecutar

```bash
cd "Semana 11 - Extra"
npm install
npm test          # modo team: src/hooks
npm run test:ai   # modo ai: src/ai
```

Contrato respetado: no se modificaron `src/test/`, `vite.config.js`, `package.json` ni los componentes ya escritos. Los cambios se limitan a `src/hooks/`, `src/ai/`, evidencias y documentación.

## 1. Commits (estado original de la IA incluido)

| Commit | Contenido |
|---|---|
| `8fceaa6` | Importación de la plantilla oficial (sin `src/hooks` ni `src/ai`). |
| `136638c` | **Estado original de la versión de la IA** antes de arreglarla. |
| `3d4e60a` | `useDebounce` propio. |
| `f6b3b44` | `usePlans` propio. |
| `ab06ebc` | `useAgentRun` propio. |
| `fe04a31` | Corrección de los seis fallos de `src/ai/`. |
| `…` | Entregable, tabla de IA y actualización del README. |

El commit exigido por la rúbrica es **`136638c`**: congela los tres hooks generados por la IA tal como vinieron en la plantilla. El diff del rechazo está en `evidence/ai-rechazo-useAgentRun.diff`.

## 2. Conteo de pruebas antes y después

### Modo `team` (`src/hooks`)

| Hook | Antes | Después |
|---|---|---|
| `useDebounce` | 4 pasan / 6 fallan (10) | **10 / 10** |
| `usePlans` | 1 pasa / 11 fallan (12) | **12 / 12** |
| `useAgentRun` | 4 pasan / 14 fallan (18) | **18 / 18** |
| Global | 17 pasan / 40 fallan (57) | **57 / 57** |

### Modo `ai` (`src/ai`)

| Archivo | Antes | Después |
|---|---|---|
| `useDebounce` | 5 / 10 | **10 / 10** |
| `usePlans` | 7 / 12 | **12 / 12** |
| `useAgentRun` | 11 / 18 | **18 / 18** |
| `App` (consume los hooks) | 6 / 7 | **7 / 7** |
| `Inbox` (consume los hooks) | 8 / 10 | **10 / 10** |
| Global | 37 pasan / 20 fallan (57) | **57 / 57** |

Salidas resumidas en `evidence/test-team-antes.txt`, `evidence/test-ai-antes.txt`, `evidence/test-team-despues.txt` y `evidence/test-ai-despues.txt`.

## 3. Revisiones del diff — cuatro preguntas por hook

### 3.1 `src/hooks/useDebounce.js`

1. **¿Está bien el orden y la forma de los hooks de arriba abajo?** Sí. Solo `useState` y `useEffect`, ambos incondicionales y al inicio; no hay retornos anticipados ni hooks dentro de conducciones o bucles. El valor inicial es `value`, de modo que el primer dibujado ya es correcto.
2. **¿Qué se limpia y cuándo?** El efecto devuelve `clearTimeout(timer)`. La limpieza corre antes de cada nuevo efecto (cambio de `value` o `delay`) y al desmontar. Por eso un valor intermedio nunca llega al estado: la prueba `vi.getTimerCount()` termina en 0.
3. **¿Se resuelven los tres estados y se ven en la interfaz?** Este hook no tiene estados de red; su análogo es *valor inicial → pendiente → valor asentado*. El dato asentado (`quietQuery`) se ve en el filtro de `Inbox`, mientras el input muestra `query` sin debounce. Los estados de red se cubren en `usePlans` y `useAgentRun`.
4. **¿Dónde vive el dato y por qué ahí?** En `Inbox`, el componente más bajo que necesita filtrar. No se subió a `App` porque `Header` no filtra; subirlo habría obligado a pasar dos valores por props sin beneficio.

### 3.2 `src/hooks/usePlans.js`

1. **¿Orden y forma de los hooks?** Sí: `useState`, `useRef`, `useCallback`, `useEffect`, siempre en ese orden y sin condicionales. `requestRef` se incrementa antes de pedir, así que cada `reload()` invalida la generación anterior.
2. **¿Qué se limpia y cuándo?** El efecto de carga limpia incrementando `requestRef.current`. Las respuestas que lleguen después de un `reload()` o del desmontaje se descartan por id. Las 4 pruebas de carrera/StrictMode lo confirman.
3. **¿Los tres estados y su reflejo en la UI?** Sí: `loading` → `PlansSkeleton`, `ready` → `PlanCard` dentro de `Inbox`, `error` → `ErrorBanner` con botón de reintento que llama a `reload()`. `plans` es `[]` en carga y error; `error` es `null` salvo en error.
4. **¿Dónde vive el dato?** En `App`, el ancestro común de `Header` (cuenta pendientes) e `Inbox` (lista). `reload` es estable con `useCallback([fetchPlans])`, así que el efecto no se dispara en cada render.

### 3.3 `src/hooks/useAgentRun.js`

1. **¿Orden y forma de los hooks?** Sí. Aunque `runAgent` puede llegar `undefined` en el primer render y aparecer después, **todos** los hooks se ejecutan siempre; el valor se lee desde `runAgentRef.current`, actualizado en cada render. No hay `if (...) return` antes de un hook. Esa es precisamente la prueba que la versión de la IA rompía.
2. **¿Qué se limpia y cuándo?** `AbortController` por ejecución; `reject()` aborta en `running` y `awaiting_approval`; el `useEffect` de desmontaje aborta lo que quede. El `.then` comprueba `signal.aborted` y la identidad del controlador, así que una respuesta tardía no muta el estado.
3. **¿Estados y reflejo en la UI?** `idle`, `running`, `awaiting_approval`, `done` y `error`, todos dibujados por `RunPanel`. Un plan **R2** termina en `awaiting_approval` y solo pasa a `done` con `approve()`; el botón Confirmar y aplicar no aparece antes. Las 18 pruebas pasan.
4. **¿Dónde vive el dato?** En `RunPanel`, porque nadie más necesita el resultado de la ejecución. Las decisiones de aprobación viven un nivel arriba (`App`) porque también las cuenta `Header`; el hook no decide eso, solo expone events.

## 4. Parte 4 — versión de la IA: seis fallos encontrados y corregidos

| # | Archivo | Fallo | Evidencia / prueba |
|---|---|---|---|
| 1 | `ai/useDebounce` | Limpieza en un `useEffect([])` separado: al cambiar el texto no se cancelaba el temporizador anterior y se devolvían valores intermedios. | 5 de 10 fallaban. |
| 2 | `ai/usePlans` | `.catch` solo hacía `console.error`: `status` se quedaba en `loading` y `error` en `null`. | Prueba “si falla, lo dice”. |
| 3 | `ai/usePlans` | Sin bandera de cancelación: una respuesta vieja podía sobrescribir la nueva tras `reload()` o desmontaje. | Pruebas de carrera y StrictMode. |
| 4 | `ai/useAgentRun` | `if (!runAgent) return {...}` antes de los hooks: número de hooks distinto entre renders. | 1 error de reglas de hooks. |
| 5 | `ai/useAgentRun` | Plan R2 pasaba directo a `done`: la aprobación del usuario nunca era obligatoria. | Prueba “R2 espera aprobación”. |
| 6 | `ai/useAgentRun` | Sin limpieza al desmontar: un resultado tardío actualizaba un componente muerto. | Prueba “no actualiza tras desmontar”. |

Diff completo del rechazo: `evidence/ai-rechazo-useAgentRun.diff` (de `136638c` a `fe04a31`).

## 5. Árbol de componentes con el dato de cada nivel

```
App                                  estado: {status, plans, error} de usePlans;
│                                    decisions[id] = approved|rejected; network.failing
├── Header                           recibe: pending = plans sin decisión, failing, onRetry
├── ErrorBanner                      recibe: error de usePlans + reload()
├── PlansSkeleton                    se dibuja solo cuando status === "loading"
└── Inbox                            recibe: plans, decisions, onDecide, runAgent
    │                                estado propio: query (texto escrito)
    │                                dato derivado: quietQuery = useDebounce(query, 300)
    ├── PlanCard (por plan)          recibe: plan, onDecide; sin estado propio
    │   └── HashConfirm (solo R2)    recibe: plan_hash; exige escribir el hash exacto
    └── RunPanel                     recibe: approvedPlans, runAgent
        │                            estado: {status, plan, result, error} de useAgentRun
        └── Button                   Ejecutar / Cancelar / Confirmar y aplicar / Descartar
```

**Dato por nivel:** la red vive en `App`; el texto del buscador en `Inbox`; la decisión en `App` (porque `Header` la cuenta); la ejecución en `RunPanel`; la tarjeta y el botón no guardan estado. Ningún hook sube un estado “por si acaso”.

## 6. ¿Por qué esta interfaz NO es la frontera de seguridad?

Porque es código del cliente y un atacante no está obligado a usarla: puede abrir DevTools, llamar al endpoint directamente con `curl`, modificar el bundle, falsificar el estado de React o reproducir el `plan_hash` de un plan R2 sin pasar por `HashConfirm`. Incluso un debounce o un botón desactivado son solo comodidades, no autorizaciones.

La barrera real debe estar en el servidor:

1. Recomputar `plan_hash` desde una representación canónica de `op + target + params`, no fiarse del hash que llega.
2. Exigir una aprobación explícita ligada a la sesión autenticada, al usuario y al hash **y** a la versión actual del objetivo (ETag/versión), con caducidad corta y un solo uso.
3. Verificar permisos del usuario sobre ese objetivo antes de ejecutar; rechazar R2 si falta el token aunque el cliente diga `status: done`.
4. Volver a hacer un *dry run* en servidor y auditar quién aprobó qué.
5. Tratar el contenido del objetivo (por ejemplo P-02, texto hostil) como dato: escaparlo al renderizar y validarlo también en servidor.

El hook `useAgentRun` evita accidentes y hace explícito el flujo en la UI; **no** sustituye esas comprobaciones. Si el backend aceptara `{"approved": true}` sin verificar la firma, el “C” de `HashConfirm` sería decoración. Por eso la conclusión de la guía es: *la aprobación se verifica donde se aplica el cambio, no donde se pinta el botón*.

## 7. Cierre

Ambos modos terminan en **57/57**. El contrato de la plantilla se respetó, el estado original de la IA quedó congelado en `136638c`, y cada rechazo quedó documentado con comando, salida y diff.
