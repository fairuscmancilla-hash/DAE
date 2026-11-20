import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App.jsx";

const { toastSuccess } = vi.hoisted(() => ({ toastSuccess: vi.fn() }));

vi.mock("sonner", () => ({
  Toaster: () => null,
  toast: { success: toastSuccess },
}));

beforeEach(() => {
  window.localStorage.clear();
  toastSuccess.mockClear();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("App: favorites and filters", () => {
  it("notifies from App and shows the elevated counter in Header", () => {
    render(<App />);

    expect(screen.getByLabelText("0 favoritas")).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: /Agregar La .* a favoritas/i }),
    );

    expect(toastSuccess).toHaveBeenCalledWith(
      "Agregada a favoritas",
      expect.objectContaining({ description: expect.any(String) }),
    );
    expect(screen.getByLabelText("1 favoritas")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: /Quitar La .* de favoritas/i }),
    );
    expect(toastSuccess).toHaveBeenLastCalledWith(
      "Quitada de favoritas",
      expect.anything(),
    );
    expect(screen.getByLabelText("0 favoritas")).toBeInTheDocument();
  });

  it("clears the search from the hero banner", () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Título, sinopsis o clasificación/i);

    fireEvent.change(input, { target: { value: "robot" } });
    expect(input).toHaveValue("robot");

    fireEvent.click(
      screen.getByRole("button", { name: "Limpiar filtros de búsqueda" }),
    );
    expect(input).toHaveValue("");
  });

  it("shows the loading, data and error states of the premieres section", () => {
    vi.useFakeTimers();
    render(<App />);

    expect(screen.getByText("Cargando estrenos…")).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(1100));
    expect(screen.getByText("El Eco del Volcán")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Simular error" }));
    act(() => vi.advanceTimersByTime(1100));
    expect(screen.getByRole("alert")).toHaveTextContent(
      "El servicio de estrenos no respondió",
    );
  });
});
