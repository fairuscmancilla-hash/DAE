# Laboratorio 12 — Servicios Web

**Nombre del alumno:** Yajaira  
**Curso:** Desarrollo de Aplicaciones Empresariales · 4.º ciclo · Sección A  
**Docente:** Michael Montgomery Rosell  
**Semana:** 12 · **Fecha:** 20/11/2026  
**Título del desarrollo:** Integración de la API de cuestionarios de Django con un cliente React mediante Axios, CORS y gestión de los tres estados de la petición.

---

## 1. Desarrollo

### 1.1 Direcciones comprobadas en el navegador

El servidor se levantó en `http://127.0.0.1:8001` porque el puerto 8000 estaba ocupado por otro proceso del equipo. El cliente React se sirve en `http://127.0.0.1:5173`.

| Recurso | Método | Dirección consumida | Uso en la interfaz |
|---|---|---|---|
| Exámenes | GET | `/api/exams/` | Llena el selector del formulario de alta. |
| Preguntas | GET | `/api/questions/` | Dibuja la tabla del listado al montar la página. |
| Preguntas | POST | `/api/questions/` | Envía el formulario controlado de nueva pregunta. |
| Pregunta | DELETE | `/api/questions/{id}/` | Elimina la fila y vuelve a cargar la lista. |

La respuesta de `/api/exams/` se comprobó en el navegador con `Authorization: Token <token de la persona>` y devolvió `200 OK` con `count: 2`.

### 1.2 Configuración del servidor (CORS)

En `server/config/settings.py` se añadió la aplicación, el middleware inmediatamente después del de seguridad y una lista explícita de orígenes. No se usa el comodín `*`.

```python
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "corsheaders",
    "rest_framework",
    ...
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = False
```

El preflight desde el origen de React responde `200` y devuelve `access-control-allow-origin: http://127.0.0.1:5173`. Se añadieron tres pruebas automáticas en `server/quiz/tests/test_cors.py`: orígenes explícitos sin comodín, preflight permitido y preflight rechazado para `http://evil.example`.

### 1.3 Cliente de la API en un solo módulo

`client/src/lib/api.js` concentra la dirección base, el token y las tres operaciones. Ningún componente escribe una URL.

```js
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";
const token = import.meta.env.VITE_QUIZ_TOKEN || "";

export const api = axios.create({
  baseURL: `${baseURL}/api/`,
  headers: {
    Authorization: `Token ${token}`,
    "Content-Type": "application/json",
  },
});

export async function fetchExams() {
  const { data } = await api.get("exams/");
  return data.results;
}

export async function fetchQuestions() {
  const { data } = await api.get("questions/");
  return { items: data.results, count: data.count };
}

export async function createQuestion(payload) {
  const { data } = await api.post("questions/", payload);
  return data;
}

export async function deleteQuestion(id) {
  await api.delete(`questions/${id}/`);
}
```

Además, `describeApiError()` convierte los errores 400, 401/403, 404 y de red en mensajes legibles para la interfaz, incluidos los objetos anidados de validación de DRF.

### 1.4 Listado con tres estados

`client/src/hooks/useQuestions.js` lanza la petición GET al montar (a través de `useEffect`), guarda `loading | ready | error`, descarta respuestas desactualizadas y expone `reload()` y `remove(id)`.

```js
const load = useCallback(() => {
  const requestId = ++requestRef.current;
  setState(LOADING);

  fetchQuestions().then(
    ({ items, count }) => {
      if (requestId === requestRef.current) {
        setState({ status: "ready", items, count, error: null });
      }
    },
    (error) => {
      if (requestId === requestRef.current) {
        setState({ status: "error", items: [], count: 0, error });
      }
    },
  );
}, []);

useEffect(() => {
  load();
  return () => { requestRef.current += 1; };
}, [load]);

const remove = useCallback(async (id) => {
  await deleteQuestion(id);
  load();
}, [load]);
```

`QuestionsPage.jsx` decide qué dibujar según el estado:

```jsx
{status === "loading" && <LoadingSkeleton />}
{status === "error" && <ErrorBanner message={describeApiError(error)} onRetry={reload} />}
{status === "ready" && (
  <>
    <p className="api-count">{count} pregunta(s) recibidas sin recargar la página.</p>
    <QuestionTable items={items} onDelete={handleDelete} />
  </>
)}
```

### 1.5 Alta y borrado

El formulario usa entradas controladas y `onSubmit` con `preventDefault()`. Al terminar el `POST`, `onNavigate("questions")` vuelve al listado, que vuelve a pedir los datos y refleja el cambio sin recargar el navegador.

```jsx
async function submit(event) {
  event.preventDefault();
  setError(null);
  const payload = {
    exam: Number(form.exam),
    text: form.text,
    choices: [
      { text: form.first, is_correct: form.correct === "first" },
      { text: form.second, is_correct: form.correct === "second" },
    ],
  };
  try {
    await createQuestion(payload);
    onNavigate("questions");
  } catch (err) {
    setError(describeApiError(err));
  }
}
```

