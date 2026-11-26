# DAE — Extra S13: El carrito revisado por pruebas

**Alumna:** Yajaira Cerrón Mancilla  
**Curso:** Desarrollo de Aplicaciones Empresariales  
**Ciclo:** 4 · **Sección:** A · **Semana:** 13 · **Periodo:** 2026-2  
**Docente:** Michael Montgomery Rosell  
**Repositorio:** `https://github.com/fairuscmancilla-hash/DAE.git`, carpeta `Semana 13 - Extra/`

## 1. Desarrollo

### 1.1 Reglas leídas del README y resultado inicial

Las reglas de la tienda quedan resumidas en la tabla de `README.md`. Con mis
palabras: el dinero es `Decimal` redondeado a céntimos con mitad hacia arriba;
el precio lo decide el servidor y el cliente solo envía `sku` y `qty`; las
existencias se acumulan y `checkout` vuelve a comprobarlas antes de descontar;
hay un solo cupón por carrito; el IGV se calcula después del descuento; y quitar
más de lo que hay elimina la línea sin dejar cantidades negativas.

Ejecuté `python manage.py seed_shop` y luego `python manage.py test`. Con el
carrito de la IA (`SHOP_MODE=ai`) el resumen fue:

```text
Ran 27 tests in 0.059s
FAILED (failures=12)
```

Las 15 pruebas que pasaban son las del carrito del equipo y las de auditoría
(`shop/tests/test_audit.py`). Las de auditoría pasan porque consultan el catálogo
del servidor y usan `TeamCart` como oráculo, sin importar qué implementación
esté seleccionada en `SHOP_MODE`; por eso sirven como control desde el inicio.

**Captura del resultado:** `evidencias/resultado-inicial-ai.txt`,
`evidencias/duelo-inicial.txt`.

### 1.2 Catálogo puro, cantidades y precio

`shop/domain.py` guarda datos puros (diccionarios con `Decimal` y enteros), no
modelos de Django. Así las reglas se prueban sin base de datos ni navegador, y
el mismo oráculo se usa para la auditoría. `_qty` guarda únicamente la cantidad
por SKU: el precio no se guarda porque puede cambiar en el servidor y porque
guardarlo en el cliente permitiría que una petición manipulada fijara el cobro.
`shop/impl.py` lee `SHOP_MODE`: con `team` usa `cart_team.Cart` y con `ai` usa
`cart_ai.Cart`, sin tocar las pruebas.

**Código:** `shop/domain.py`, `shop/cart_team.py`, `shop/impl.py`.

### 1.3 Líneas, cantidades y pago

`add` valida entero positivo, comprueba `cantidad_actual + cantidad_nueva <= stock`
y actualiza `_qty`. `remove` resta y, si el resultado llega a cero o menos,
elimina la línea con `pop`, de modo que no queda una cantidad negativa que
restaría dinero del total. `lines` devuelve el precio del catálogo y el subtotal
por línea ya redondeado.

`checkout` comprueba **todas** las líneas antes de descontar ninguna, calcula el
recibo, descuenta existencias de una sola pasada y vacía el carrito. La segunda
comprobación es necesaria porque entre `add` y `checkout` otro cliente pudo
comprar las últimas unidades. Si dos clientes pagan al mismo tiempo las últimas
unidades sin bloqueo, los dos podrían pasar la comprobación y el stock quedar
negativo; en la API eso se mitiga con `select_for_update()` dentro de
`transaction.atomic()` y la comprobación final en `shop/api.py`.

**Pruebas:** `shop/tests/test_lines.py`, `shop/tests/test_stock.py`.

### 1.4 Dinero exacto

En el intérprete de Python:

```text
>>> 0.1 + 0.2
0.30000000000000004
>>> Decimal("0.1") + Decimal("0.2")
Decimal('0.3')
>>> round(0.845, 2)
0.84
>>> Decimal("0.845").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
Decimal('0.85')
```

