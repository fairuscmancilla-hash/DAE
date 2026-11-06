// Hero receives the featured movie by props and renders the banner.
export default function Hero({ movie }) {
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
        <a className="button" href={`#horarios-${movie.id}`}>
          Ver horarios
        </a>
      </div>
    </section>
  );
}
