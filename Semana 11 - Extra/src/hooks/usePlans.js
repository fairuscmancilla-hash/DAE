import { useCallback, useEffect, useRef, useState } from "react";

const LOADING = { status: "loading", plans: [], error: null };

// Carga los planes del agente y expone los tres estados de la petición.
export default function usePlans(fetchPlans) {
  const [state, setState] = useState(LOADING);
  const requestRef = useRef(0);

  const reload = useCallback(() => {
    const requestId = ++requestRef.current;
    setState(LOADING);
    let promise;
    try {
      promise = fetchPlans();
    } catch (error) {
      if (requestId === requestRef.current) setState({ status: "error", plans: [], error });
      return;
    }
    Promise.resolve(promise).then(
      (plans) => {
        if (requestId === requestRef.current) setState({ status: "ready", plans, error: null });
      },
      (error) => {
        if (requestId === requestRef.current) setState({ status: "error", plans: [], error });
      },
    );
  }, [fetchPlans]);

  useEffect(() => {
    reload();
    return () => {
      requestRef.current += 1;
    };
  }, [reload]);

  return { ...state, reload };
}
