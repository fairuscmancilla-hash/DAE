import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ProductCard from "../components/ProductCard/index.js";
import CategoryFilter from "../components/CategoryFilter/index.js";

const product = {
  id: 1,
  name: "Ground coffee 500 g",
  description: "Dark roast.",
  price: "18.90",
  stock: 25,
  image_url: "http://127.0.0.1:8002/media/products/coffee.png",
  category: { id: 10, name: "Drinks", description: "Bebidas" },
};

describe("catalog components", () => {
  it("renders the nested category, price and image in one card", () => {
    render(<ProductCard product={product} onEdit={() => {}} onDelete={() => {}} />);
    expect(screen.getByText("Drinks")).toBeInTheDocument();
    expect(screen.getByText("Ground coffee 500 g")).toBeInTheDocument();
    expect(screen.getByText(/18\.90/)).toBeInTheDocument();
    expect(screen.getByAltText(product.name)).toHaveAttribute("src", product.image_url);
  });

  it("calls edit and delete with the whole product", () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    render(<ProductCard product={product} onEdit={onEdit} onDelete={onDelete} />);
    fireEvent.click(screen.getByText("Editar"));
    fireEvent.click(screen.getByText("Eliminar"));
    expect(onEdit).toHaveBeenCalledWith(product);
    expect(onDelete).toHaveBeenCalledWith(product);
  });

  it("renders the categories supplied by the API as filter buttons", () => {
    const onSelect = vi.fn();
    const categories = [
      { id: 10, name: "Drinks", product_count: 3 },
      { id: 11, name: "Technology", product_count: 4 },
    ];
    render(<CategoryFilter categories={categories} selected="all" onSelect={onSelect} />);
    expect(screen.getByRole("button", { name: "Todas" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Technology/ }));
    expect(onSelect).toHaveBeenCalledWith(11);
  });
});
