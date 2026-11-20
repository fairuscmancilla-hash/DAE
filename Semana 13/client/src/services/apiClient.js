import axios from "axios";

// The API address lives here and nowhere else in the catalog codebase.
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8002";
const token = import.meta.env.VITE_QUIZ_TOKEN || "";

export const apiClient = axios.create({
  baseURL: `${baseURL}/api/`,
  headers: token ? { Authorization: `Token ${token}` } : {},
});

function flatMessages(value) {
  if (Array.isArray(value)) return value.map(flatMessages).join(" ");
  if (value && typeof value === "object") return Object.values(value).map(flatMessages).join(" ");
  return String(value);
}

export function describeApiError(error) {
  if (!error?.response) {
    if (error?.code === "ERR_NETWORK" || error?.message === "Network Error") {
      return "No se pudo conectar con la API. Revisa que Django esté encendido y que el origen esté autorizado.";
    }
    return error?.message || "Error inesperado de red.";
  }
  const { status, data } = error.response;
  if (status === 400) {
    const details = Object.entries(data || {})
      .map(([field, messages]) => `${field}: ${flatMessages(messages)}`)
      .join(" · ");
    return `La API rechazó los datos. ${details || "Revisa el formulario."}`;
  }
  if (status === 401 || status === 403) return "No tienes permiso para esta operación. Revisa el token.";
  if (status === 404) return "El recurso solicitado no existe.";
  return `Error del servidor (${status}). Inténtalo de nuevo.`;
}

function bodyConfig(payload) {
  if (typeof FormData !== "undefined" && payload instanceof FormData) return {};
  return { headers: { "Content-Type": "application/json" } };
}

export async function listResource(path, params) {
  const { data } = await apiClient.get(path, { params });
  return data;
}

export async function getResource(path, id) {
  const { data } = await apiClient.get(`${path}${id}/`);
  return data;
}

export async function createResource(path, payload) {
  const { data } = await apiClient.post(`${path}`, payload, bodyConfig(payload));
  return data;
}

export async function updateResource(path, id, payload) {
  const { data } = await apiClient.put(`${path}${id}/`, payload, bodyConfig(payload));
  return data;
}

export async function deleteResource(path, id) {
  await apiClient.delete(`${path}${id}/`);
}
