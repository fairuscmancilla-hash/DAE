import { Eraser } from "lucide-react";
import Button from "./Button.jsx";

// Hero can clear the filters owned by App, so the banner and the list stay in sync.
export default function Hero({
  movie,
  isFavorite = false,
  onToggleFavorite,
  onClearFilters,
  hasFilters = false,
}) {
  return (
    <section className="hero" aria-label="Destacada">
      <img className="hero__image" src={movie.image} alt={movie.title} />
      <div className="hero__content">
        <p className="hero__eyebrow">
          Película destacada <span className="badge">{movie.classification}</span>
        </p>
        <h2>{movie.title}</h2>
        <p className="hero__synopsis">{movie.synopsis}</p>
        <p className="rating">★ {movie.rating}</p>
        <div className="hero__actions">
          <a className="button" href={`#horarios-${movie.id}`}>
            Ver horarios
          </a>
          <Button
            variant={isFavorite ? "danger" : "ghost"}
            onClick={() => onToggleFavorite(movie.id)}
            aria-pressed={isFavorite}
          >
            {isFavorite ? "♥ En favoritas" : "♡ Guardar en favoritas"}
          </Button>
          <Button
            variant="ghost"
            onClick={onClearFilters}
            disabled={!hasFilters}
            aria-label="Limpiar filtros de búsqueda"
          >
            <Eraser size={16} aria-hidden="true" />
            Limpiar filtros
          </Button>
        </div>
      </div>
    </section>
  );
}
