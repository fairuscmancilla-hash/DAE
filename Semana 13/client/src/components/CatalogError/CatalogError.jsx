import Button from "../../components/Button.jsx";

export default function CatalogError({ message, onRetry }) {
  return (
    <div className="api-error" role="alert">
      <div>
        <strong>No se pudo cargar el catálogo</strong>
        <p>{message}</p>
      </div>
      <Button variant="secondary" onClick={onRetry}>
        Reintentar
      </Button>
    </div>
  );
}
