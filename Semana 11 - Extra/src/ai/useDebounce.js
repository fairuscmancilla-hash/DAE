import { useEffect, useState } from "react";

export default function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value);

  // Limpieza en el MISMO efecto: cada cambio cancela el temporizador anterior.
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
