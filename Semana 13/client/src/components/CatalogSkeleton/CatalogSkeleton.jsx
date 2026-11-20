export default function CatalogSkeleton() {
  return (
    <div className="product-grid" role="status" aria-busy="true" aria-label="Cargando catálogo">
      {[1, 2, 3, 4].map((card) => (
        <div className="product-card product-card--skeleton" key={card}>
          <span className="skeleton skeleton__image" />
          <span className="skeleton skeleton__line" />
          <span className="skeleton skeleton__line skeleton__line--short" />
          <span className="skeleton skeleton__line" />
        </div>
      ))}
    </div>
  );
}
