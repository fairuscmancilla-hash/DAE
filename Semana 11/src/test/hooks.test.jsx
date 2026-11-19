import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import useDebounce from "../hooks/useDebounce.js";
import usePremieres from "../hooks/usePremieres.js";
import useWindowSize from "../hooks/useWindowSize.js";

afterEach(() => {
  vi.useRealTimers();
});

describe("useDebounce", () => {
  it("keeps the previous value until the delay has passed", () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: "robot" } },
    );

    rerender({ value: "volcán" });
    expect(result.current).toBe("robot");

    act(() => vi.advanceTimersByTime(299));
    expect(result.current).toBe("robot");

    act(() => vi.advanceTimersByTime(1));
    expect(result.current).toBe("volcán");
  });
});

describe("useWindowSize", () => {
  it("updates the width when the window is resized", () => {
    const originalWidth = window.innerWidth;
    window.innerWidth = 1200;

    const { result } = renderHook(() => useWindowSize());
    expect(result.current.width).toBe(1200);

    act(() => {
      window.innerWidth = 500;
      window.dispatchEvent(new Event("resize"));
    });
    expect(result.current.width).toBe(500);

    window.innerWidth = originalWidth;
  });
});

describe("usePremieres", () => {
  it("moves from loading to success, error and recovery", () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => usePremieres({ delay: 1000 }));

    expect(result.current.status).toBe("loading");
    act(() => vi.advanceTimersByTime(1000));
    expect(result.current.status).toBe("success");
    expect(result.current.premieres).toHaveLength(4);

    act(() => result.current.retry(true));
    expect(result.current.status).toBe("loading");
    act(() => vi.advanceTimersByTime(1000));
    expect(result.current.status).toBe("error");
    expect(result.current.error.message).toMatch(/no respondió/);

    act(() => result.current.retry(false));
    act(() => vi.advanceTimersByTime(1000));
    expect(result.current.status).toBe("success");
    expect(result.current.error).toBeNull();
  });
});
