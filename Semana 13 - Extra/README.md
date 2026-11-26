# Extra S13 — El carrito revisado por pruebas

 Laboratorio extra de **Desarrollo de Aplicaciones Empresariales**, semana 13.
 Aquí el carrito es lógica pura de servidor: se escribe contra pruebas, se audita
 sin abrir pantalla y se revisa el código que propone una IA con una compuerta.

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_shop
python manage.py test shop.tests
```

La semilla crea cuatro productos. El precio y las existencias viven en el
servidor; el cliente solo envía `sku` y `qty`.

## Reglas de la tienda

| Regla | Qué dice con mis palabras |
|-------|---------------------------|
| Dinero exacto | Todo importe se calcula con `Decimal` y se redondea a céntimos con `ROUND_HALF_UP`. Nunca se usa `float`: `0.845` debe cobrarse como `0.85`. |
| Precio del servidor | El precio sale del catálogo del servidor. El cuerpo de la petición no puede traer `price`; si llegara, se ignora. |
| Existencias | `add` suma lo ya agregado con lo nuevo y rechaza la operación si pasa del stock. `checkout` vuelve a comprobar todas las líneas antes de descontar nada, así que el stock nunca baja de cero. |
| Cupón | Hay un solo cupón por carrito: aplicarlo otra vez lo reemplaza. El código se limpia de espacios y se convierte a mayúsculas. El descuento nunca supera el subtotal. |
| Impuesto | El IGV de 18 % se calcula después del descuento y también se redondea con `Decimal`. |
| Quitar | Quitar una cantidad mayor que la existente elimina la línea; nunca queda una cantidad negativa que reste dinero del total. |

Fórmula usada por las pruebas, con el carrito de un mousepad y `BIENVENIDA10`:

```text
subtotal = 8.45
descuento = money(8.45 × 0.10) = money(0.845) = 0.85
igv = money((8.45 - 0.85) × 0.18) = money(1.368) = 1.37
total = money(8.45 - 0.85 + 1.37) = 8.97
```

## Arquitectura

- `shop/domain.py`: catálogo puro, cupones, `Decimal`, `money()` y errores.
- `shop/cart_team.py`: carrito del equipo, escrito contra las pruebas.
- `shop/cart_ai.py`: carrito propuesto por la IA, con cinco fallos documentados.
- `shop/impl.py`: selecciona la implementación con `SHOP_MODE` (`team` o `ai`).
- `shop/api.py`: capa delgada que traduce HTTP a llamadas del carrito.
- `shop/management/commands/`: semillas, duelo, auditoría y compuerta.
- `carts/`: seis carritos declarados para la auditoría sin pantalla.

## Pruebas y compuertas

```powershell
# Carrito del equipo
python manage.py test shop.tests

# Carrito de la IA
$env:SHOP_MODE = "ai"
python manage.py test shop.tests
Remove-Item Env:SHOP_MODE

# Duelo, auditoría y compuerta
python manage.py duelo
python manage.py audit_cart carts/*.json
python manage.py audit_cart carts/*.json --replay --json --strict
python manage.py gate --modo team
python manage.py gate --modo ai --json
python manage.py gate --cart carts/03-negative.json
```

`gate` devuelve `0` para **ACEPTAR** y `1` para **RECHAZAR**. Con `--json`
imprime `verdict`, `tests.failing` y `audit.findings`, que son los campos que
leería un agente para decidir qué arreglar.

## API

| Método | Ruta | Cuerpo | Respuesta |
|--------|------|--------|-----------|
| GET | `/api/cart/` | — | Resumen con líneas, subtotal, descuento, IGV y total. |
| POST | `/api/cart/add/` | `{"sku":"MOUSEPAD","qty":1,"price":"0.01"}` | `201` con el resumen. El `price` se ignora. |
| POST | `/api/cart/coupon/` | `{"code":" bienvenida10 "}` | `200` con el resumen y un solo cupón. |
| POST | `/api/cart/checkout/` | `{}` | `201` con el recibo; descuenta existencias y vacía el carrito. |

Códigos de error: `400` petición mala o cupón inválido, `404` SKU desconocido,
`409` existencias insuficientes.

Ejemplo con `Invoke-RestMethod`:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/cart/add/ -Method Post -ContentType 'application/json' -Body '{"sku":"MOUSEPAD","qty":1,"price":"0.01"}'
Invoke-RestMethod http://127.0.0.1:8000/api/cart/coupon/ -Method Post -ContentType 'application/json' -Body '{"code":"BIENVENIDA10"}'
Invoke-RestMethod http://127.0.0.1:8000/api/cart/checkout/ -Method Post -ContentType 'application/json' -Body '{}'
```

## Contrato del agente

`AGENTS.md` fija el contrato: un método por turno, solo `shop/cart_ai.py`, sin
tocar pruebas ni reglas, y la compuerta en cero como criterio de terminado.
`AI_USAGE.md` registra cada pedido, respuesta, decisión y evidencia.
