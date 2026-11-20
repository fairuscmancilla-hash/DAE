import { useEffect, useRef, useState } from "react";
import { premieresPayload } from "../data/premieres.js";
import { adaptPremieres } from "../lib/movieAdapter.js";

// Simulates a request with three explicit states: loading, success and error.
export default function usePremieres({ delay = 1100 } = {}) {
  const [status, setStatus] = useState("loading");
  const [premieres, setPremieres] = useState([]);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);
  const requestRef = useRef(0);

  function startRequest(shouldFail = false) {
    const requestId = ++requestRef.current;
    window.clearTimeout(timerRef.current);
    setStatus("loading");
    setError(null);

    timerRef.current = window.setTimeout(() => {
      if (requestId !== requestRef.current) {
        return;
      }

      if (shouldFail) {
        setPremieres([]);
        setError(new Error("El servicio de estrenos no respondió. Inténtalo de nuevo."));
        setStatus("error");
        return;
      }

      setPremieres(adaptPremieres(premieresPayload));
      setStatus("success");
    }, delay);
  }

  useEffect(() => {
    startRequest(false);
    return () => window.clearTimeout(timerRef.current);
  }, [delay]);

  return {
    status,
    premieres,
    error,
    retry: startRequest,
  };
}
