import CategoriasTable from "../components/CategoriasTable";

export default function CategoriasPage() {
  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Categorías</h1>
      <CategoriasTable />
    </main>
  );
}