El borrado confirma la acción, llama a `deleteQuestion(id)` y ejecuta `load()` al terminar:

```jsx
async function handleDelete(id) {
  if (!window.confirm(`¿Eliminar la pregunta #${id}?`)) return;
  try {
    await remove(id);
  } catch (err) {
    window.alert(describeApiError(err));
  }
}
```

---

## 2. Captura del resultado

### 2.1 Listado con datos desde la API

![Listado de preguntas obtenido con Axios](evidencias/01-listado-api.png)

*Figura 1.* La tabla muestra las preguntas devueltas por `GET /api/questions/`; el contador indica `8 pregunta(s) recibidas sin recargar la página`.

### 2.2 Alta de una pregunta

![Alta de pregunta](evidencias/06-crear-pregunta.png)

*Figura 2.* Después de enviar el formulario, la aplicación vuelve al listado y el contador pasa a `10 pregunta(s)` (dos ejecuciones de la prueba acumuladas antes de restaurar la semilla en 8).

### 2.3 Borrado de una pregunta

![Borrado de pregunta](evidencias/07-eliminar-pregunta.png)

*Figura 3.* El botón **Eliminar** llama al `DELETE` y la lista se refresca: el contador baja de 10 a 9 sin recargar.

---

## 3. Explicación del resultado

El servidor del Laboratorio 8 se reutilizó como API del Laboratorio 12. `django-cors-headers` permite que el navegador acepte las peticiones del origen de React: se autorizan únicamente `localhost:5173` y `127.0.0.1:5173`, nunca todos los orígenes. El middleware se colocó antes del manejo común para que pueda responder al preflight `OPTIONS` con las cabeceras `Access-Control-Allow-Origin`, `Access-Control-Allow-Headers` y `Access-Control-Allow-Methods`.

El cliente conserva la cartelera del Laboratorio 11 y añade dos vistas accedidas desde la barra superior: **Preguntas API** y **Nueva pregunta**. Toda la comunicación HTTP pasa por `src/lib/api.js`, que crea una instancia de Axios con la dirección base y la cabecera `Authorization: Token …`. Así, cambiar el puerto de Django no obliga a tocar los componentes.

La página de listado modela explícitamente los tres estados. Mientras llega la respuesta se ve un esqueleto animado (`aria-busy="true"`); si llegan datos se renderiza la tabla con ID, examen, enunciado, opciones y acción de borrado; si falla la petición se muestra un banner con el mensaje leído del error y un botón **Reintentar**. Para evitar que una respuesta antigua sobrescriba una más reciente, cada petición lleva un identificador y solo el último actualiza el estado.

El formulario de alta mantiene cada campo en estado de React, previene el envío tradicional del navegador, construye el cuerpo con las dos opciones y la correcta, y navega de vuelta al listado cuando el `POST` termina. Los errores 400 de la API se muestran dentro del propio formulario, sin perder lo escrito. El borrado usa el identificador de la fila, pide confirmación y vuelve a cargar la lista, de modo que la interfaz refleja el cambio sin una recarga manual.

Los dos errores provocados confirman que no aparece una pantalla en blanco: al retirar el origen autorizado, el navegador bloquea la petición por CORS y se ve el banner; al apagar Django con React abierto, la petición termina en `net::ERR_CONNECTION_REFUSED` y se ve el mismo estado de error con la opción de reintento. Después de cada prueba se restauró la configuración normal y la base semilla (`manage.py seed_quiz`).

---

## 4. Tabla de la pantalla

| Petición al entrar | Estado de carga | Estado con datos | Estado de error |
|---|---|---|---|
| `GET /api/questions/` lanzado por `useEffect` al montar `QuestionsPage`. | `LoadingSkeleton`: mensaje «Cargando preguntas desde la API…» y cuatro filas de esqueleto con `aria-busy`. | `QuestionTable` con ID, examen, enunciado, opciones (la correcta en verde) y botón **Eliminar**; encima, el contador total. | `ErrorBanner` con mensaje descriptivo y botón **Reintentar** que vuelve a llamar a `load()`. |

### Capturas de los errores provocados

**a) CORS: origen retirado**

![Error de CORS](evidencias/03-error-cors.png)

Mensaje de la consola del navegador:

```text
Access to XMLHttpRequest at 'http://127.0.0.1:8002/api/questions/'
from origin 'http://127.0.0.1:5174' has been blocked by CORS policy:
Response to preflight request doesn't pass access control check:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
net::ERR_FAILED
```

**b) Validación: campo obligatorio vacío**

![Error de validación](evidencias/04-error-validacion.png)

```text
La API rechazó los datos. text: Este campo no puede estar en blanco. ·
choices: Este campo no puede estar en blanco. Este campo no puede estar en blanco.
HTTP 400 en /api/questions/
```

**c) Servidor de Django apagado**

![Servidor apagado](evidencias/05-servidor-apagado.png)

```text
[requestfailed] http://127.0.0.1:8001/api/questions/ :: net::ERR_CONNECTION_REFUSED
Interfaz: No se pudo conectar con la API. Revisa que Django esté encendido
y que el origen esté autorizado (CORS).
```

---

## 5. Casos de prueba

| # | Caso | Acción | Resultado esperado | Resultado obtenido | Evidencia |
|---|---|---|---|---|---|
| 1 | Preflight CORS permitido | `OPTIONS /api/exams/` con `Origin: http://127.0.0.1:5173` | `200` con cabecera CORS del origen | `200`, `access-control-allow-origin: http://127.0.0.1:5173` | `evidencias/comandos.txt` |
| 2 | Preflight CORS rechazado | Prueba con `Origin: http://evil.example` | Sin cabecera CORS | Sin `Access-Control-Allow-Origin` | `server/quiz/tests/test_cors.py` |
| 3 | API base responde | `GET /api/exams/` con token | `200`, 2 exámenes | `count: 2` | `evidencias/comandos.txt` |
| 4 | Carga de la lista | Entrar en **Preguntas API** con la respuesta retrasada | Esqueleto visible | `role="status"`, `aria-busy="true"` | `evidencias/02-estado-carga.png` |
| 5 | Datos en pantalla | Terminar la petición | Tabla y contador | 5 filas visibles de la página 1; contador 8 | `evidencias/01-listado-api.png`, `resultado-listado.txt` |
| 6 | Alta | Enviar formulario válido | `POST 201`, volver al listado, contador aumenta | De 8 a 9 y luego a 10 en la segunda ejecución | `evidencias/06-crear-pregunta.png`, `resultado-crud.txt` |
| 7 | Borrado | Clic en **Eliminar** y confirmar | `DELETE 204`, lista actualizada | Contador de 10 a 9 sin recargar | `evidencias/07-eliminar-pregunta.png`, `resultado-crud.txt` |
| 8 | Validación | Enviar enunciado vacío | `400` y mensaje en el formulario | Mensaje de DRF visible en rojo | `evidencias/04-error-validacion.png`, `comandos.txt` |
| 9 | CORS roto | Quitar el origen autorizado | Error en consola y banner en pantalla | `net::ERR_FAILED`, banner visible | `evidencias/03-error-cors.png`, `console-cors.txt` |
| 10 | Servidor apagado | Detener Django con React abierto | Error en pantalla, no hoja en blanco | `net::ERR_CONNECTION_REFUSED`, banner visible | `evidencias/05-servidor-apagado.png`, `resultado-servidor-apagado.txt` |
| 11 | Pruebas del servidor | `python manage.py test` | Todas en verde | **64 pruebas, OK** | `evidencias/comandos.txt` |
| 12 | Pruebas del cliente | `npm test` | Todas en verde | **5 archivos, 17 pruebas** | `evidencias/comandos.txt` |
| 13 | Build de producción | `npm run build` | Compila sin errores | 2226 módulos, ~343 kB JS | `evidencias/comandos.txt` |

