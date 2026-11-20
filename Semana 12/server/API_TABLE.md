# Tabla de la API — Cuestionarios

Base: `http://127.0.0.1:8000/api/` · Autenticación: `Authorization: Token <token>` · Paginación: 5 por página.

## Exámenes (`/api/exams/`)

| Recurso | Dirección | Método | Cuerpo de ejemplo | Respuesta esperada | Código |
|---|---|---|---|---|---|
| Listar exámenes | `/api/exams/` | GET | — | `{"count": 2, "results": [{"id":1,"title":"Django · ORM","created_at":...,"question_count":4}, ...]}` | 200 |
| Detalle de un examen | `/api/exams/{id}/` | GET | — | `{"id":1,"title":"Django · ORM","created_at":...,"question_count":4}` | 200 |
| Eliminar examen | `/api/exams/{id}/` | DELETE | — | (sin contenido) | 204 |

## Preguntas (`/api/questions/`)

| Recurso | Dirección | Método | Cuerpo de ejemplo | Respuesta esperada | Código |
|---|---|---|---|---|---|
| Listar preguntas | `/api/questions/` | GET | — (filtros: `?exam=1`, `?search=texto`, `?page=2`) | `{"count":8,"next":...,"results":[{"id":1,"exam":1,"text":...,"choices":[...],"created_at":...}]}` | 200 |
| Detalle de una pregunta | `/api/questions/{id}/` | GET | — | `{"id":1,"exam":1,"text":...,"choices":[...],"created_at":...}` | 200 |
| Crear pregunta | `/api/questions/` | POST | `{"exam":1,"text":"¿Qué es REST?","choices":[{"text":"Un estilo","is_correct":true},{"text":"Un lenguaje","is_correct":false}]}` | `{"id":9,"exam":1,"text":"¿Qué es REST?","choices":[...],"created_at":...}` | 201 |
| Modificar parcialmente | `/api/questions/{id}/` | PATCH | `{"text":"Nuevo enunciado"}` | Objeto pregunta con `choices` conservadas | 200 |
| Eliminar pregunta | `/api/questions/{id}/` | DELETE | — | (sin contenido) | 204 |

## Errores esperados

| Caso | Dirección | Método | Cuerpo | Código | Mensaje |
|---|---|---|---|---|---|
| Campo obligatorio ausente | `/api/questions/` | POST | sin `text` | 400 | `{"text":["This field is required."]}` |
| Tipo incorrecto | `/api/questions/` | POST | `exam` como texto | 400 | error de validación de DRF |
| Validación de opción correcta | `/api/questions/` | POST | dos `is_correct:true` | 400 | `"Debe haber exactamente una opción correcta."` |
| Sin token | `/api/exams/` | GET | — | 401 | — |
| Token inválido | `/api/exams/` | GET | — | 401 | — |
| Agente intenta borrar | `/api/questions/{id}/` | DELETE | token del agente | 403 | — |
| Recurso inexistente | `/api/questions/99999/` | GET | — | 404 | — |
