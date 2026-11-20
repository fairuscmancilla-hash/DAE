import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../services/apiClient.js", () => ({
  listResource: vi.fn(),
  getResource: vi.fn(),
  createResource: vi.fn(),
  updateResource: vi.fn(),
  deleteResource: vi.fn(),
  describeApiError: (error) => error.message,
  apiClient: {},
}));

import {
  getResource,
  listResource,
  createResource,
  updateResource,
  deleteResource,
} from "../services/apiClient.js";
import { categoryService } from "../services/categoryService.js";
import { productService, toProductForm } from "../services/productService.js";

beforeEach(() => vi.clearAllMocks());

describe("catalog services", () => {
  it("productService exposes the five operations on the product path", async () => {
    listResource.mockResolvedValue({ results: [] });
    getResource.mockResolvedValue({ id: 1 });
    createResource.mockResolvedValue({ id: 2 });
    updateResource.mockResolvedValue({ id: 1 });
    deleteResource.mockResolvedValue(undefined);

    expect(await productService.list({ page_size: 20 })).toEqual({ results: [] });
    expect(listResource).toHaveBeenCalledWith("catalog/products/", { page_size: 20 });

    await productService.get(1);
    expect(getResource).toHaveBeenCalledWith("catalog/products/", 1);

    await productService.create({ name: "Mouse", category_id: 3 });
    expect(createResource).toHaveBeenCalledWith("catalog/products/", expect.any(FormData));

    await productService.update(1, { name: "Mouse Pro", price: "10.00", stock: 2, category_id: 3 });
    expect(updateResource).toHaveBeenCalledWith("catalog/products/", 1, {
      name: "Mouse Pro",
      description: undefined,
      price: "10.00",
      stock: 2,
      category_id: 3,
    });

    await productService.remove(1);
    expect(deleteResource).toHaveBeenCalledWith("catalog/products/", 1);
  });

  it("categoryService exposes the five operations on the category path", async () => {
    listResource.mockResolvedValue({ results: [] });
    await categoryService.list();
    expect(listResource).toHaveBeenCalledWith("catalog/categories/", undefined);

    await categoryService.get(2);
    expect(getResource).toHaveBeenCalledWith("catalog/categories/", 2);

    await categoryService.create({ name: "Home" });
    expect(createResource).toHaveBeenCalledWith("catalog/categories/", { name: "Home" });

    await categoryService.update(2, { name: "Office" });
    expect(updateResource).toHaveBeenCalledWith("catalog/categories/", 2, { name: "Office" });

    await categoryService.remove(2);
    expect(deleteResource).toHaveBeenCalledWith("catalog/categories/", 2);
  });

  it("builds multipart bodies without an image on edit", () => {
    const body = toProductForm({
      name: "Keyboard",
      description: "Compact",
      price: "129.00",
      stock: 7,
      category_id: 3,
    });
    expect(body.get("name")).toBe("Keyboard");
    expect(body.get("category_id")).toBe("3");
    expect(body.has("image")).toBe(false);
  });
});
