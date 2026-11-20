import { useEffect, useMemo, useState } from "react";
import { Heart, HeartCrack } from "lucide-react";
import { Toaster, toast } from "sonner";
import {
  Button,
  Footer,
  Header,
  Hero,
  MovieList,
  PremieresSection,
  QuestionForm,
  QuestionsPage,
  SearchBar,
} from "./components/index.js";
import { contact, links } from "./data/movies.js";
import { billboardPayload } from "./data/billboard.js";
import { adaptMovies } from "./lib/movieAdapter.js";
import { readFavorites, writeFavorites } from "./lib/storage.js";
import useDebounce from "./hooks/useDebounce.js";

export default function App() {
  const movies = useMemo(() => adaptMovies(billboardPayload.peliculas), []);
  const [favorites, setFavorites] = useState(readFavorites);
  const [query, setQuery] = useState("");
  const hashView = window.location.hash.slice(1);
  const [view, setView] = useState(["questions", "new"].includes(hashView) ? hashView : "home");
  const [onlyFavorites, setOnlyFavorites] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const hasFilters = query.trim() !== "" || onlyFavorites;
  const favoriteCount = favorites.length;

  useEffect(() => {
    writeFavorites(favorites);
  }, [favorites]);

  useEffect(() => {
    window.location.hash = view;
  }, [view]);

  const visibleMovies = useMemo(() => {
    const needle = debouncedQuery.trim().toLowerCase();

    return movies.filter((movie) => {
      const matchesText =
        needle === "" ||
        [movie.title, movie.synopsis, movie.classification].some((value) =>
          value.toLowerCase().includes(needle),
        );
      const matchesFavorites = !onlyFavorites || favorites.includes(movie.id);

      return matchesText && matchesFavorites;
    });
  }, [debouncedQuery, favorites, movies, onlyFavorites]);

  function toggleFavorite(id) {
    const movie = movies.find((item) => item.id === id);
    const wasFavorite = favorites.includes(id);

    setFavorites((current) =>
      wasFavorite
        ? current.filter((favoriteId) => favoriteId !== id)
        : [...current, id],
    );

    // The card only reports the click; App decides how the notice is shown.
    toast.success(wasFavorite ? "Quitada de favoritas" : "Agregada a favoritas", {
      description: movie?.title,
      icon: wasFavorite ? <HeartCrack size={18} /> : <Heart size={18} />,
    });
  }

  function clearFilters() {
    setQuery("");
    setOnlyFavorites(false);
  }

  const featured = movies[0];

  return (
    <>
      <Header name="Cine Tecsup" links={links} favoriteCount={favoriteCount} />
      <nav className="api-nav" aria-label="Navegación del laboratorio 12">
        <button className={view === "home" ? "is-active" : ""} onClick={() => setView("home")}>Cartelera (Lab 11)</button>
        <button className={view === "questions" ? "is-active" : ""} onClick={() => setView("questions")}>Preguntas API</button>
        <button className={view === "new" ? "is-active" : ""} onClick={() => setView("new")}>Nueva pregunta</button>
      </nav>
      <main>
        {view === "questions" && <QuestionsPage onNavigate={setView} />}
        {view === "new" && <QuestionForm onNavigate={setView} />}
        {view === "home" && (
          <>
        <Hero
          movie={featured}
          isFavorite={favorites.includes(featured.id)}
          onToggleFavorite={toggleFavorite}
          onClearFilters={clearFilters}
          hasFilters={hasFilters}
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
              {onlyFavorites ? "★" : "☆"} Solo favoritas ({favoriteCount})
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

        <PremieresSection />
          </>
        )}
      </main>
      <Footer contact={contact} />
      <Toaster position="top-right" richColors closeButton />
    </>
  );
}
