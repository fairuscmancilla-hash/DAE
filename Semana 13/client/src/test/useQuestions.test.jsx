import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../lib/api.js", () => ({
  fetchQuestions: vi.fn(),
  deleteQuestion: vi.fn(),
  describeApiError: (e) => e.message,
}));

import useQuestions from "../hooks/useQuestions.js";
import { deleteQuestion, fetchQuestions } from "../lib/api.js";

beforeEach(() => vi.clearAllMocks());

describe("useQuestions", () => {
  it("moves from loading to ready with data", async () => {
    fetchQuestions.mockResolvedValue({ items: [{ id: 1 }], count: 1 });
    const { result } = renderHook(() => useQuestions());
    expect(result.current.status).toBe("loading");
    await waitFor(() => expect(result.current.status).toBe("ready"));
    expect(result.current.items).toEqual([{ id: 1 }]);
    expect(result.current.count).toBe(1);
  });

  it("shows the error state when the request fails", async () => {
    fetchQuestions.mockRejectedValue(new Error("sin conexión"));
    const { result } = renderHook(() => useQuestions());
    await waitFor(() => expect(result.current.status).toBe("error"));
    expect(result.current.error.message).toBe("sin conexión");
    expect(result.current.items).toEqual([]);
  });

  it("reloads after deleting and refreshes the list", async () => {
    fetchQuestions
      .mockResolvedValueOnce({ items: [{ id: 1 }, { id: 2 }], count: 2 })
      .mockResolvedValueOnce({ items: [{ id: 2 }], count: 1 });
    deleteQuestion.mockResolvedValue(undefined);
    const { result } = renderHook(() => useQuestions());
    await waitFor(() => expect(result.current.items).toHaveLength(2));
    await act(async () => { await result.current.remove(1); });
    await waitFor(() => expect(result.current.items).toEqual([{ id: 2 }]));
    expect(deleteQuestion).toHaveBeenCalledWith(1);
  });

  it("ignores a stale response after reload", async () => {
    let resolveOld;
    fetchQuestions
      .mockReturnValueOnce(new Promise((r) => { resolveOld = r; }))
      .mockResolvedValueOnce({ items: [{ id: 99 }], count: 1 });
    const { result } = renderHook(() => useQuestions());
    act(() => result.current.reload());
    resolveOld({ items: [{ id: 1 }], count: 1 });
    await waitFor(() => expect(result.current.items).toEqual([{ id: 99 }]));
  });
});
