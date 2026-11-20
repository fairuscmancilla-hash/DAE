import {
  createResource,
  deleteResource,
  getResource,
  listResource,
  updateResource,
} from "./apiClient.js";

const PATH = "catalog/categories/";

export const categoryService = {
  list(params) {
    return listResource(PATH, params);
  },
  get(id) {
    return getResource(PATH, id);
  },
  create(values) {
    return createResource(PATH, values);
  },
  update(id, values) {
    return updateResource(PATH, id, values);
  },
  remove(id) {
    return deleteResource(PATH, id);
  },
};
