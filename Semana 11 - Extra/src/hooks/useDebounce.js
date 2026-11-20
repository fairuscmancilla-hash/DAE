import { useEffect, useState } from "react";

// Devuelve el último valor que lleva `delay` ms sin cambiar.
// El primer dibujado devuelve `value` tal cual; cada cambio cancela el temporizador anterior.
export default function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
