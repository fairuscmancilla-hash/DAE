import { movies } from "./movies.js";

// Simulates the payload of an external service: Spanish field names and
// showtimes as objects, instead of the shape the React components expect.
export const billboardPayload = {
  origen: "cartelera-local",
  peliculas: movies.map((movie) => ({
    id_pelicula: movie.id,
    titulo: movie.title,
    cartel: movie.image,
    descripcion: movie.synopsis,
    clasificacion: movie.classification,
    puntuacion: movie.rating,
    funciones: movie.showtimes.map((hora, index) => ({
      hora,
      sala: String(index + 1),
    })),
  })),
};
