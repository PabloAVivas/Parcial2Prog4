export interface ICategoriaShort {
  id: number;
  nombre: string;
}

export interface IProductoBasicRead {
  id: number;
  nombre: string;
  precio_base: number;
  stock_cantidad: number;
}

export interface ICategoria {
  id: number;
  padre: ICategoriaShort | null;
  nombre: string;
  descripcion: string;
  imagen_url: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  productos: IProductoBasicRead[];
}

export interface ICategoriaCreate {
  nombre: string;
  descripcion: string;
  imagen_url: string;
  parent_id?: number | null;
}

export interface ICategoriaUpdate {
  nombre?: string;
  descripcion?: string;
  imagen_url?: string;
  parent_id?: number | null;
}

export interface ICategoriaPaginada {
  total: number;
  data: ICategoria[];
}
