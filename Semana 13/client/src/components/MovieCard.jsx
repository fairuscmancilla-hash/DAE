import { Heart } from "lucide-react";
import Button from "./Button.jsx";

// MovieCard receives one movie and the favorite state controlled by App.
export default function MovieCard({ movie, isFavorite = false, onToggleFavorite }) {
  return (
    <article className="movie-card" id={`horarios-${movie.id}`}>
      <img className="movie-card__image" src={movie.image} alt={movie.title} />
      <div className="movie-card__body">
        <div className="movie-card__heading">
          <h3>{movie.title}</h3>
          <span className="badge">{movie.classification}</span>
        </div>
        <p className="rating">★ {movie.rating}</p>

        <Button
          variant={isFavorite ? "danger" : "secondary"}
          className="favorite-button"
          onClick={() => onToggleFavorite(movie.id)}
          aria-pressed={isFavorite}
          aria-label={`${isFavorite ? "Quitar" : "Agregar"} ${movie.title} ${
            isFavorite ? "de" : "a"
          } favoritas`}
        >
          <Heart size={16} aria-hidden="true" fill={isFavorite ? "currentColor" : "none"} />
          {isFavorite ? "En favoritas" : "Favorita"}
        </Button>

        {movie.showtimes.length > 0 ? (
          <div className="movie-card__showtimes">
            <p className="movie-card__label">Horarios</p>
            <ul className="showtimes">
              {movie.showtimes.map((time) => (
                <li key={time}>{time}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="no-showtimes">Sin funciones hoy</p>
        )}
      </div>
    </article>
  );
}
