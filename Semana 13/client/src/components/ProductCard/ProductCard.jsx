const money = new Intl.NumberFormat("es-PE", {
  style: "currency",
  currency: "PEN",
});

export default function ProductCard({ product, onEdit, onDelete }) {
  return (
    <article className="product-card">
      <img src={product.image_url || product.image} alt={product.name} loading="lazy" />
      <div className="product-card__body">
        <span className="product-card__category">{product.category?.name}</span>
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        <div className="product-card__meta">
          <strong>{money.format(Number(product.price))}</strong>
          <span>{product.stock} und.</span>
        </div>
        <div className="product-card__actions">
          <button className="btn btn-secondary btn-sm" onClick={() => onEdit(product)}>
            Editar
          </button>
          <button className="btn btn-danger btn-sm" onClick={() => onDelete(product)}>
            Eliminar
          </button>
        </div>
      </div>
    </article>
  );
}
