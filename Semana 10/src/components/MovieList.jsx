import MovieCard from "./MovieCard.jsx";

// MovieList walks the filtered billboard and gives every element its own key.
export default function MovieList({ movies, favorites, onToggleFavorite }) {
  return (
    <ul className="movie-list">
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
