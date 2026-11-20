import { useCallback, useEffect, useRef, useState } from "react";
import { deleteQuestion, fetchQuestions } from "../lib/api.js";

const LOADING = { status: "loading", items: [], count: 0, error: null };

// Keeps the three visible states of the list request: loading, data and error.
export default function useQuestions() {
  const [state, setState] = useState(LOADING);
  const requestRef = useRef(0);

  const load = useCallback(() => {
    const requestId = ++requestRef.current;
    setState(LOADING);

    fetchQuestions().then(
      ({ items, count }) => {
        if (requestId === requestRef.current) {
          setState({ status: "ready", items, count, error: null });
        }
      },
      (error) => {
        if (requestId === requestRef.current) {
          setState({ status: "error", items: [], count: 0, error });
        }
      },
    );
  }, []);

  useEffect(() => {
    load();
    return () => {
      requestRef.current += 1;
    };
  }, [load]);

  const remove = useCallback(
    async (id) => {
      await deleteQuestion(id);
      load();
    },
    [load],
  );

  return { ...state, reload: load, remove };
}
