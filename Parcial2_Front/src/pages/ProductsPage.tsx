import ProductsTable from "../components/ProductsTable";

export default function ProductsPage() {
  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Productos</h1>
      <ProductsTable />
    </main>
  );
}
