import { NavLink } from 'react-router-dom'

const links = [
  { to: "/categorias", label: "Categorías" },
  { to: "/ingredientes", label: "Ingredientes" },
  { to: "/productos", label: "Productos" },
];

export function Navbar() {
  return (
        <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
          <ul className="max-w-7xl mx-auto px-4 flex items-center gap-1 h-14">
            <li className="mr-auto">
              <span className="text-lg font-bold text-gray-800">FOOD STORE</span>
            </li>
            {links.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
  )
}