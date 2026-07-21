import React from "react";
import { empresa, horarios } from "../../data";

const Contact = () => {
  return (
    <section id="contacto" className="py-16">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Contáctanos</h2>
        <div className="max-w-lg mx-auto bg-gray-50 rounded-xl p-6 text-center space-y-4">
          <p className="text-2xl font-bold text-[#0077B6]">
            📞 {empresa.telefono}
          </p>
          <p>📍 {empresa.direccion}</p>
          <p>
            ⏰ Lunes a Sábado: {horarios.lunesSabado}
            <br />
            Domingo: {horarios.domingo}
          </p>
          <p>
            📷{" "}
            <a
              href="https://instagram.com/aguaminelva"
              className="text-[#0077B6]"
            >
              {empresa.instagram}
            </a>
          </p>
          <a
            href={`https://wa.me/58${empresa.telefono}`}
            target="_blank"
            className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            📲 WhatsApp
          </a>
        </div>
        <p className="text-center mt-8 text-gray-500 italic">
          "{empresa.lema}"
        </p>
      </div>
    </section>
  );
};

export default Contact;
