import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Navbar } from './components/Navbar'
import CategoriasPage from "./pages/CategoriasPage";
import CategoriaDetailPage from "./pages/CategoriaDetailPage";
import IngredientesPage from "./pages/IngredientesPage";
import IngredienteDetailPage from "./pages/IngredienteDetailPage";
import ProductsPage from "./pages/ProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false, retry: 1 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Navbar/>
        <Routes>
          <Route path="/" element={<Navigate to="/productos" replace />} />
          <Route path="/categorias" element={<CategoriasPage />} />
          <Route path="/detalle-categoria/:id" element={<CategoriaDetailPage />} />
          <Route path="/ingredientes" element={<IngredientesPage />} />
          <Route path="/detalle-ingrediente/:id" element={<IngredienteDetailPage />} />
          <Route path="/productos" element={<ProductsPage />} />
          <Route path="/detalle/:id" element={<ProductDetailPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
