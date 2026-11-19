import Button from "./Button.jsx";

// Controlled search input: the text lives in App, not inside this component.
export default function SearchBar({ value, onChange, onClear, resultCount, totalCount }) {
  return (
    <div className="search-bar">
      <label className="search-bar__field">
        <span className="search-bar__label">Buscar película</span>
        <input
          type="search"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Título, sinopsis o clasificación"
        />
      </label>
      <Button variant="ghost" onClick={onClear} disabled={value.trim() === ""}>
        Limpiar búsqueda
      </Button>
      <p className="search-bar__count" aria-live="polite">
        {resultCount} de {totalCount} películas
      </p>
    </div>
  );
}
