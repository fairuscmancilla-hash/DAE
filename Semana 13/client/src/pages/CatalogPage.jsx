import Button from "../components/Button.jsx";
import CatalogError from "../components/CatalogError/index.js";
import CatalogSkeleton from "../components/CatalogSkeleton/index.js";
import CategoryFilter from "../components/CategoryFilter/index.js";
import ProductGrid from "../components/ProductGrid/index.js";
import useCatalog from "../hooks/useCatalog.js";
import { describeApiError } from "../services/index.js";

export default function CatalogPage({ onNavigate }) {
  const {
    status,
    categories,
    error,
    visibleProducts,
    selectedCategory,
    selectCategory,
    reload,
    removeProduct,
  } = useCatalog();

  async function handleDelete(product) {
    if (!window.confirm(`¿Eliminar "${product.name}"?`)) return;
    try {
      await removeProduct(product.id);
    } catch (err) {
      window.alert(describeApiError(err));
    }
  }

  return (
    <section className="section catalog-page" aria-labelledby="catalog-title">
      <div className="section__heading">
        <div>
          <h2 id="catalog-title">Catálogo de productos</h2>
          <p>Django REST Framework + servicios de Axios · una sola petición por producto</p>
        </div>
        <Button variant="primary" onClick={() => onNavigate("product-new")}>
          + Nuevo producto
        </Button>
      </div>

      {status === "loading" && <CatalogSkeleton />}
      {status === "error" && <CatalogError message={describeApiError(error)} onRetry={reload} />}
      {status === "ready" && (
        <>
          <CategoryFilter
            categories={categories}
            selected={selectedCategory}
            onSelect={selectCategory}
          />
          <p className="catalog-count" role="status">
            {visibleProducts.length} producto(s) · categorías cargadas desde la API
          </p>
          <ProductGrid
            products={visibleProducts}
            onEdit={(product) => onNavigate("product-edit", product.id)}
            onDelete={handleDelete}
          />
        </>
      )}
    </section>
  );
}
