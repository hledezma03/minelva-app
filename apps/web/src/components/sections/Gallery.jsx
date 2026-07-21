import React, { useState } from "react";
import FadeInSection from "../ui/FadeInSection";

// Importar los flyers (ajusta los nombres según tus archivos)
import flyer1 from "../../assets/images/flyer1.png";
import flyer2 from "../../assets/images/flyer2.png";
import flyer3 from "../../assets/images/flyer3.png";
import flyer4 from "../../assets/images/flyer4.png";
import flyer5 from "../../assets/images/flyer5.png";
import flyer6 from "../../assets/images/flyer6.png";

const flyers = [
  {
    id: 1,
    img: flyer1,
    titulo: "Pura de Manantial",
    descripcion: "Agua pura, libre de sodio",
  },
  {
    id: 2,
    img: flyer2,
    titulo: "Recarga y Sanitización",
    descripcion: "Limpieza de botellones",
  },
  {
    id: 3,
    img: flyer3,
    titulo: "Tu dosis de frescura",
    descripcion: "Bienestar para tu hogar",
  },
  {
    id: 4,
    img: flyer4,
    titulo: "Invvierte en calidad",
    descripcion: "Solución para empresas",
  },
  {
    id: 5,
    img: flyer5,
    titulo: "Sin residuos ni mal olor",
    descripcion: "Sanitización profesional",
  },
  {
    id: 6,
    img: flyer6,
    titulo: "Botellones hasta la puerta de tu casa",
    descripcion: "Servicio a domicilio activo",
  },
];

const Gallery = () => {
  const [selected, setSelected] = useState(null);

  return (
    <section id="galeria" className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <FadeInSection>
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4 text-[#1A2A3A]">
            Productos
          </h2>
          <p className="text-center text-gray-600 mb-12 text-lg">
            Conoce más sobre Minelva Los Morros
          </p>
        </FadeInSection>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {flyers.map((flyer, index) => (
            <FadeInSection key={flyer.id} delay={index * 100}>
              <div
                className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-2 cursor-pointer group"
                onClick={() => setSelected(flyer)}
              >
                <div className="h-56 overflow-hidden">
                  <img
                    src={flyer.img}
                    alt={flyer.titulo}
                    className="w-full h-full object-cover group-hover:scale-110 transition duration-500"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-[#0077B6] text-lg">
                    {flyer.titulo}
                  </h3>
                  <p className="text-gray-600 text-sm">{flyer.descripcion}</p>
                </div>
              </div>
            </FadeInSection>
          ))}
        </div>

        {/* Modal para ver imagen ampliada */}
        {selected && (
          <div
            className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4"
            onClick={() => setSelected(null)}
          >
            <div
              className="bg-white rounded-xl max-w-2xl w-full overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={selected.img}
                alt={selected.titulo}
                className="w-full h-auto"
              />
              <div className="p-4 text-center">
                <h3 className="text-xl font-bold text-[#0077B6]">
                  {selected.titulo}
                </h3>
                <p className="text-gray-600">{selected.descripcion}</p>
                <button
                  className="mt-4 bg-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                  onClick={() => setSelected(null)}
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Gallery;
