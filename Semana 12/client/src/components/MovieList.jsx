import useWindowSize from "../hooks/useWindowSize.js";
import MovieCard from "./MovieCard.jsx";

// useWindowSize is shared with the premieres carousel to choose the column count.
export default function MovieList({ movies, favorites, onToggleFavorite }) {
  const { width } = useWindowSize();
  const columns = width >= 1200 ? 4 : width >= 768 ? 3 : width >= 480 ? 2 : 1;

  return (
    <ul
      className="movie-list"
      style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
    >
      {movies.map((movie) => (
        <li key={movie.id}>
          <MovieCard
            movie={movie}
            isFavorite={favorites.includes(movie.id)}
            onToggleFavorite={onToggleFavorite}
          />
        </li>
      ))}
    </ul>
  );
}
