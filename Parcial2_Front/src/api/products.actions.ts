import type { IProduct, IProductCreate, IProductPaginado, IProductUpdate } from "../types/IProduct";

const API = "http://localhost:8000/productos";

export async function getProducts(offset = 0, limit = 20, nombre?: string): Promise<IProductPaginado> {
  const params = new URLSearchParams({ offset: String(offset), limit: String(limit) });
  if (nombre) params.append("nombre", nombre);
  const res = await fetch(`${API}?${params}`);
  if (!res.ok) throw new Error("Error al obtener productos");
  return res.json();
}

export async function getProductById(id: number): Promise<IProduct> {
  const res = await fetch(`${API}/${id}`);
  if (!res.ok) throw new Error("Producto no encontrado");
  return res.json();
}

export async function createProduct(data: IProductCreate): Promise<IProduct> {
  const res = await fetch(API + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al crear producto");
  }
  return res.json();
}

export async function updateProduct(id: number, data: IProductUpdate): Promise<IProduct> {
  const res = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al actualizar producto");
  }
  return res.json();
}

export async function deleteProduct(id: number): Promise<void> {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Error al eliminar producto");
}
