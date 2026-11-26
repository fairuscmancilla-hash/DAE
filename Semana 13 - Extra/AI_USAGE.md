# Uso de IA

 Registro de cada pedido a un asistente o agente de IA durante este laboratorio.
 Las decisiones se justifican con una prueba o con una de las cuatro preguntas
 de revisión del contrato `AGENTS.md`.

| Pedido | Respuesta de la IA | Decisión | Motivo | Evidencia |
|--------|--------------------|----------|--------|-----------|
| «Escribe un carrito de Django con líneas, stock, cupones y checkout que compile y responda.» | Entregó `shop/cart_ai.py`: funciona en el caso feliz, pero usa `float`, toma el precio del cuerpo, no acumula stock, deja cantidades negativas y acumula cupones. | Aceptado como **sujeto a revisión** | Es el material a auditar; no se integra al carrito del equipo. | `python manage.py duelo` → IA con 12 fallos; `evidencias/duelo-inicial.txt`. |
| «Corrige los cinco fallos del carrito de la IA, un método por turno, sin tocar las pruebas.» | Propuso cambios en `shop/cart_ai.py`, uno por fallo. | Aceptado después de la compuerta | Cada turno se cerró con `gate --modo ai` hasta código `0`. | `evidencias/arreglos-ia.txt`; sección del entregable. |

> La tabla se amplía al final con el diff rechazado por revisión humana aunque
> la compuerta lo aceptara.
