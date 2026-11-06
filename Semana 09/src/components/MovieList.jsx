import MovieCard from "./MovieCard.jsx";

// MovieList walks the billboard with map and gives every element its own key.
export default function MovieList({ movies }) {
  return (
    <ul className="movie-list">
      {movies.map((movie) => (
        <li key={movie.id}>
          <MovieCard movie={movie} />
        </li>
      ))}
    </ul>
  );
}
