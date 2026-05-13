// src/pages/IngredienteDetailPage.tsx
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getIngredienteById } from "../api/ingredientes.actions";

export default function IngredienteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const ingId = Number(id);

  const { data: ingrediente, isLoading, error } = useQuery({
    queryKey: ["ingrediente", ingId],
    queryFn: () => getIngredienteById(ingId),
    enabled: ingId > 0,
  });

  if (isLoading) return <p className="text-center py-20 text-gray-500">Cargando ingrediente...</p>;
  if (error) return <p className="text-center py-20 text-red-500">Error: {error.message}</p>;
  if (!ingrediente) return <p className="text-center py-20 text-gray-400">Ingrediente no encontrado</p>;

  return (
    <main className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/ingredientes" className="text-blue-600 hover:underline text-sm mb-6 inline-block">← Volver a ingredientes</Link>
      <article className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{ingrediente.nombre}</h1>
        <p className="text-gray-600 mb-6">{ingrediente.descripcion}</p>
        
        <div className="flex gap-4 mb-8">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${ingrediente.es_alergeno ? "bg-amber-100 text-amber-700" : "bg-blue-100 text-blue-700"}`}>
            {ingrediente.es_alergeno ? "⚠️ Contiene Alérgenos" : "✓ Libre de Alérgenos"}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${ingrediente.activo ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {ingrediente.activo ? "Disponible" : "No Disponible"}
          </span>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Productos que lo contienen</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {ingrediente.producto_links.map(p => (
              <Link key={p.id} to={`/detalle/${p.id}`} className="block p-4 border rounded-xl hover:border-blue-400 transition-all shadow-sm">
                <span className="font-semibold text-gray-800">{p.nombre}</span>
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>Stock: {p.stock_cantidad}</span>
                  <span>${p.precio_base}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </article>
    </main>
  );
}