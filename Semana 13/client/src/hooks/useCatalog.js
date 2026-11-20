import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { categoryService, productService } from "../services/index.js";

const INITIAL = {
  status: "loading",
  products: [],
  categories: [],
  error: null,
  selectedCategory: "all",
};

// One effect loads both collections; the filter is applied in memory so the
// category chips do not trigger an extra request per click.
export default function useCatalog() {
  const [state, setState] = useState(INITIAL);
  const requestRef = useRef(0);

  const load = useCallback(() => {
    const requestId = ++requestRef.current;
    setState((current) => ({ ...current, status: "loading", error: null }));

    Promise.all([
      productService.list({ page_size: 20 }),
      categoryService.list({ page_size: 20 }),
    ]).then(
      ([products, categories]) => {
        if (requestId === requestRef.current) {
          setState((current) => ({
            ...current,
            status: "ready",
            products: products.results,
            categories: categories.results,
            error: null,
          }));
        }
      },
      (error) => {
        if (requestId === requestRef.current) {
          setState((current) => ({ ...current, status: "error", error }));
        }
      },
    );
  }, []);

  useEffect(() => {
    load();
    return () => {
      requestRef.current += 1;
    };
  }, [load]);

  const selectCategory = useCallback((id) => {
    setState((current) => ({ ...current, selectedCategory: id }));
  }, []);

  const visibleProducts = useMemo(() => {
    if (state.selectedCategory === "all") return state.products;
    return state.products.filter(
      (product) => String(product.category?.id) === String(state.selectedCategory),
    );
  }, [state.products, state.selectedCategory]);

  const mutate = useCallback(
    async (operation) => {
      await operation();
      load();
    },
    [load],
  );

  return {
    ...state,
    visibleProducts,
    reload: load,
    selectCategory,
    createProduct: (values) => mutate(() => productService.create(values)),
    updateProduct: (id, values) => mutate(() => productService.update(id, values)),
    removeProduct: (id) => mutate(() => productService.remove(id)),
  };
}
