// Adapter: translates the external billboard/premiere payload into the model
// consumed by Header, Hero, MovieList and the new premiere components.
const asText = (value, fallback = "") =>
  typeof value === "string" && value.trim() ? value.trim() : fallback;

export function adaptMovie(raw) {
  const showtimes = Array.isArray(raw?.funciones) ? raw.funciones : [];
  const rating = Number(raw?.puntuacion);

  return {
    id: Number(raw?.id_pelicula),
    title: asText(raw?.titulo, "Sin título"),
    image: asText(raw?.cartel, "/posters/1.svg"),
    synopsis: asText(raw?.descripcion, "Sin sinopsis disponible."),
    classification: asText(raw?.clasificacion, "TP"),
    rating: Number.isFinite(rating) ? rating : 0,
    showtimes: showtimes.map((item) => asText(item?.hora)).filter(Boolean),
  };
}

export function adaptMovies(rows) {
  return Array.isArray(rows) ? rows.map(adaptMovie) : [];
}

export function adaptPremiere(raw) {
  return {
    ...adaptMovie(raw),
    releaseDate: asText(raw?.fecha_estreno, "Fecha por confirmar"),
  };
}

export function adaptPremieres(rows) {
  return Array.isArray(rows) ? rows.map(adaptPremiere) : [];
}
