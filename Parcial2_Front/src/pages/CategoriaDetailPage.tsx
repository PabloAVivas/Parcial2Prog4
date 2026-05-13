// src/pages/CategoriaDetailPage.tsx
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getCategoriaById } from "../api/categorias.actions";

export default function CategoriaDetailPage() {
  const { id } = useParams<{ id: string }>();
  const catId = Number(id);

  const { data: categoria, isLoading, error } = useQuery({
    queryKey: ["categoria", catId],
    queryFn: () => getCategoriaById(catId),
    enabled: catId > 0,
  });

  if (isLoading) return <p className="text-center py-20 text-gray-500">Cargando categoría...</p>;
  if (error) return <p className="text-center py-20 text-red-500">Error: {error.message}</p>;
  if (!categoria) return <p className="text-center py-20 text-gray-400">Categoría no encontrada</p>;

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/categorias" className="text-blue-600 hover:underline text-sm mb-6 inline-block">← Volver a categorías</Link>
      <article className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex gap-6 mb-6">
          {categoria.imagen_url && (
            <img src={categoria.imagen_url} alt={categoria.nombre} className="w-32 h-32 object-cover rounded-lg border" />
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{categoria.nombre}</h1>
            <p className="text-gray-600 mt-2">{categoria.descripcion}</p>
            <span className={`inline-block mt-3 px-3 py-1 rounded-full text-sm font-medium ${categoria.activo ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
              {categoria.activo ? "Activa" : "Inactiva"}
            </span>
          </div>
        </div>

        {categoria.padre && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Categoría Padre</h3>
            <p className="text-gray-800">{categoria.padre.nombre}</p>
          </div>
        )}

        <div>
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Productos Relacionados</h3>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {categoria.productos.map(p => (
              <li key={p.id} className="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                <Link to={`/detalle/${p.id}`} className="text-blue-600 font-medium">{p.nombre}</Link>
                <p className="text-sm text-gray-500">${p.precio_base.toLocaleString()}</p>
              </li>
            ))}
          </ul>
        </div>
      </article>
    </main>
  );
}