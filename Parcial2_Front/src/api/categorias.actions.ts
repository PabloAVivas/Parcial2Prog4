import type { ICategoria, ICategoriaCreate, ICategoriaPaginada, ICategoriaUpdate } from "../types/ICategoria";

const API = "http://localhost:8000/categorias";

export async function getCategorias(offset = 0, limit = 20, nombre?: string): Promise<ICategoriaPaginada> {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (nombre) params.append("nombre", nombre);
  const res = await fetch(`${API}?${params}`);
  if (!res.ok) throw new Error("Error al obtener categorías");
  return res.json();
}

export async function getCategoriaById(id: number): Promise<ICategoria> {
  const res = await fetch(`${API}/${id}`);
  if (!res.ok) throw new Error("Categoría no encontrada");
  return res.json();
}

export async function createCategoria(data: ICategoriaCreate): Promise<ICategoria> {
  const res = await fetch(API + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al crear categoría");
  }
  return res.json();
}

export async function updateCategoria(id: number, data: ICategoriaUpdate): Promise<ICategoria> {
  const res = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al actualizar categoría");
  }
  return res.json();
}

export async function deleteCategoria(id: number): Promise<void> {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Error al eliminar categoría");
}
