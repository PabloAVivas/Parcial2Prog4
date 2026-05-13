import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getProductById } from "../api/products.actions";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const productId = Number(id);

  const { data: product, isLoading, error } = useQuery({
    queryKey: ["producto", productId],
    queryFn: () => getProductById(productId),
    enabled: productId > 0,
  });

  if (isLoading) return <p className="text-center py-20 text-gray-500">Cargando producto...</p>;
  if (error) return <p className="text-center py-20 text-red-500">Error: {error.message}</p>;
  if (!product) return <p className="text-center py-20 text-gray-400">Producto no encontrado</p>;

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/productos" className="text-blue-600 hover:underline text-sm mb-6 inline-block">← Volver a productos</Link>

      <article className="rounded-xl border border-gray-200 overflow-hidden">
        {product.imagenes_url.length > 0 && (
          <figure className="flex gap-2 p-4 bg-gray-50 overflow-x-auto">
            {product.imagenes_url.map((url, i) => (
              <img
                key={i}
                src={url}
                alt={`${product.nombre} - imagen ${i + 1}`}
                className="h-48 w-auto rounded-lg object-cover flex-shrink-0"
                onError={(e) => { (e.target as HTMLImageElement).src = "https://placehold.co/200x200?text=N/A"; }}
              />
            ))}
          </figure>
        )}

        <section className="p-6 space-y-4">
          <header className="flex items-start justify-between gap-4">
            <h1 className="text-2xl font-bold text-gray-800">{product.nombre}</h1>
            <span className={`rounded-full px-3 py-1 text-sm font-medium ${product.disponible ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
              {product.disponible ? "Disponible" : "No disponible"}
            </span>
          </header>

          <p className="text-gray-600">{product.descripcion}</p>

          <dl className="grid grid-cols-2 gap-4 text-sm">
            <dt className="text-gray-500">Precio base</dt>
            <dd className="font-semibold text-gray-800">${product.precio_base.toFixed(2)}</dd>
            <dt className="text-gray-500">Stock</dt>
            <dd className="font-semibold text-gray-800">{product.stock_cantidad} unidades</dd>
          </dl>

          {product.categorias.length > 0 && (
            <fieldset>
              <legend className="text-sm font-medium text-gray-500 mb-2">Categorías</legend>
              <ul className="flex flex-wrap gap-2">
                {product.categorias.map((c) => (
                  <li key={c.id} className={`rounded-full px-3 py-1 text-sm font-medium ${c.es_principal ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"}`}>
                    {c.nombre}{c.es_principal ? " (principal)" : ""}
                  </li>
                ))}
              </ul>
            </fieldset>
          )}

          {product.ingredientes.length > 0 && (
            <fieldset>
              <legend className="text-sm font-medium text-gray-500 mb-2">Ingredientes</legend>
              <ul className="flex flex-wrap gap-2">
                {product.ingredientes.map((i) => (
                  <li key={i.id} className={`rounded-full px-3 py-1 text-sm font-medium ${i.es_alergeno ? "bg-amber-100 text-amber-700" : "bg-gray-100 text-gray-600"}`}>
                    {i.nombre}
                    {i.es_alergeno && " ⚠️"}
                    {i.es_removible && " (removible)"}
                  </li>
                ))}
              </ul>
            </fieldset>
          )}

          <footer className="text-xs text-gray-400 pt-4 border-t border-gray-100">
            Creado: {new Date(product.created_at).toLocaleString()} · Actualizado: {new Date(product.updated_at).toLocaleString()}
          </footer>
        </section>
      </article>
    </main>
  );
}
