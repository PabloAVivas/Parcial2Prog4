import { useState } from "react";
import type { IIngrediente, IIngredienteCreate, IIngredienteUpdate } from "../types/IIngrediente";

interface IngredienteFormProps {
  initial?: IIngrediente | null;
  onSubmit: (data: IIngredienteCreate | IIngredienteUpdate) => void;
  isPending: boolean;
  error: string | null;
}

export function IngredienteForm({ initial, onSubmit, isPending, error }: IngredienteFormProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? "");
  const [descripcion, setDescripcion] = useState(initial?.descripcion ?? "");
  const [esAlergeno, setEsAlergeno] = useState(initial?.es_alergeno ?? false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ nombre, descripcion, es_alergeno: esAlergeno });
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
        <label className="block text-xs font-medium text-gray-500 mb-1">Descripción</label>
        <textarea className={inputClass} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} rows={3} />
      </div>
      <label className="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" checked={esAlergeno} onChange={(e) => setEsAlergeno(e.target.checked)} className="w-4 h-4 text-blue-600" />
        <span className="text-sm text-gray-700 font-medium">Contiene Alérgenos</span>
      </label>
      <button type="submit" disabled={isPending} className="w-full bg-blue-600 text-white font-semibold py-2 rounded-lg hover:bg-blue-700 transition-colors">
        {isPending ? "Guardando..." : initial ? "Actualizar" : "Crear"}
      </button>
    </form>
  );
}