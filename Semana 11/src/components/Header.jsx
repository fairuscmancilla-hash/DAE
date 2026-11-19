import { Heart } from "lucide-react";

// Header only receives the count, never the favorites list.
export default function Header({ name, links, favoriteCount = 0 }) {
  return (
    <header className="site-header">
      <h1>{name}</h1>
      <nav aria-label="Principal">
        <ul>
          {links.map((link) => (
            <li key={link.href}>
              <a href={link.href}>{link.label}</a>
            </li>
          ))}
        </ul>
      </nav>
      <span className="favorite-counter" aria-label={`${favoriteCount} favoritas`}>
        <Heart size={18} aria-hidden="true" />
        <strong>{favoriteCount}</strong>
        <span className="u-visually-hidden">favoritas</span>
      </span>
    </header>
  );
}
