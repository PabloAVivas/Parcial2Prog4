import { useState } from "react";
import { useQuery, } from "@tanstack/react-query";
import { getCategorias } from "../api/categorias.actions";
import { getIngredientes } from "../api/ingredientes.actions";
import type { IProduct, IProductCreate, IProductUpdate, ICategoriaBasicCreate, IIngredienteBasicCreate } from "../types/IProduct";

interface ProductFormProps {
  initial?: IProduct | null;
  onSubmit: (data: IProductCreate | IProductUpdate) => void;
  isPending: boolean;
  error: string | null;
}

export function ProductForm({ initial, onSubmit, isPending, error }: ProductFormProps) {
  const [nombre, setNombre] = useState(initial?.nombre ?? "");
  const [descripcion, setDescripcion] = useState(initial?.descripcion ?? "");
  const [precioBase, setPrecioBase] = useState(initial?.precio_base ?? 0);
  const [imagenesUrl, setImagenesUrl] = useState(initial?.imagenes_url?.join("\n") ?? "");
  const [stockCantidad, setStockCantidad] = useState(initial?.stock_cantidad ?? 0);
  const [disponible, setDisponible] = useState(initial?.disponible ?? true);
  
  const [selectedCats, setSelectedCats] = useState<ICategoriaBasicCreate[]>(
    initial?.categorias?.map((c) => ({ id: c.id, es_principal: c.es_principal })) ?? []
  );
  const [selectedIngs, setSelectedIngs] = useState<IIngredienteBasicCreate[]>(
    initial?.ingredientes?.map((i) => ({ id: i.id, es_removible: i.es_removible })) ?? []
  );

  const { data: catData } = useQuery({ queryKey: ["categorias-select"], queryFn: () => getCategorias(0, 100) });
  const { data: ingData } = useQuery({ queryKey: ["ingredientes-select"], queryFn: () => getIngredientes(0, 100) });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      nombre,
      descripcion,
      precio_base: precioBase,
      imagenes_url: imagenesUrl.split("\n").filter(u => u.trim()),
      stock_cantidad: stockCantidad,
      disponible,
      categorias: selectedCats,
      ingredientes: selectedIngs
    };
    onSubmit(data);
  };

  const inputClass = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</p>}
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Nombre</label>
          <input className={inputClass} value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Precio Base</label>
          <input type="number" className={inputClass} value={precioBase} onChange={(e) => setPrecioBase(Number(e.target.value))} required />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Descripción</label>
        <textarea className={inputClass} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} rows={2} />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500 mb-1">Imágenes (una por línea)</label>
        <textarea className={inputClass} value={imagenesUrl} onChange={(e) => setImagenesUrl(e.target.value)} rows={2} placeholder="https://..." />
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-500 mb-1">Stock</label>
          <input type="number" className={inputClass} value={stockCantidad} onChange={(e) => setStockCantidad(Number(e.target.value))} required />
        </div>
        <label className="flex items-center gap-2 mt-5 cursor-pointer">
          <input type="checkbox" checked={disponible} onChange={(e) => setDisponible(e.target.checked)} className="w-4 h-4 text-blue-600" />
          <span className="text-sm text-gray-700">Disponible</span>
        </label>
      </div>

      <div className="grid grid-cols-2 gap-4 border-t pt-4">
        <div>
          <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Categorías</h4>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {catData?.data.map(c => (
              <label key={c.id} className="flex items-center gap-2 text-sm p-1 hover:bg-gray-50 rounded cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={selectedCats.some(sc => sc.id === c.id)} 
                  onChange={(e) => {
                    if(e.target.checked) setSelectedCats([...selectedCats, { id: c.id, es_principal: false }]);
                    else setSelectedCats(selectedCats.filter(sc => sc.id !== c.id));
                  }}
                />
                <span className="flex-1">{c.nombre}</span>
                {selectedCats.some(sc => sc.id === c.id) && (
                  <button 
                    type="button"
                    onClick={() => setSelectedCats(selectedCats.map(sc => sc.id === c.id ? { ...sc, es_principal: !sc.es_principal } : sc))}
                    className={`text-[10px] px-1 rounded ${selectedCats.find(sc => sc.id === c.id)?.es_principal ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
                  >
                    Principal
                  </button>
                )}
              </label>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Ingredientes</h4>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {ingData?.data.map(i => (
              <label key={i.id} className="flex items-center gap-2 text-sm p-1 hover:bg-gray-50 rounded cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={selectedIngs.some(si => si.id === i.id)} 
                  onChange={(e) => {
                    if(e.target.checked) setSelectedIngs([...selectedIngs, { id: i.id, es_removible: false }]);
                    else setSelectedIngs(selectedIngs.filter(si => si.id !== i.id));
                  }}
                />
                <span className="flex-1">{i.nombre}</span>
                {selectedIngs.some(si => si.id === i.id) && (
                  <button 
                    type="button"
                    onClick={() => setSelectedIngs(selectedIngs.map(si => si.id === i.id ? { ...si, es_removible: !si.es_removible } : si))}
                    className={`text-[10px] px-1 rounded ${selectedIngs.find(si => si.id === i.id)?.es_removible ? 'bg-amber-600 text-white' : 'bg-gray-200'}`}
                  >
                    Removible
                  </button>
                )}
              </label>
            ))}
          </div>
        </div>
      </div>

      <button type="submit" disabled={isPending} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition-colors disabled:opacity-50">
        {isPending ? "Guardando..." : initial ? "Actualizar Producto" : "Crear Producto"}
      </button>
    </form>
  );
}