import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProducts, createProduct, updateProduct, deleteProduct } from "../api/products.actions";
import type { IProduct, IProductCreate, IProductUpdate } from "../types/IProduct";
import { ProductForm } from "../hooks/ProductsForm";
import Modal from "./Modal";

export default function ProductsTable() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<IProduct | null>(null);
  const [mutError, setMutError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["productos", offset, appliedSearch],
    queryFn: () => getProducts(offset, limit, appliedSearch),
  });

  const createMut = useMutation({
    mutationFn: createProduct,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["productos"] }); closeModal(); },
    onError: (err: Error) => setMutError(err.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: IProductUpdate }) => updateProduct(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["productos"] }); closeModal(); },
    onError: (err: Error) => setMutError(err.message),
  });

  const deleteMut = useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["productos"] }),
  });

  const handleSubmit = (formData: IProductCreate | IProductUpdate) => {
    if (editing) updateMut.mutate({ id: editing.id, data: formData });
    else createMut.mutate(formData as IProductCreate);
  };

  const openEdit = (prod: IProduct) => { setEditing(prod); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); setMutError(null); };

  if (isLoading) return <div className="py-10 text-center text-gray-500">Cargando productos...</div>;
  if (isError) return <div className="py-10 text-center text-red-500">Error al cargar productos.</div>;

  const productos = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <div className="flex w-full sm:w-auto gap-2">
          <input
            type="text"
            placeholder="Nombre del producto..."
            className="flex-1 sm:w-64 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 outline-none"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button 
            onClick={() => { setOffset(0); setAppliedSearch(searchTerm); }}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-900 transition-colors"
          >
            Buscar
          </button>
        </div>
        <button onClick={() => setModalOpen(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
          + Nuevo Producto
        </button>
      </div>

      <article className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden overflow-x-auto">
        <table className="w-full text-left text-sm border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 font-medium uppercase text-[11px] tracking-wider">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Imagen</th>
              <th className="px-4 py-3">Nombre</th>
              <th className="px-4 py-3">Precio</th>
              <th className="px-4 py-3">Stock</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {productos.map((prod) => (
              <tr key={prod.id} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-4 py-3 font-mono text-gray-400">#{prod.id}</td>
                <td className="px-4 py-3">
                    <img src={prod.imagenes_url[0]} alt={prod.nombre} className="w-20 h-20 object-cover rounded-lg" />
                </td>
                <td className="px-4 py-3 font-medium text-gray-900">{prod.nombre}</td>
                <td className="px-4 py-3 text-gray-600">${prod.precio_base.toLocaleString()}</td>
                <td className="px-4 py-3 text-gray-600">{prod.stock_cantidad}</td>
                <td className="px-4 py-3">
                  <span className={`inline-block rounded-full px-2 py-0.5 text-[11px] font-bold uppercase ${prod.disponible ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {prod.disponible ? "Disponible" : "No disponible"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right space-x-3">
                  <Link to={`/detalle/${prod.id}`} className="text-gray-500 hover:text-blue-600 font-medium">Ver</Link>
                  <button onClick={() => openEdit(prod)} className="text-blue-600 hover:text-blue-800 font-medium cursor-pointer">Editar</button>
                  <button onClick={() => { if (confirm("¿Eliminar este producto?")) deleteMut.mutate(prod.id); }} className="text-red-600 hover:text-red-800 font-medium cursor-pointer">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      <Modal open={modalOpen} onClose={closeModal} title={editing ? "Editar Producto" : "Nuevo Producto"}>
        <ProductForm
          key={editing?.id ?? 'new'} 
          initial={editing}
          onSubmit={handleSubmit}
          isPending={createMut.isPending || updateMut.isPending}
          error={mutError}
        />
      </Modal>
    </div>
  );
}