> Las filas 6 y 7 corresponden a dos ejecuciones de la prueba automatizada de navegador; al terminar se volvió a ejecutar `manage.py seed_quiz` para dejar la base en su estado original de 8 preguntas.

---

## 6. Captura de la estructura del proyecto en el editor

![Estructura del proyecto](evidencias/08-estructura-proyecto.png)

*Figura 4.* `server/` contiene la API del Laboratorio 8 con CORS y la prueba nueva; `client/` contiene la cartelera del Laboratorio 11 más el módulo Axios, el hook de estados, los componentes de la consola y sus pruebas; `evidencias/` guarda las capturas y salidas reales.

---

## 7. Cómo levantar ambos proyectos

```powershell
# Terminal 1 — servidor
cd "Semana 12/server"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_quiz
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001 --noreload

# Terminal 2 — cliente
cd "Semana 12/client"
npm install
Copy-Item .env.example .env.local   # pegar el token que imprimió seed_quiz
npm run dev                         # http://127.0.0.1:5173
```

El servidor espera peticiones desde `http://127.0.0.1:5173` (o `localhost:5173`). El cliente espera la API en `http://127.0.0.1:8001`. El token real se guarda solo en `.env.local`, que Git ignora; en el repositorio queda `.env.example` como plantilla.

---

## 8. Conclusiones

La API del Laboratorio 8 pasó a ser consumible desde otro origen sin abrir CORS a todos los sitios. React consumió correctamente listar, crear y eliminar con Axios, y la interfaz reflejó cada cambio sin recargar. Los tres estados de la petición quedan diferenciados a simple vista y los dos errores provocados muestran mensajes útiles en lugar de una pantalla en blanco. La entrega incluye ambos proyectos, sus pruebas (64 del lado Django y 17 del lado React), el build de producción y el entregable con capturas reales.