Un `float` no puede guardar `0,845` porque 0,845 no es una fracción binaria
exacta: se almacena como 0,84499999999999997... y `round()` aplica además
redondeo al par, por lo que da `0,84`. La tienda usa `ROUND_HALF_UP`, es decir,
mitad hacia arriba, para cobrar `0,85`.

Cálculo manual para un mousepad con `BIENVENIDA10`:

| Concepto | Cálculo | Resultado |
|----------|---------|-----------|
| Subtotal | 8,45 × 1 | 8,45 |
| Descuento | `money(8,45 × 0,10) = money(0,845)` | 0,85 |
| IGV | `money((8,45 − 0,85) × 0,18) = money(1,368)` | 1,37 |
| Total | `money(8,45 − 0,85 + 1,37)` | **8,97** |

Coincide con `shop/tests/test_totals.py::test_mousepad_with_welcome_coupon_matches_the_manual_calculation`.

### 1.5 Cupones y cuerpo de la API

`apply_coupon` limpia espacios, convierte a mayúsculas y **reemplaza** el cupón
anterior. Un doble clic en «Aplicar cupón» o un reintento de red produce el
mismo descuento que una sola aplicación; acumular cupones abarataría el pedido
y la tienda perdería dinero.

`add_from_payload` exige un diccionario con `sku` de texto, delega en `add` y
nunca lee `payload["price"]`. Si el precio viniera del cliente, una petición
hecha a mano podría pagar 1,00 por un teclado de 49,90: ese es el fallo de
seguridad que no se ve en el navegador.

### 1.6 Llamadas manuales a la API

