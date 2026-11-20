export default function QuestionTable({ items, onDelete }) {
  return (
    <div className="api-table-wrap">
      <table className="api-table">
        <thead>
          <tr><th>ID</th><th>Examen</th><th>Enunciado</th><th>Opciones</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          {items.map((question) => (
            <tr key={question.id}>
              <td><code>#{question.id}</code></td>
              <td>{question.exam}</td>
              <td>{question.text}</td>
              <td>
                <ul>
                  {question.choices.map((choice) => (
                    <li key={choice.id} className={choice.is_correct ? "is-correct" : ""}>
                      {choice.text}{choice.is_correct ? " ✓" : ""}
                    </li>
                  ))}
                </ul>
              </td>
              <td>
                <button className="btn btn-danger btn-sm" onClick={() => onDelete(question.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
