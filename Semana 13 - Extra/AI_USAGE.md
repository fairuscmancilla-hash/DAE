# Uso de IA

 Registro de cada pedido a un asistente o agente de IA durante este laboratorio.
 Las decisiones se justifican con una prueba o con una de las cuatro preguntas
 de revisión del contrato `AGENTS.md`.

| Pedido | Respuesta de la IA | Decisión | Motivo | Evidencia |
|--------|--------------------|----------|--------|-----------|
| «Escribe un carrito de Django con líneas, stock, cupones y checkout que compile y responda.» | Entregó `shop/cart_ai.py`: funciona en el caso feliz, pero usa `float`, toma el precio del cuerpo, no acumula stock, deja cantidades negativas y acumula cupones. | Aceptado como **sujeto a revisión** | Es el material a auditar; no se integra al carrito del equipo. | `python manage.py duelo` → IA con 12 fallos; `evidencias/duelo-inicial.txt`. |
| «Corrige los cinco fallos del carrito de la IA, un método por turno, sin tocar las pruebas.» | Propuso 14 turnos de cambio en `shop/cart_ai.py`, uno por método. | Aceptado al final | Cada turno se cerró con `gate --modo ai`; el último quedó en `ACEPTAR`, exit `0`. | `evidencias/arreglos-ia.txt`; `evidencias/gate-turno14.json`. |
| «Deja `summary()` como está: las pruebas ya pasan y la compuerta está en verde.» | Mantenía `float(self.subtotal())` y `float(self.total())` al formatear el recibo. | **Rechazado** | Pregunta 1 del contrato: todo el dinero debe ser `Decimal` de principio a fin. La compuerta no evalúa esa decisión de diseño. | `evidencias/diff-rechazado.txt`; `evidencias/gate-turno10.json`. |
| «Explica por qué la auditoría no sustituye las reglas del servidor.» | Respondió que la auditoría avisa después del cobro y la regla lo impide antes. | Aceptado | Coincide con `add`, `checkout` y con la comparación `PRICE_MISMATCH` de la compuerta. | `evidencias/auditoria-final-ai.json.txt`; `evidencias/gate-carrito05.txt`. |
