export default function LoadingSkeleton() {
  return (
    <div className="api-skeleton" role="status" aria-busy="true" aria-label="Cargando preguntas">
      <p className="api-skeleton__message">Cargando preguntas desde la API…</p>
      {[1, 2, 3, 4].map((row) => (
        <div className="api-skeleton__row" key={row}>
          <span />
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}
