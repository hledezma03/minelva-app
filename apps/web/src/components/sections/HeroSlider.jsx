import React from "react";
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, Pagination, Navigation, EffectFade } from "swiper/modules";

// Importar estilos de Swiper
import "swiper/css";
import "swiper/css/effect-fade";
import "swiper/css/pagination";
import "swiper/css/navigation";

// Importar tus flyers (ajusta las rutas según donde guardaste las imágenes)
import flyer1 from "../../assets/images/flyer1.png";
import flyer2 from "../../assets/images/flyer2.png";
import flyer3 from "../../assets/images/flyer3.png";
import flyer4 from "../../assets/images/flyer4.png";
import flyer5 from "../../assets/images/flyer5.png";

const slides = [
  {
    id: 1,
    image: flyer1,
    titulo: "PURA DE MANANTIAL",
    subtitulo: "Agua pura, libre de sodio",
    botonTexto: "Solicitar Delivery",
    botonLink: "https://wa.me/5804120336537",
  },
  {
    id: 2,
    image: flyer2,
    titulo: "RECARGA Y SANITIZACIÓN",
    subtitulo: "Limpieza profesional de botellones",
    botonTexto: "Conocer más",
    botonLink: "#servicios",
  },
  {
    id: 3,
    image: flyer3,
    titulo: "TU DOSIS DE FRESCURA",
    subtitulo: "Bienestar para tu hogar",
    botonTexto: "Ver productos",
    botonLink: "#productos",
  },
  {
    id: 4,
    image: flyer4,
    titulo: "INVERTÍ EN CALIDAD",
    subtitulo: "Solución para empresas",
    botonTexto: "Contactar",
    botonLink: "#contacto",
  },
  {
    id: 5,
    image: flyer5,
    titulo: "SIN RESIDUOS NI MAL OLOR",
    subtitulo: "Sanitización profesional",
    botonTexto: "Saber más",
    botonLink: "#servicios",
  },
];

const HeroSlider = () => {
  return (
    <section id="inicio" className="relative">
      <Swiper
        modules={[Autoplay, Pagination, Navigation, EffectFade]}
        effect="fade"
        spaceBetween={0}
        slidesPerView={1}
        autoplay={{
          delay: 5000,
          disableOnInteraction: false,
        }}
        pagination={{
          clickable: true,
          dynamicBullets: true,
        }}
        navigation={{
          nextEl: ".swiper-button-next-custom",
          prevEl: ".swiper-button-prev-custom",
        }}
        loop={true}
        className="h-screen w-full"
      >
        {slides.map((slide) => (
          <SwiperSlide key={slide.id}>
            <div
              className="relative w-full h-full bg-cover bg-center bg-no-repeat"
              style={{ backgroundImage: `url(${slide.image})` }}
            >
              {/* Overlay oscuro para mejorar legibilidad del texto */}
              <div className="absolute inset-0 bg-black bg-opacity-40"></div>

              {/* Contenido del slide */}
              <div className="relative z-10 flex flex-col items-center justify-center h-full text-white text-center px-4">
                <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 drop-shadow-lg">
                  {slide.titulo}
                </h2>
                <p className="text-lg md:text-xl lg:text-2xl mb-8 drop-shadow-md">
                  {slide.subtitulo}
                </p>
                <a
                  href={slide.botonLink}
                  target={
                    slide.botonLink.startsWith("http") ? "_blank" : "_self"
                  }
                  rel="noopener noreferrer"
                  className="bg-[#0077B6] hover:bg-[#005f8f] text-white px-8 py-3 rounded-lg font-semibold transition duration-300 shadow-lg hover:shadow-xl"
                >
                  {slide.botonTexto}
                </a>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Botones de navegación personalizados (opcional, Swiper ya tiene los suyos) */}
      <div className="swiper-button-prev-custom !hidden md:!flex !absolute !left-4 !top-1/2 !-translate-y-1/2 !z-20 !w-10 !h-10 !bg-white/80 !rounded-full !items-center !justify-center !cursor-pointer hover:!bg-white transition">
        ❮
      </div>
      <div className="swiper-button-next-custom !hidden md:!flex !absolute !right-4 !top-1/2 !-translate-y-1/2 !z-20 !w-10 !h-10 !bg-white/80 !rounded-full !items-center !justify-center !cursor-pointer hover:!bg-white transition">
        ❯
      </div>
    </section>
  );
};

export default HeroSlider;
