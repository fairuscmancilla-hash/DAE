import { useEffect, useState } from "react";
import Button from "../components/Button.jsx";
import { categoryService, describeApiError, productService } from "../services/index.js";

const EMPTY = { name: "", description: "", price: "", stock: 0, category_id: "", image: null };

export default function ProductFormPage({ editingId, onNavigate }) {
  const [form, setForm] = useState(EMPTY);
  const [categories, setCategories] = useState([]);
  const [preview, setPreview] = useState("");
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    Promise.all([
      categoryService.list({ page_size: 20 }),
      editingId ? productService.get(editingId) : Promise.resolve(null),
    ]).then(
      ([categoryPage, product]) => {
        if (!alive) return;
        setCategories(categoryPage.results);
        if (product) {
          setForm({
            name: product.name,
            description: product.description,
            price: product.price,
            stock: product.stock,
            category_id: String(product.category?.id || ""),
            image: null,
          });
          setPreview(product.image_url || product.image || "");
        } else if (categoryPage.results.length) {
          setForm((current) => ({
            ...current,
            category_id: String(categoryPage.results[0].id),
          }));
        }
        setStatus("ready");
      },
      (err) => {
        if (!alive) return;
        setError(describeApiError(err));
        setStatus("error");
      },
    );
    return () => {
      alive = false;
    };
  }, [editingId]);

  function change(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function pickImage(event) {
    const file = event.target.files?.[0] || null;
    change("image", file);
    setPreview(file ? URL.createObjectURL(file) : preview);
  }

  async function submit(event) {
    event.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await productService.update(editingId, form);
      } else {
        await productService.create(form);
      }
      onNavigate("catalog");
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  if (status === "error") {
    return (
      <section className="section catalog-page">
        <div className="api-error" role="alert">{error}</div>
        <Button variant="secondary" onClick={() => onNavigate("catalog")}>Volver al catálogo</Button>
      </section>
    );
  }

  return (
    <section className="section catalog-page" aria-labelledby="product-form-title">
      <div className="section__heading">
        <div>
          <h2 id="product-form-title">{editingId ? "Editar producto" : "Nuevo producto"}</h2>
          <p>Formulario controlado · categorías cargadas por categoryService</p>
        </div>
        <Button variant="ghost" onClick={() => onNavigate("catalog")}>← Volver al catálogo</Button>
      </div>

      {status === "loading" && <p role="status">Cargando categorías…</p>}

      {status === "ready" && (
        <form className="product-form" onSubmit={submit} noValidate>
          <label>
            Nombre
            <input value={form.name} onChange={(e) => change("name", e.target.value)} />
          </label>

          <label>
            Descripción
            <textarea rows="3" value={form.description} onChange={(e) => change("description", e.target.value)} />
          </label>

          <div className="product-form__row">
            <label>
              Precio
              <input type="number" step="0.01" min="0" value={form.price} onChange={(e) => change("price", e.target.value)} />
            </label>
            <label>
              Existencias
              <input type="number" min="0" value={form.stock} onChange={(e) => change("stock", e.target.value)} />
            </label>
          </div>

          <label>
            Categoría
            <select value={form.category_id} onChange={(e) => change("category_id", e.target.value)}>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>{category.name}</option>
              ))}
            </select>
          </label>

          <label>
            Imagen {editingId && "(déjala vacía para conservar la actual)"}
            <input type="file" accept="image/*" onChange={pickImage} />
          </label>
          {preview && <img className="product-form__preview" src={preview} alt="Vista previa" />}

          {error && <div className="api-error api-error--form" role="alert">{error}</div>}

          <div className="api-actions">
            <Button type="submit" variant="primary">
              {editingId ? "Guardar cambios" : "Crear producto"}
            </Button>
            <Button variant="ghost" onClick={() => setForm(EMPTY)}>Limpiar</Button>
          </div>
        </form>
      )}
    </section>
  );
}
