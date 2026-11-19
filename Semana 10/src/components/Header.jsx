// Header receives the cinema name and the navigation links from App.
export default function Header({ name, links }) {
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
    </header>
  );
}
