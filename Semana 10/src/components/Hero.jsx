import Button from "./Button.jsx";

// Hero receives the featured movie and the favorite state controlled by App.
export default function Hero({ movie, isFavorite = false, onToggleFavorite }) {
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
        </div>
      </div>
    </section>
  );
}
