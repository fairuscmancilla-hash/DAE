import Button from "./Button.jsx";
import ErrorBanner from "./ErrorBanner.jsx";
import LoadingSkeleton from "./LoadingSkeleton.jsx";
import QuestionTable from "./QuestionTable.jsx";
import useQuestions from "../hooks/useQuestions.js";
import { describeApiError } from "../lib/api.js";

export default function QuestionsPage({ onNavigate }) {
  const { status, items, count, error, reload, remove } = useQuestions();

  async function handleDelete(id) {
    if (!window.confirm(`¿Eliminar la pregunta #${id}?`)) return;
    try {
      await remove(id);
    } catch (err) {
      window.alert(describeApiError(err));
    }
  }

  return (
    <section className="section api-page" aria-labelledby="api-title">
      <div className="section__heading">
        <div>
          <h2 id="api-title">Preguntas desde la API</h2>
          <p>Cliente Axios · Django REST Framework · tres estados de petición</p>
        </div>
        <div className="api-actions">
          <Button variant="secondary" onClick={reload}>Actualizar</Button>
          <Button variant="primary" onClick={() => onNavigate("new")}>+ Nueva pregunta</Button>
        </div>
      </div>

      {status === "loading" && <LoadingSkeleton />}
      {status === "error" && <ErrorBanner message={describeApiError(error)} onRetry={reload} />}
      {status === "ready" && (
        <>
          <p className="api-count" role="status">{count} pregunta(s) recibidas sin recargar la página.</p>
          <QuestionTable items={items} onDelete={handleDelete} />
        </>
      )}
    </section>
  );
}
