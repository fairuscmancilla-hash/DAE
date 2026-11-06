// MovieCard receives one movie by props and shows all of its information.
export default function MovieCard({ movie }) {
  return (
    <article className="movie-card" id={`horarios-${movie.id}`}>
      <img className="movie-card__image" src={movie.image} alt={movie.title} />
      <div className="movie-card__body">
        <div className="movie-card__heading">
          <h3>{movie.title}</h3>
          <span className="badge">{movie.classification}</span>
        </div>
        <p className="rating">★ {movie.rating}</p>

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
