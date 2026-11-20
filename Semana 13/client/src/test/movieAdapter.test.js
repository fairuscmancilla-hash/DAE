import { describe, expect, it } from "vitest";
import { adaptMovie, adaptMovies, adaptPremieres } from "../lib/movieAdapter.js";

describe("movieAdapter", () => {
  it("maps the external billboard fields to the app model", () => {
    const result = adaptMovie({
      id_pelicula: 7,
      titulo: "  Mi Vecino el Robot  ",
      cartel: "/posters/7.svg",
      descripcion: "Una historia de robot y niña.",
      clasificacion: "TP",
      puntuacion: 4.9,
      funciones: [{ hora: "13:00", sala: "1" }, { hora: "15:15", sala: "2" }],
    });

    expect(result).toEqual({
      id: 7,
      title: "Mi Vecino el Robot",
      image: "/posters/7.svg",
      synopsis: "Una historia de robot y niña.",
      classification: "TP",
      rating: 4.9,
      showtimes: ["13:00", "15:15"],
    });
  });

  it("uses safe defaults when the payload is incomplete", () => {
    expect(adaptMovie({ id_pelicula: 9, puntuacion: "x", funciones: null })).toMatchObject({
      id: 9,
      title: "Sin título",
      rating: 0,
      showtimes: [],
    });
    expect(adaptMovies(null)).toEqual([]);
  });

  it("adds the release date for premieres", () => {
    const [premiere] = adaptPremieres([
      { id_pelicula: 201, titulo: "El Eco del Volcán", fecha_estreno: "27 nov 2026" },
    ]);

    expect(premiere.releaseDate).toBe("27 nov 2026");
  });
});
