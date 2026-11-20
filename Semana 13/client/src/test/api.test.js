import { afterEach, describe, expect, it, vi } from "vitest";
import { api, createQuestion, deleteQuestion, describeApiError, fetchQuestions } from "../lib/api.js";

afterEach(() => vi.restoreAllMocks());

describe("API client", () => {
  it("keeps a single base address with the token header", () => {
    expect(api.defaults.baseURL).toMatch(/\/api\/$/);
    expect(api.defaults.headers.Authorization).toMatch(/^Token /);
  });

  it("lists questions and keeps count", async () => {
    vi.spyOn(api, "get").mockResolvedValue({ data: { count: 8, results: [{ id: 1 }] } });
    await expect(fetchQuestions()).resolves.toEqual({ items: [{ id: 1 }], count: 8 });
    expect(api.get).toHaveBeenCalledWith("questions/");
  });

  it("creates and deletes without writing URLs in components", async () => {
    const payload = { exam: 1, text: "Q", choices: [] };
    vi.spyOn(api, "post").mockResolvedValue({ data: { id: 9 } });
    await expect(createQuestion(payload)).resolves.toEqual({ id: 9 });
    expect(api.post).toHaveBeenCalledWith("questions/", payload);

    vi.spyOn(api, "delete").mockResolvedValue({ status: 204 });
    await deleteQuestion(9);
    expect(api.delete).toHaveBeenCalledWith("questions/9/");
  });

  it("describes validation, permission and network errors", () => {
    expect(describeApiError({ code: "ERR_NETWORK" })).toMatch(/No se pudo conectar/);
    expect(describeApiError({ response: { status: 400, data: { text: ["This field is required."] } } })).toMatch(/text: This field is required/);
    expect(describeApiError({ response: { status: 403 } })).toMatch(/permiso/);
    expect(describeApiError({ response: { status: 500 } })).toMatch(/500/);
  });
});
