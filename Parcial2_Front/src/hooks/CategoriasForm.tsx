import { useState } from "react";
import type { ICategoria, ICategoriaCreate, ICategoriaUpdate } from "../types/ICategoria";

interface CategoriaFormProps {
  initial?: ICategoria | null;
  categorias: ICategoria[];
  onSubmit: (data: ICategoriaCreate | ICategoriaUpdate) => void;
  isPending: boolean;
  error: string | null;
}

export function CategoriaForm({ initial, categorias, onSubmit, isPending, error }: CategoriaFormProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? "");
  const [descripcion, setDescripcion] = useState(initial?.descripcion ?? "");
  const [imagenUrl, setImagenUrl] = useState(initial?.imagen_url ?? "");
  const [parentId, setParentId] = useState<number | null>(initial?.padre?.id ?? null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ nombre, descripcion, imagen_url: imagenUrl, parent_id: parentId || null });
  };

  const inputClass = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 outline-none";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>}
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Nombre</label>
        <input className={inputClass} value={nombre} onChange={(e) => setNombre(e.target.value)} required />
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Imagen URL</label>
        <input className={inputClass} value={imagenUrl} onChange={(e) => setImagenUrl(e.target.value)} />
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Categoría Padre</label>
        <select className={inputClass} value={parentId || ""} onChange={(e) => setParentId(Number(e.target.value) || null)}>
          <option value="">Ninguna (Nivel Raíz)</option>
          {categorias.filter(c => c.id !== initial?.id).map(c => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Descripción</label>
        <textarea className={inputClass} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} rows={3} />
      </div>
      <button type="submit" disabled={isPending} className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50">
        {isPending ? "Guardando..." : initial ? "Actualizar" : "Crear"}
      </button>
    </form>
  );
}