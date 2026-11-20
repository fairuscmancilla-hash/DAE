import { useEffect, useState } from "react";
import Button from "./Button.jsx";
import { createQuestion, describeApiError, fetchExams } from "../lib/api.js";

const EMPTY = { exam: "", text: "", first: "", second: "", correct: "first" };

export default function QuestionForm({ onNavigate }) {
  const [form, setForm] = useState(EMPTY);
  const [exams, setExams] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchExams().then(
      (items) => {
        setExams(items);
        setForm((current) => ({ ...current, exam: current.exam || String(items[0]?.id || "") }));
        setStatus("ready");
      },
      (err) => {
        setError(describeApiError(err));
        setStatus("error");
      },
    );
  }, []);

  function change(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

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

  return (
    <section className="section api-page" aria-labelledby="form-title">
      <div className="section__heading">
        <div>
          <h2 id="form-title">Nueva pregunta</h2>
          <p>Envío controlado con onSubmit y navegación de vuelta al listado.</p>
        </div>
        <Button variant="ghost" onClick={() => onNavigate("questions")}>← Volver al listado</Button>
      </div>

      {status === "error" && <div className="api-error" role="alert">{error}</div>}

      <form className="api-form" onSubmit={submit} noValidate>
        <label>
          Examen
          <select value={form.exam} onChange={(e) => change("exam", e.target.value)}>
            {exams.map((exam) => <option key={exam.id} value={exam.id}>{exam.title}</option>)}
          </select>
        </label>

        <label>
          Enunciado
          <textarea
            value={form.text}
            onChange={(e) => change("text", e.target.value)}
            placeholder="¿Qué es REST?"
            rows="3"
          />
        </label>

        <fieldset>
          <legend>Opciones (marca la correcta)</legend>
          <div className="api-choice">
            <input type="radio" name="correct" checked={form.correct === "first"} onChange={() => change("correct", "first")} />
            <input value={form.first} onChange={(e) => change("first", e.target.value)} placeholder="Opción correcta" />
          </div>
          <div className="api-choice">
            <input type="radio" name="correct" checked={form.correct === "second"} onChange={() => change("correct", "second")} />
            <input value={form.second} onChange={(e) => change("second", e.target.value)} placeholder="Otra opción" />
          </div>
        </fieldset>

        {error && <div className="api-error api-error--form" role="alert">{error}</div>}

        <div className="api-actions">
          <Button type="submit" variant="primary">Guardar pregunta</Button>
          <Button variant="ghost" onClick={() => setForm(EMPTY)}>Limpiar</Button>
        </div>
      </form>
    </section>
  );
}
