import React from "react";
import { empresa } from "../../data";
import logo from "../../assets/images/logo.png"; // Ajusta el nombre si es diferente

const Header = () => {
  return (
    <header className="bg-[#0077B6] text-white shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        {/* Logo y nombre */}
        <div className="flex items-center gap-3">
          <img
            src={logo}
            alt="Minelva Los Morros"
            className="w-24 h-24 object-contain"
          />
          <div>
            <div className="font-bold text-lg leading-tight">Minelva</div>
            <div className="text-xs text-blue-200">Los Morros C.A.</div>
          </div>
        </div>

        {/* Menú desktop */}
        <nav className="hidden md:flex space-x-8">
          <a href="#inicio" className="hover:text-[#00B4D8] transition">
            Inicio
          </a>
          <a href="#servicios" className="hover:text-[#00B4D8] transition">
            Servicios
          </a>
          <a href="#productos" className="hover:text-[#00B4D8] transition">
            Productos
          </a>
          <a href="#contacto" className="hover:text-[#00B4D8] transition">
            Contacto
          </a>
        </nav>

        {/* Botón WhatsApp */}
        <a
          href={`https://wa.me/58${empresa.telefono}`}
          target="_blank"
          rel="noopener noreferrer"
          className="hidden md:flex items-center gap-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg transition text-sm"
        >
          📲 WhatsApp
        </a>
      </div>
    </header>
  );
};

export default Header;
