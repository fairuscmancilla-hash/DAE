import { useEffect, useState } from "react";

const readSize = () => ({
  width: typeof window === "undefined" ? 1024 : window.innerWidth,
  height: typeof window === "undefined" ? 768 : window.innerHeight,
});

// Shared viewport state: MovieList and PremieresCarousel derive their columns.
export default function useWindowSize() {
  const [size, setSize] = useState(readSize);

  useEffect(() => {
    const handleResize = () => setSize(readSize());
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return size;
}
