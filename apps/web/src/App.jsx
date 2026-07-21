import React from "react";
import Header from "./components/layout/Header";
import HeroSlider from "./components/sections/HeroSlider"; // ← Cambio importante
import Services from "./components/sections/Services";
import Gallery from "./components/sections/Gallery";
import Contact from "./components/sections/Contact";
import Footer from "./components/layout/Footer";
import Chatbot from "./components/ui/Chatbot";

function App() {
  return (
    <div>
      <Header />
      <HeroSlider /> {/* ← Ahora es el carrusel */}
      <Services />
      <Gallery />
      <Contact />
      <Footer />
      <Chatbot />
    </div>
  );
}

export default App;
