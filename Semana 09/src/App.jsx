import { Footer, Header, Hero, MovieList } from "./components/index.js";
import { contact, links, movies } from "./data/movies.js";

export default function App() {
  const featured = movies[0];

  return (
    <>
      <Header name="Cine Tecsup" links={links} />
      <main>
        <Hero movie={featured} />

        <section id="cartelera" className="section" aria-labelledby="cartelera-titulo">
          <div className="section__heading">
            <h2 id="cartelera-titulo">Cartelera</h2>
            <p>{movies.length} películas en cartelera</p>
          </div>
          <MovieList movies={movies} />
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
