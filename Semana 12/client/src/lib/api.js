import axios from "axios";

// Single place for the API address. No component writes a URL by hand.
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";
const token = import.meta.env.VITE_QUIZ_TOKEN || "";

export const api = axios.create({
  baseURL: `${baseURL}/api/`,
  headers: {
    Authorization: `Token ${token}`,
    "Content-Type": "application/json",
  },
});

function flatMessages(value) {
  if (Array.isArray(value)) return value.map(flatMessages).join(" ");
  if (value && typeof value === "object") return Object.values(value).map(flatMessages).join(" ");
  return String(value);
}

export function describeApiError(error) {
  if (!error?.response) {
    if (error?.code === "ERR_NETWORK" || error?.message === "Network Error") {
      return "No se pudo conectar con la API. Revisa que Django esté encendido y que el origen esté autorizado (CORS).";
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
  if (status === 401 || status === 403) return "No tienes permiso para esta operación (token ausente, inválido o sin permisos).";
  if (status === 404) return "El recurso solicitado no existe.";
  return `Error del servidor (${status}). Inténtalo de nuevo.`;
}

export async function fetchExams() {
  const { data } = await api.get("exams/");
  return data.results;
}

export async function fetchQuestions() {
  const { data } = await api.get("questions/");
  return { items: data.results, count: data.count };
}

export async function createQuestion(payload) {
  const { data } = await api.post("questions/", payload);
  return data;
}

export async function deleteQuestion(id) {
  await api.delete(`questions/${id}/`);
}
