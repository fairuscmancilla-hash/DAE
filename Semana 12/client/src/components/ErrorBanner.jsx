import Button from "./Button.jsx";

export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="api-error" role="alert">
      <div>
        <strong>No se pudo cargar la lista</strong>
        <p>{message}</p>
      </div>
      {onRetry && <Button variant="secondary" onClick={onRetry}>Reintentar</Button>}
    </div>
  );
}
