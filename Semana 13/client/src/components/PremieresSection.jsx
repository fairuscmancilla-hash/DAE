import { RefreshCw, TriangleAlert } from "lucide-react";
import usePremieres from "../hooks/usePremieres.js";
import Button from "./Button.jsx";
import PremieresCarousel from "./PremieresCarousel.jsx";
import PremieresSkeleton from "./PremieresSkeleton.jsx";

export default function PremieresSection() {
  const { status, premieres, error, retry } = usePremieres();

  return (
    <section
      id="proximamente"
      className="section premieres"
      aria-labelledby="proximamente-titulo"
    >
      <div className="section__heading">
        <div>
          <h2 id="proximamente-titulo">Próximos estrenos</h2>
          <p className="u-muted u-mb-0">Carga, datos y error del servicio simulado.</p>
        </div>
        <div className="premieres__actions">
          <Button variant="ghost" onClick={() => retry(true)}>
            Simular error
          </Button>
          <Button variant="secondary" onClick={() => retry(false)}>
            <RefreshCw size={16} aria-hidden="true" />
            Recargar
          </Button>
        </div>
      </div>

      {status === "loading" && (
        <div aria-busy="true" aria-live="polite">
          <p className="premieres__status">Cargando estrenos…</p>
          <PremieresSkeleton count={3} />
        </div>
      )}

      {status === "error" && (
        <div className="premieres__error" role="alert">
          <TriangleAlert size={28} aria-hidden="true" />
          <div>
            <h3>No pudimos cargar los estrenos</h3>
            <p>{error?.message ?? "Error desconocido."}</p>
          </div>
          <Button variant="primary" onClick={() => retry(false)}>
            Reintentar
          </Button>
        </div>
      )}

      {status === "success" && <PremieresCarousel premieres={premieres} />}
    </section>
  );
}
