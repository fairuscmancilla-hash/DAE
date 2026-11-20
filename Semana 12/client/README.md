# Semana 12 — Cliente React de servicios web

Proyecto del Lab 11 (cartelera) más el cliente Axios del Laboratorio 12. Conserva la cartelera y añade una consola de la API de cuestionarios con sus tres estados, alta y borrado.

## Puesta en marcha

```powershell
# 1) Servidor (otra terminal): ver ../server/README.md
#    http://127.0.0.1:8001

# 2) Cliente
npm install
Copy-Item .env.example .env.local   # pega el token que imprime manage.py seed_quiz
npm run dev                         # http://127.0.0.1:5173
npm test
npm run build
```

Navegación de la aplicación:

- **Cartelera (Lab 11)**: proyecto acumulado.
- **Preguntas API**: `GET /api/questions/` con esqueleto de carga, tabla y banner de error con reintento.
- **Nueva pregunta**: formulario controlado con `POST /api/questions/`; muestra los errores 400 de la API y vuelve al listado sin recargar.

El borrado usa `DELETE /api/questions/{id}/` y refresca la lista con `reload()`.

## Puntos clave

- `src/lib/api.js`: única dirección base, cabecera `Token` y funciones `fetchExams`, `fetchQuestions`, `createQuestion`, `deleteQuestion`. Ningún componente escribe una URL.
- `src/hooks/useQuestions.js`: estados `loading | ready | error`, descarte de respuestas viejas y recarga tras borrar.
- `src/components/`: `QuestionsPage`, `QuestionForm`, `QuestionTable`, `LoadingSkeleton` y `ErrorBanner`.
- `src/test/`: pruebas del cliente y del hook (17 en total).

El entregable con capturas está en `../ENTREGABLE.md` y `../ENTREGABLE.docx`.
