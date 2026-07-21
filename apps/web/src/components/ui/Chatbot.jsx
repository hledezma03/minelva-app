import React, { useState } from "react";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      text: "¡Hola! Soy el asistente virtual de Minelva Los Morros. ¿En qué puedo ayudarte?",
      sender: "bot",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Generar un ID de sesión único para cada visitante
  const [sessionId] = useState(() => {
    let id = localStorage.getItem("minelva_session_id");
    if (!id) {
      id =
        "session_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
      localStorage.setItem("minelva_session_id", id);
    }
    return id;
  });

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Función para registrar pedido en el backend
  const registrarPedido = async (
    nombre,
    direccion,
    telefono,
    producto,
    cantidad,
  ) => {
    console.log("Llamando a registrarPedido:", {
      nombre,
      direccion,
      telefono,
      producto,
      cantidad,
    });
    try {
      const bodyData = {
        session_id: sessionId,
        nombre: nombre,
        direccion: direccion,
        telefono: telefono,
        productos: producto,
        cantidad: cantidad,
      };

      // Si cantidad es 0, es un pedido múltiple, ajustamos para que el backend lo guarde
      if (cantidad === 0) {
        // Para pedidos múltiples, usamos cantidad = 1 como valor por defecto
        // y guardamos la descripción completa en el campo "productos"
        bodyData.cantidad = 1;
        // El backend ya tiene la descripción completa en "productos"
      }

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/pedido`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(bodyData),
        },
      );

      const data = await response.json();
      console.log("Respuesta del pedido:", data);

      if (data.pedido_id) {
        setMessages((prev) => [
          ...prev,
          {
            text: `✅ ${data.mensaje}`,
            sender: "bot",
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            text: `⚠️ ${data.mensaje}`,
            sender: "bot",
          },
        ]);
      }
    } catch (error) {
      console.error("Error registrando pedido:", error);
      setMessages((prev) => [
        ...prev,
        {
          text: "❌ Error al registrar tu pedido. Por favor, contacta por WhatsApp al 0412-0336537.",
          sender: "bot",
        },
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === "") return;

    const userMessage = { text: inputValue, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);

    const userText = inputValue;
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            texto: userText,
            session_id: sessionId,
            historial: messages
              .slice(-10)
              .map((msg) => ({ text: msg.text, sender: msg.sender })),
          }),
        },
      );

      const data = await response.json();
      let respuestaBot = data.respuesta;

      console.log("📨 Respuesta recibida:", respuestaBot);

      // Verificar si es un mensaje de confirmación de pedido
      // Aceptar tanto PEDIDO_CONFIRMADO| como PEDIDOCONFIRMADO|
      if (
        respuestaBot.includes("PEDIDO_CONFIRMADO|") ||
        respuestaBot.includes("PEDIDOCONFIRMADO|")
      ) {
        console.log("✅ Formato de confirmación detectado");

        // Normalizar: reemplazar PEDIDOCONFIRMADO por PEDIDO_CONFIRMADO
        let respuestaNormalizada = respuestaBot;
        if (respuestaBot.includes("PEDIDOCONFIRMADO|")) {
          respuestaNormalizada = respuestaBot.replace(
            "PEDIDOCONFIRMADO|",
            "PEDIDO_CONFIRMADO|",
          );
          console.log("📝 Formato normalizado:", respuestaNormalizada);
        }

        const partes = respuestaNormalizada.split("|");
        console.log("📊 Partes:", partes);
        console.log("📊 Número de partes:", partes.length);

        // El formato esperado es: PEDIDO_CONFIRMADO|nombre|direccion|telefono|productos
        if (partes.length >= 5) {
          const nombre = partes[1];
          const direccion = partes[2];
          const telefono = partes[3];
          const productosRaw = partes.slice(4).join("|");

          console.log("📝 Datos extraídos:", {
            nombre,
            direccion,
            telefono,
            productosRaw,
          });

          // Parsear productos
          const items = productosRaw.includes(";")
            ? productosRaw.split(";")
            : [productosRaw];

          console.log("📦 Items detectados:", items);

          let productosValidos = [];

          for (const item of items) {
            const partesItem = item.split(",");
            if (partesItem.length === 2) {
              const prod = partesItem[0].trim();
              const cant = parseInt(partesItem[1].trim());
              if (prod && !isNaN(cant) && cant > 0) {
                productosValidos.push({ nombre: prod, cantidad: cant });
              }
            }
          }

          if (productosValidos.length === 0) {
            console.log("⚠️ No se pudo parsear ningún producto");
            setMessages((prev) => [
              ...prev,
              {
                text: "❌ No pude entender los productos de tu pedido. Por favor, intenta nuevamente o contacta por WhatsApp.",
                sender: "bot",
              },
            ]);
            setIsLoading(false);
            return;
          }

          // === REGISTRAR EN EL BACKEND ===
          // NO mostramos mensaje de resumen aquí para evitar duplicidad
          // El backend ya enviará su propio mensaje de confirmación

          if (productosValidos.length === 1) {
            const p = productosValidos[0];
            console.log("📝 Registrando pedido simple:", p);
            await registrarPedido(
              nombre,
              direccion,
              telefono,
              p.nombre,
              p.cantidad,
            );
          } else {
            const descripcion = productosValidos
              .map((p) => `${p.cantidad} x ${p.nombre}`)
              .join(", ");
            console.log("📝 Registrando pedido múltiple:", descripcion);
            await registrarPedido(nombre, direccion, telefono, descripcion, 0);
          }
        } else {
          console.log("⚠️ Formato inesperado, no se puede procesar el pedido");
          setMessages((prev) => [
            ...prev,
            {
              text: "❌ Hubo un error procesando tu pedido. Por favor, contacta por WhatsApp al 0412-0336537.",
              sender: "bot",
            },
          ]);
        }
      } else {
        // Mostrar respuesta normal
        setMessages((prev) => [...prev, { text: respuestaBot, sender: "bot" }]);
      }
    } catch (error) {
      console.error("❌ Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          text: "❌ Error de conexión. Por favor, intenta más tarde o contacta por WhatsApp al 0412-0336537.",
          sender: "bot",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Botón flotante del chatbot */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 bg-[#0077B6] text-white p-4 rounded-full shadow-lg hover:bg-[#005f8f] transition z-50"
      >
        💬
      </button>

      {/* Ventana del chatbot */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-80 h-96 bg-white rounded-xl shadow-2xl flex flex-col z-50 border border-gray-200 overflow-hidden">
          {/* Cabecera */}
          <div className="bg-[#0077B6] text-white p-3 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span>💧</span>
              <span className="font-semibold">Asistente Minelva</span>
            </div>
            <button
              onClick={toggleChat}
              className="text-white hover:text-gray-200"
            >
              ✕
            </button>
          </div>

          {/* Área de mensajes */}
          <div className="flex-1 p-3 overflow-y-auto bg-gray-50">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`mb-3 flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] p-2 rounded-lg break-words whitespace-pre-wrap ${
                    msg.sender === "user"
                      ? "bg-[#0077B6] text-white rounded-br-none"
                      : "bg-gray-200 text-gray-800 rounded-bl-none"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 p-2 rounded-lg rounded-bl-none">
                  <div className="flex gap-1">
                    <span className="animate-bounce">●</span>
                    <span className="animate-bounce delay-100">●</span>
                    <span className="animate-bounce delay-200">●</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Campo de entrada */}
          <div className="border-t p-2 flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu mensaje..."
              className="flex-1 p-2 border rounded-lg focus:outline-none focus:border-[#0077B6]"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              className="bg-[#0077B6] text-white px-3 py-2 rounded-lg hover:bg-[#005f8f] transition"
              disabled={isLoading}
            >
              Enviar
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;
