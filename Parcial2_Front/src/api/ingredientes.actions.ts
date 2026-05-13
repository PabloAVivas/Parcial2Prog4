import type { IIngrediente, IIngredienteCreate, IIngredientePaginado, IIngredienteUpdate } from "../types/IIngrediente";

const API = "http://localhost:8000/ingredientes";

export async function getIngredientes(offset = 0, limit = 20, nombre?: string): Promise<IIngredientePaginado> {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (nombre) params.append("nombre", nombre);
  const res = await fetch(`${API}?${params}`);
  if (!res.ok) throw new Error("Error al obtener ingredientes");
  return res.json();
}

export async function getIngredienteById(id: number): Promise<IIngrediente> {
  const res = await fetch(`${API}/${id}`);
  if (!res.ok) throw new Error("Ingrediente no encontrado");
  return res.json();
}

export async function createIngrediente(data: IIngredienteCreate): Promise<IIngrediente> {
  const res = await fetch(API + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al crear ingrediente");
  }
  return res.json();
}

export async function updateIngrediente(id: number, data: IIngredienteUpdate): Promise<IIngrediente> {
  const res = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al actualizar ingrediente");
  }
  return res.json();
}

export async function deleteIngrediente(id: number): Promise<void> {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Error al eliminar ingrediente");
}
