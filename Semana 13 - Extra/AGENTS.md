# AGENTS.md — contrato para el agente del carrito

Este archivo rige a cualquier asistente o agente de IA que trabaje en este
repositorio. El objetivo no es que el carrito «se vea bien», sino que pase el
oráculo de pruebas y la compuerta sin pantalla.

## Alcance permitido

- Trabaja **un método por turno** en `shop/cart_ai.py`.
- Puedes recibir como contexto únicamente ese archivo y el archivo de pruebas
  relacionado (`shop/tests/test_lines.py`, `test_stock.py`, `test_totals.py`,
  `test_coupons.py` o `test_api.py`).
- No cambies `shop/domain.py`, `shop/cart_team.py`, las pruebas, los carritos
  `carts/*.json` ni los comandos de auditoría o compuerta.
- No escribas credenciales ni valores de precio en el cliente.

## Reglas que debes respetar

1. Todo el dinero es `Decimal` de principio a fin y se redondea con `money()`.
2. El servidor es la única fuente del precio: `add_from_payload` nunca lee
   `payload["price"]`.
3. Toda regla de cantidad y existencias se cumple con cualquier secuencia de
   acciones: `add` acumula, `remove` borra la línea al llegar a cero y
   `checkout` vuelve a comprobar antes de descontar.
4. Repetir una acción (doble clic, reintento) da el mismo resultado: un solo
   cupón por carrito.

## Definición de terminado

Un turno termina solo cuando:

```powershell
python manage.py gate --modo ai --cart carts/01-valid.json
```

devuelve `VEREDICTO: ACEPTAR` y código de salida `0`. Si la compuerta está en
rojo, no digas que terminaste: pega la salida y continúa con el siguiente
método. La última palabra sobre el diff la tiene una persona con las cuatro
preguntas de revisión anteriores.
