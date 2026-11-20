import { useRef } from "react";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";
import useWindowSize from "../hooks/useWindowSize.js";
import Button from "./Button.jsx";

export default function PremieresCarousel({ premieres }) {
  const trackRef = useRef(null);
  const { width } = useWindowSize();
  const visibleColumns = width >= 1024 ? 3 : width >= 640 ? 2 : 1;

  function scroll(direction) {
    const track = trackRef.current;
    if (!track) {
      return;
    }
    const card = track.querySelector(".premiere-card");
    const step = card ? card.getBoundingClientRect().width + 16 : track.clientWidth;
    track.scrollBy({ left: direction * step * visibleColumns, behavior: "smooth" });
  }

  return (
    <div className="premieres-carousel">
      <Button
        variant="secondary"
        className="carousel__control carousel__control--prev"
        onClick={() => scroll(-1)}
        aria-label="Ver estrenos anteriores"
      >
        <ChevronLeft size={18} aria-hidden="true" />
      </Button>

      <ul
        className="premieres-track"
        ref={trackRef}
        style={{ "--visible-columns": visibleColumns }}
      >
        {premieres.map((premiere) => (
          <li className="premiere-card" key={premiere.id}>
            <img
              className="premiere-card__image"
              src={premiere.image}
              alt={premiere.title}
            />
            <h3>{premiere.title}</h3>
            <p className="premiere-card__date u-muted">
              <CalendarDays size={14} aria-hidden="true" />
              {premiere.releaseDate}
            </p>
            <span className="premiere-card__badge">{premiere.classification}</span>
          </li>
        ))}
      </ul>

      <Button
        variant="secondary"
        className="carousel__control carousel__control--next"
        onClick={() => scroll(1)}
        aria-label="Ver estrenos siguientes"
      >
        <ChevronRight size={18} aria-hidden="true" />
      </Button>
    </div>
  );
}
