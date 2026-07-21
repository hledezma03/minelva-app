import React from "react";
import { servicios } from "../../data";
import FadeInSection from "../ui/FadeInSection";

const Services = () => {
  return (
    <section id="servicios" className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">
          Nuestros Servicios
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {servicios.map((s, i) => (
            <FadeInSection key={s.id} delay={i * 100}>
              <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition">
                <div className="text-5xl mb-4">{s.icono}</div>
                <h3 className="text-xl font-bold text-[#0077B6] mb-2">
                  {s.titulo}
                </h3>
                <p className="text-gray-600">{s.descripcion}</p>
              </div>
            </FadeInSection>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
