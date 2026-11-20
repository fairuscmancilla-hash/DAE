// Loading state: same layout as the carousel, without content.
export default function PremieresSkeleton({ count = 3 }) {
  return (
    <ul className="premieres-track" aria-hidden="true">
      {Array.from({ length: count }, (_, index) => (
        <li className="premiere-skeleton" key={index}>
          <div className="skeleton skeleton--poster" />
          <div className="skeleton skeleton--line" />
          <div className="skeleton skeleton--line skeleton--short" />
        </li>
      ))}
    </ul>
  );
}
