import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getIngredientes, createIngrediente, updateIngrediente, deleteIngrediente } from "../api/ingredientes.actions";
import type { IIngrediente, IIngredienteCreate, IIngredienteUpdate } from "../types/IIngrediente";
import { IngredienteForm } from "../hooks/IngredientesForm";
import Modal from "./Modal";


export default function IngredientesTable() {
  const queryClient = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<IIngrediente | null>(null);
  const [mutError, setMutError] = useState<string | null>(null);
  
  const [searchTerm, setSearchTerm] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["ingredientes", appliedSearch],
    queryFn: () => getIngredientes(0, 50, appliedSearch),
  });

  const createMut = useMutation({
    mutationFn: createIngrediente,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["ingredientes"] }); closeModal(); },
    onError: (err: Error) => setMutError(err.message),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: IIngredienteUpdate }) => updateIngrediente(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["ingredientes"] }); closeModal(); },
    onError: (err: Error) => setMutError(err.message),
  });

  const deleteMut = useMutation({
    mutationFn: deleteIngrediente,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ingredientes"] }),
  });

  const openEdit = (ing: IIngrediente) => { setEditing(ing); setModalOpen(true); };
  const closeModal = () => { setModalOpen(false); setEditing(null); setMutError(null); };

  const handleSubmit = (formData: IIngredienteCreate | IIngredienteUpdate) => {
    if (editing) updateMut.mutate({ id: editing.id, data: formData });
    else createMut.mutate(formData as IIngredienteCreate);
  };

  if (isLoading) return <div className="py-10 text-center text-gray-500">Cargando...</div>;

  const ingredientes = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <input
            className="border rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-blue-500 w-64"
            placeholder="Buscar ingrediente..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button onClick={() => setAppliedSearch(searchTerm)} className="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm">Buscar</button>
        </div>
        <button onClick={() => setModalOpen(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700">+ Nuevo</button>
      </div>

      <article className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b text-gray-500 uppercase text-[11px] tracking-wider">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Nombre</th>
              <th className="px-4 py-3">Alérgeno</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {ingredientes.map(ing => (
              <tr key={ing.id} className="hover:bg-gray-50/50">
                <td className="px-4 py-3 text-gray-400">#{ing.id}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{ing.nombre}</td>
                <td className="px-4 py-3">
                   {ing.es_alergeno ? <span className="text-amber-600 font-bold">⚠️ Sí</span> : <span className="text-gray-400">No</span>}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${ing.activo ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {ing.activo ? "Activo" : "Inactivo"}
                  </span>
                </td>
                <td className="px-4 py-3 text-right space-x-3">
                  <Link to={`/detalle-ingrediente/${ing.id}`} className="text-gray-500 hover:text-blue-600">Ver</Link>
                  <button onClick={() => openEdit(ing)} className="text-blue-600 hover:underline cursor-pointer">Editar</button>
                  <button onClick={() => { if (confirm("¿Eliminar?")) deleteMut.mutate(ing.id); }} className="text-red-600 hover:underline cursor-pointer">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>

      <Modal open={modalOpen} onClose={closeModal} title={editing ? "Editar Ingrediente" : "Nuevo Ingrediente"}>
        <IngredienteForm key={editing?.id ?? 'new'} initial={editing} onSubmit={handleSubmit} isPending={createMut.isPending || updateMut.isPending} error={mutError} />
      </Modal>
    </div>
  );
}