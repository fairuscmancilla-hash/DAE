export default function CategoryFilter({ categories, selected, onSelect }) {
  return (
    <div className="category-filter" role="group" aria-label="Filtrar por categoría">
      <button
        className={selected === "all" ? "is-active" : ""}
        onClick={() => onSelect("all")}
      >
        Todas
      </button>
      {categories.map((category) => (
        <button
          key={category.id}
          className={String(selected) === String(category.id) ? "is-active" : ""}
          onClick={() => onSelect(category.id)}
        >
          {category.name}
          <span>{category.product_count}</span>
        </button>
      ))}
    </div>
  );
}
