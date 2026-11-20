import {
  createResource,
  deleteResource,
  getResource,
  listResource,
  updateResource,
} from "./apiClient.js";

const PATH = "catalog/products/";

export function toProductForm(values) {
  if (typeof FormData !== "undefined" && values instanceof FormData) return values;
  const body = new FormData();
  body.append("name", values.name || "");
  body.append("description", values.description || "");
  body.append("price", values.price || "0");
  body.append("stock", String(values.stock ?? 0));
  body.append("category_id", String(values.category_id || values.category?.id || ""));
  if (values.image instanceof File) body.append("image", values.image);
  return body;
}

export const productService = {
  list(params) {
    return listResource(PATH, params);
  },
  get(id) {
    return getResource(PATH, id);
  },
  create(values) {
    return createResource(PATH, toProductForm(values));
  },
  update(id, values) {
    // DRF does not parse multipart bodies on PUT. Send JSON unless a new file was picked.
    if (values.image instanceof File) {
      return updateResource(PATH, id, toProductForm(values));
    }
    return updateResource(PATH, id, {
      name: values.name,
      description: values.description,
      price: values.price,
      stock: Number(values.stock),
      category_id: Number(values.category_id || values.category?.id),
    });
  },
  remove(id) {
    return deleteResource(PATH, id);
  },
};
