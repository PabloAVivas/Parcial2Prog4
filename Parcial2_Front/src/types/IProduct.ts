export interface ICategoriaBasicCreate {
  id: number;
  es_principal: boolean;
}

export interface IIngredienteBasicCreate {
  id: number;
  es_removible: boolean;
}

export interface ICategoriaBasicRead {
  id: number;
  nombre: string;
  es_principal: boolean;
}

export interface IIngredienteBasicRead {
  id: number;
  nombre: string;
  es_alergeno: boolean;
  es_removible: boolean;
}

export interface IProduct {
  id: number;
  nombre: string;
  descripcion: string;
  precio_base: number;
  imagenes_url: string[];
  stock_cantidad: number;
  categorias: ICategoriaBasicRead[];
  ingredientes: IIngredienteBasicRead[];
  disponible: boolean;
  created_at: string;
  updated_at: string;
}

export interface IProductCreate {
  nombre: string;
  descripcion: string;
  precio_base: number;
  imagenes_url: string[];
  stock_cantidad: number;
  disponible?: boolean;
  categorias: ICategoriaBasicCreate[];
  ingredientes: IIngredienteBasicCreate[];
}

export interface IProductUpdate {
  nombre?: string;
  descripcion?: string;
  precio_base?: number;
  imagenes_url?: string[];
  stock_cantidad?: number;
  disponible?: boolean;
  categorias?: ICategoriaBasicCreate[];
  ingredientes?: IIngredienteBasicCreate[];
}

export interface IProductPaginado {
  total: number;
  data: IProduct[];
}
