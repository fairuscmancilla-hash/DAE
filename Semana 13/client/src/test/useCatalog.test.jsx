import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../services/index.js", () => ({
  productService: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
  categoryService: { list: vi.fn() },
  describeApiError: (error) => error.message,
  apiClient: {},
  toProductForm: (v) => v,
}));

import useCatalog from "../hooks/useCatalog.js";
import { categoryService, productService } from "../services/index.js";

const products = [
  { id: 1, name: "Coffee", category: { id: 10, name: "Drinks" } },
  { id: 2, name: "Mouse", category: { id: 11, name: "Technology" } },
];
const categories = [
  { id: 10, name: "Drinks", product_count: 1 },
  { id: 11, name: "Technology", product_count: 1 },
];

beforeEach(() => {
  vi.clearAllMocks();
  productService.list.mockResolvedValue({ results: products, count: 2 });
  categoryService.list.mockResolvedValue({ results: categories, count: 2 });
});

describe("useCatalog", () => {
  it("loads products and categories from the services in one effect", async () => {
    const { result } = renderHook(() => useCatalog());
    expect(result.current.status).toBe("loading");
    await waitFor(() => expect(result.current.status).toBe("ready"));
    expect(result.current.products).toEqual(products);
    expect(result.current.categories).toEqual(categories);
    expect(productService.list).toHaveBeenCalledTimes(1);
    expect(categoryService.list).toHaveBeenCalledTimes(1);
  });

  it("filters in memory from the API-loaded categories", async () => {
    const { result } = renderHook(() => useCatalog());
    await waitFor(() => expect(result.current.status).toBe("ready"));
    act(() => result.current.selectCategory(11));
    expect(result.current.visibleProducts).toEqual([products[1]]);
    expect(productService.list).toHaveBeenCalledTimes(1);
  });

  it("moves to error state and can retry", async () => {
    productService.list.mockRejectedValueOnce(new Error("sin conexión"));
    const { result } = renderHook(() => useCatalog());
    await waitFor(() => expect(result.current.status).toBe("error"));
    expect(result.current.error.message).toBe("sin conexión");

    act(() => result.current.reload());
    await waitFor(() => expect(result.current.status).toBe("ready"));
  });

  it("reloads the list after deleting a product", async () => {
    productService.remove.mockResolvedValue(undefined);
    productService.list
      .mockResolvedValueOnce({ results: products, count: 2 })
      .mockResolvedValueOnce({ results: [products[1]], count: 1 });
    const { result } = renderHook(() => useCatalog());
    await waitFor(() => expect(result.current.products).toHaveLength(2));

    await act(async () => { await result.current.removeProduct(1); });
    await waitFor(() => expect(result.current.products).toEqual([products[1]]));
    expect(productService.remove).toHaveBeenCalledWith(1);
    expect(productService.list).toHaveBeenCalledTimes(2);
  });
});