Con el servidor en `127.0.0.1:8000` y una sola sesión HTTP:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/cart/add/ -Method Post -ContentType 'application/json' -Body '{"sku":"MOUSEPAD","qty":1,"price":"0.01"}' -SessionVariable carrito
Invoke-RestMethod http://127.0.0.1:8000/api/cart/coupon/ -Method Post -ContentType 'application/json' -Body '{"code":"BIENVENIDA10"}' -WebSession $carrito
Invoke-RestMethod http://127.0.0.1:8000/api/cart/checkout/ -Method Post -ContentType 'application/json' -Body '{}' -WebSession $carrito
```

 Respuestas completas: `evidencias/api-manual.txt`. El `price` enviado como
`0.01` fue ignorado: el precio de la línea fue `8,45`, el descuento `0,85` y el
total `8,97`. Después del pago la línea desapareció y el stock bajó de 5 a 4.
**Captura del resultado:** `evidencias/capturas/01-api-get-vacio.png`.

### 1.7 Duelo y clasificación de los cinco fallos de la IA

`python manage.py duelo` antes de los arreglos:

| modo | pruebas | pasadas | fallidas | veredicto |
|------|---------|---------|----------|-----------|
| team | 27 | 27 | 0 | OK |
| ai | 27 | 15 | 12 | RECHAZAR |

Las 12 fallidas, agrupadas por archivo:

- `test_api.py`: `test_client_price_is_never_read`, `test_http_add_coupon_checkout_sequence`.
- `test_coupons.py`: `test_discount_cannot_exceed_subtotal`, `test_double_click_does_not_accumulate_discount`, `test_one_coupon_replaces_the_previous_one`.
- `test_lines.py`: `test_add_builds_a_line_and_remove_to_zero_deletes_it`, `test_remove_more_than_current_never_creates_negative_quantity`.
- `test_stock.py`: `test_add_counts_what_is_already_in_the_cart`.
- `test_totals.py`: `test_igv_is_calculated_after_discount`, `test_mousepad_with_welcome_coupon_matches_the_manual_calculation`, `test_total_is_always_decimal`, `test_totals_without_coupon`.

Clasificación con las líneas del commit original `371d8a0`:

| # | Archivo y línea | Prueba que lo detecta | Mensaje / diferencia | Causa | ¿Se ve a mano? |
|---|-----------------|-----------------------|----------------------|-------|----------------|
| 1 | `shop/cart_ai.py:56-93` (`subtotal`, `discount`, `igv`, `total`, `summary`) | `test_totals.py` (4 pruebas) | `8.45 != Decimal('8.45')`; `0.84` en vez de `0.85` | `float` + `round()` en vez de `Decimal` + `money()` | Sí, al conciliar caja: un céntimo no lanza error, aparece en el arqueo. |
| 2 | `shop/cart_ai.py:97-105` (`add_from_payload`) | `test_api.py` (2 pruebas) | `'0.01' != '8.45'` | El precio viene del cuerpo de la petición | **No se ve en el navegador**: solo con API a mano o prueba de API. Es el **fallo de seguridad**. |
| 3 | `shop/cart_ai.py:20-27` (`add`) | `test_add_counts_what_is_already_in_the_cart` | `StockError not raised` | Compara solo la cantidad entrante contra el stock | Sí: el cliente agrega 3 + 3 de un producto con stock 5 y el pedido no se puede servir. |
| 4 | `shop/cart_ai.py:30-35` (`remove`) | `test_lines.py` (2 pruebas) | `qty 0` queda como línea; `remaining = -3` | La línea nunca se borra al llegar a cero | Sí: el carrito muestra cantidades negativas y el total baja. |
| 5 | `shop/cart_ai.py:65-78` (`apply_coupon`, `discount`) | `test_coupons.py` (2 pruebas) | `'BIENVENIDA10, DAE5' != 'DAE5'`; `1.69 != 0.84` | Lista de cupones en vez de un solo cupón | Sí: doble clic en «Aplicar cupón» descuenta dos veces. |

**Evidencia:** `evidencias/duelo-inicial.txt`, `evidencias/resultado-inicial-ai.txt`,
`evidencias/auditoria-inicial.txt`.

### 1.8 Las cuatro preguntas de revisión aplicadas al código arreglado

| Pregunta | Línea que lo demuestra (`cart_ai.py` final) |
|----------|---------------------------------------------|
| ¿Todo el dinero es `Decimal` de principio a fin? | Líneas 45-52 (`subtotal`), 66-71 (`discount`), 73-75 (`igv`), 77-79 (`total`) y 81-91 (`summary` usa `str()` sobre `Decimal`, nunca `float`). |
| ¿El servidor es la única fuente del precio? | Líneas 28-43 (`lines` lee `_catalog`), 93-95 (`add_from_payload` delega en la regla revisada) y 126-135 (`from_dict` ignora el precio declarado). |
| ¿Cantidad y existencias se cumplen con cualquier secuencia? | Líneas 20-22 (`add` delega en la regla acumulada), 24-26 (`remove` delega y borra la línea) y 97-113 (`checkout` recomprueba antes de descontar). |
| ¿Repetir una acción da el mismo resultado? | Líneas 57-64 (`apply_coupon` reemplaza) y 143-146 (`restore_state` guarda un solo cupón). |

### 1.9 Arreglo de la versión de la IA

Guardé el original en el commit `371d8a0` y corregí un método por turno con
`SHOP_MODE=ai`, anotando fallos antes y después de cada compuerta:

| Turno | Método | Fallos antes → después | Veredicto |
|-------|--------|------------------------|-----------|
| 1 | `add_from_payload` | 12 → 12 | RECHAZAR (el precio ya no se lee; la misma prueba ahora falla por `float`) |
| 2 | `lines` | 12 → 12 | RECHAZAR (precio del servidor en las líneas) |
| 3 | `from_dict` | 12 → 12 | RECHAZAR (replay sin precio del cliente) |
| 4-7 | `subtotal`, `discount`, `igv`, `total` | 12 → 9 → 5 | RECHAZAR (los estados intermedios mezclaban `Decimal` y `float`; se corrigió el siguiente método) |
| 8 | `apply_coupon` | 5 → 3 | RECHAZAR |
| 9 | `add` | 3 → 2 | RECHAZAR |
| 10 | `remove` | 2 → 0 | ACEPTAR, exit 0 |
| 11 | `summary` | 0 → 0 | ACEPTAR (rechazo humano del turno 10 corregido) |
| 12-14 | `discount`, `public_state`, `restore_state` | 0 → 0 | ACEPTAR, exit 0 |

**Evidencia:** `evidencias/arreglos-ia.txt` y los archivos
`evidencias/gate-turno1.json` a `gate-turno14.json`. Después de todos los
arreglos, `python manage.py duelo` da 27/27 en ambos modos
(`evidencias/duelo-final.txt`).

### 1.10 Auditoría sin pantalla

`python manage.py audit_cart carts/*.json` con `SHOP_MODE=ai` produjo:

| Carrito | Hallazgo | Fallo relacionado |
|---------|----------|-------------------|
| `01-valid.json` | sin hallazgos | — |
| `02-rounding.json` | `TOTAL_MISMATCH` en descuento y total | 1, redondeo |
| `03-negative.json` | `BAD_QTY: NOTEBOOK has quantity -1` | 4, cantidad negativa |
| `04-overstock.json` | `OVER_STOCK: KEYBOARD asks 3 but stock is 2` | 3, existencias |
| `05-price.json` | `PRICE_MISMATCH` + tres `TOTAL_MISMATCH` | 2, precio del cliente |
| `06-coupon.json` | `MULTIPLE_COUPONS` + tres `TOTAL_MISMATCH` | 5, cupones acumulados |

**Evidencia:** `evidencias/auditoria-inicial.txt`,
`evidencias/auditoria-inicial-json.txt`, `evidencias/auditoria-final-ai.json.txt`.

`TOTAL_MISMATCH` significa que el carrito **declara** mal sus totales frente a
las reglas. `REPLAY_MISMATCH` significa que la **implementación activa** calcula
mal al repetir el carrito, aunque esté declarado bien. Antes de los arreglos,
`01-valid.json` estaba bien declarado pero la IA lo calculaba como `0.84` y
`8.98`: por eso aparecía solo `REPLAY_MISMATCH`. Después de los arreglos ya no
aparece ningún `REPLAY_MISMATCH`; quedan los hallazgos de los carritos mal
declarados, que son correctos.

Con `--json --strict`, un programa o agente lee `carts[].verdict`, `findings` y
el código de salida (`1` si hay rechazos). La auditoría **no sustituye** las
reglas del servidor: avisa después de que el cobro ocurrió; la regla en `add` y
`checkout` lo impide antes.

### 1.11 Compuerta sin pantalla

| Comando | Veredicto | exit |
|---------|-----------|------|
| `python manage.py gate --modo ai` (antes) | RECHAZAR, 12 fallos + `REPLAY_MISMATCH` | 1 |
| `python manage.py gate --modo ai` (después) | ACEPTAR, 0 fallos, sin hallazgos | 0 |
| `python manage.py gate --modo team` | ACEPTAR, 27/27 | 0 |
| `python manage.py gate --cart carts/03-negative.json` | RECHAZAR, `BAD_QTY` | 1 |
| `python manage.py gate --cart carts/04-overstock.json` | RECHAZAR, `OVER_STOCK` | 1 |

Con `--json`, un agente lee `verdict`, `tests.failing`, `tests.failing_names` y
`audit.findings`. Una implementación correcta debe rechazar los carritos 03 y
04 porque la cantidad negativa y el exceso de stock son reglas, no detalles de
presentación: rechazar no es un fallo de la compuerta, es la compuerta
funcionando.

El replay de la auditoría **no detecta** el fallo del precio del cliente: si el
carrito declara `1.00` y la IA usa ese precio, declaración y replay coinciden.
Quien lo detecta es la compuerta mediante `PRICE_MISMATCH`, que compara el
precio declarado con el catálogo del servidor, y la prueba de API
`test_client_price_is_never_read`.

**Evidencia:** `evidencias/gate-inicial-ai.json.txt`, `evidencias/gate-equipo.txt`,
`evidencias/gate-carrito03.txt`, `evidencias/gate-carrito04.txt`.

### 1.12 Agente bajo `AGENTS.md`

El contrato `AGENTS.md` permite un método por turno en `shop/cart_ai.py`, prohíbe
tocar pruebas, reglas ni carritos, y fija la compuerta en cero como terminado.
En el turno 10 la compuerta dio **ACEPTAR** con 0 fallos, pero la revisión
humana rechazó el diff por la pregunta 1: `summary()` todavía convertía cada
`Decimal` a `float` antes de formatearlo. El diff rechazado y su justificación
están en `evidencias/diff-rechazado.txt`; el turno 11 lo corrigió y volvió a
aceptar la compuerta.

### 1.13 Estructura del proyecto

```text
Semana 13 - Extra/
├── AGENTS.md
├── AI_USAGE.md
├── README.md
├── ENTREGABLE.md
├── manage.py
├── requirements.txt
├── config/          settings, urls, wsgi, asgi
├── shop/
│   ├── domain.py                 reglas puras y Decimal
│   ├── cart_team.py              carrito del equipo
│   ├── cart_ai.py                carrito de la IA (original en 371d8a0)
│   ├── impl.py                   selector SHOP_MODE
│   ├── api.py                    capa HTTP delgada
│   ├── models.py, admin.py       Product, Order, OrderLine
│   ├── management/commands/      seed_shop, duelo, audit_cart, gate
│   └── tests/                    test_lines, test_stock, test_totals,
│                                 test_coupons, test_api, test_audit
├── carts/           01 a 06, carritos declarados
└── evidencias/      capturas, comandos y resultados
```

**Captura de la estructura:** `evidencias/estructura-proyecto.txt`.

## 2. Tabla de uso de IA

| Pedido | Respuesta | Decisión | Motivo | Evidencia |
|--------|-----------|----------|--------|-----------|
| «Escribe un carrito de Django con líneas, stock, cupones y checkout que compile y responda.» | `shop/cart_ai.py`, con los cinco fallos. | Aceptado como material a revisar | No se integra al carrito del equipo; sirve para el duelo. | `duelo-inicial.txt` |
| «Corrige los cinco fallos, un método por turno, sin tocar pruebas ni reglas.» | 14 turnos con cambios en `shop/cart_ai.py`. | Aceptado al final | Cada turno se cerró con la compuerta; la final quedó en 0. | `arreglos-ia.txt`, `gate-turno*.json` |
| «Deja `summary()` como está, que las pruebas ya pasan.» | Mantenía `float(...)` en los totales. | **Rechazado** | Pregunta 1 del contrato: el dinero debe ser `Decimal` de principio a fin, aunque la compuerta estuviera en verde. | `diff-rechazado.txt`, `gate-turno10.json` |
| «Explica por qué la auditoría no sustituye las reglas del servidor.» | La auditoría detecta inconsistencias después del cobro; la regla lo impide antes. | Aceptado | Coincide con `add`, `checkout` y `audit_cart`. | `auditoria-final-ai.json.txt` |

## 3. Conclusiones

El carrito es lógica de negocio y debe escribirse contra pruebas, no contra una
pantalla. El dinero exacto exige `Decimal` en todas las capas: un solo `float`
en `summary()` basta para rechazar un diff aunque las pruebas pasen. El servidor
debe ser la única fuente del precio y de las existencias; el navegador no puede
ser la frontera de confianza. Las reglas repetibles —un cupón, cantidades sin
negativo, stock acumulado— se comprobaron con secuencias de acciones y con
reintentos. Las pruebas y la auditoría permitieron revisar al agente sin abrir
pantallas, y el contrato `AGENTS.md` más la compuerta convierten «compila y se
ve bien» en un criterio verificable. La auditoría avisa, pero solo la regla en
el servidor impide el cobro incorrecto; y la última palabra sobre el diff sigue
siendo humana.
