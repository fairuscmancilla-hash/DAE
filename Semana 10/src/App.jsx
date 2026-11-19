import { useEffect, useMemo, useState } from "react";
import { Button, Footer, Header, Hero, MovieList, SearchBar } from "./components/index.js";
import { contact, links, movies } from "./data/movies.js";
import { readFavorites, writeFavorites } from "./lib/storage.js";

export default function App() {
  const [favorites, setFavorites] = useState(readFavorites);
  const [query, setQuery] = useState("");
  const [onlyFavorites, setOnlyFavorites] = useState(false);

  useEffect(() => {
    writeFavorites(favorites);
  }, [favorites]);

  const visibleMovies = useMemo(() => {
    const needle = query.trim().toLowerCase();

    return movies.filter((movie) => {
      const matchesText =
        needle === "" ||
        [movie.title, movie.synopsis, movie.classification].some((value) =>
          value.toLowerCase().includes(needle),
        );
      const matchesFavorites = !onlyFavorites || favorites.includes(movie.id);

      return matchesText && matchesFavorites;
    });
  }, [favorites, onlyFavorites, query]);

  function toggleFavorite(id) {
    setFavorites((current) =>
      current.includes(id)
        ? current.filter((favoriteId) => favoriteId !== id)
        : [...current, id],
    );
  }

  function clearFilters() {
    setQuery("");
    setOnlyFavorites(false);
  }

  const featured = movies[0];

  return (
    <>
      <Header name="Cine Tecsup" links={links} />
      <main>
        <Hero
          movie={featured}
          isFavorite={favorites.includes(featured.id)}
          onToggleFavorite={toggleFavorite}
        />

        <section id="cartelera" className="section" aria-labelledby="cartelera-titulo">
          <div className="section__heading">
            <h2 id="cartelera-titulo">Cartelera</h2>
            <p>{movies.length} películas en cartelera</p>
          </div>

          <div className="toolbar">
            <SearchBar
              value={query}
              onChange={setQuery}
              onClear={() => setQuery("")}
              resultCount={visibleMovies.length}
              totalCount={movies.length}
            />
            <Button
              variant={onlyFavorites ? "primary" : "ghost"}
              onClick={() => setOnlyFavorites((current) => !current)}
              aria-pressed={onlyFavorites}
            >
              {onlyFavorites ? "★" : "☆"} Solo favoritas ({favorites.length})
            </Button>
          </div>

          {visibleMovies.length > 0 ? (
            <MovieList
              movies={visibleMovies}
              favorites={favorites}
              onToggleFavorite={toggleFavorite}
            />
          ) : (
            <div className="empty-state">
              <p>
                {onlyFavorites
                  ? "Todavía no tienes películas favoritas."
                  : "No hay películas que coincidan con la búsqueda."}
              </p>
              <Button variant="secondary" onClick={clearFilters}>
                Limpiar filtros
              </Button>
            </div>
          )}
        </section>

        <section
          id="proximamente"
          className="coming-soon"
          aria-labelledby="proximamente-titulo"
        >
          <h2 id="proximamente-titulo">Próximamente</h2>
          <p>
            Muy pronto anunciaremos los estrenos de la próxima semana. Mientras
            tanto, consulta los horarios de hoy en la cartelera.
          </p>
        </section>
      </main>
      <Footer contact={contact} />
    </>
  );
}
