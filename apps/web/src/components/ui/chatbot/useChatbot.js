import { useState } from "react";
import { enviarMensaje } from "../../../services/api/chatService";
import { registrarPedido as registrarPedidoApi } from "../../../services/api/pedidoService";

const MENSAJE_BIENVENIDA =
  "¡Hola! Soy el asistente virtual de Minelva Los Morros. ¿En qué puedo ayudarte?";

const MENSAJE_ERROR_PEDIDO =
  "❌ Error al registrar tu pedido. Por favor, contacta por WhatsApp al 0412-0336537.";

const MENSAJE_ERROR_PRODUCTOS_INVALIDOS =
  "❌ No pude entender los productos de tu pedido. Por favor, intenta nuevamente o contacta por WhatsApp.";

const MENSAJE_ERROR_FORMATO_PEDIDO =
  "❌ Hubo un error procesando tu pedido. Por favor, contacta por WhatsApp al 0412-0336537.";

const MENSAJE_ERROR_CONEXION =
  "❌ Error de conexión. Por favor, intenta más tarde o contacta por WhatsApp al 0412-0336537.";

// Genera (o reutiliza) un ID de sesión único por visitante, guardado en localStorage.
function obtenerOCrearSessionId() {
  let id = localStorage.getItem("minelva_session_id");
  if (!id) {
    id = "session_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("minelva_session_id", id);
  }
  return id;
}

// Parsea el bloque "PEDIDO_CONFIRMADO|nombre|direccion|telefono|productos"
// que devuelve la IA y lo convierte en una lista de { nombre, cantidad }.
function parsearProductos(productosRaw) {
  const items = productosRaw.includes(";") ? productosRaw.split(";") : [productosRaw];

  const productosValidos = [];
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
  return productosValidos;
}

export function useChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{ text: MENSAJE_BIENVENIDA, sender: "bot" }]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(obtenerOCrearSessionId);

  const agregarMensajeBot = (text) => {
    setMessages((prev) => [...prev, { text, sender: "bot" }]);
  };

  const toggleChat = () => setIsOpen((prev) => !prev);

  // Registra el pedido ya parseado en el backend y muestra la respuesta.
  const registrarPedido = async (nombre, direccion, telefono, producto, cantidad) => {
    console.log("Llamando a registrarPedido:", { nombre, direccion, telefono, producto, cantidad });
    try {
      const bodyData = {
        session_id: sessionId,
        nombre,
        direccion,
        telefono,
        productos: producto,
        cantidad,
      };

      // Si cantidad es 0, es un pedido múltiple, ajustamos para que el backend lo guarde
      if (cantidad === 0) {
        // Para pedidos múltiples, usamos cantidad = 1 como valor por defecto
        // y guardamos la descripción completa en el campo "productos"
        bodyData.cantidad = 1;
      }

      const data = await registrarPedidoApi(bodyData);
      console.log("Respuesta del pedido:", data);

      if (data.pedido_id) {
        agregarMensajeBot(`✅ ${data.mensaje}`);
      } else {
        agregarMensajeBot(`⚠️ ${data.mensaje}`);
      }
    } catch (error) {
      console.error("Error registrando pedido:", error);
      agregarMensajeBot(MENSAJE_ERROR_PEDIDO);
    }
  };

  // Detecta y procesa el formato PEDIDO_CONFIRMADO| / PEDIDOCONFIRMADO| dentro
  // de la respuesta del bot, y dispara el registro del pedido si corresponde.
  const procesarPosibleConfirmacionPedido = async (respuestaBot) => {
    console.log("✅ Formato de confirmación detectado");

    let respuestaNormalizada = respuestaBot;
    if (respuestaBot.includes("PEDIDOCONFIRMADO|")) {
      respuestaNormalizada = respuestaBot.replace("PEDIDOCONFIRMADO|", "PEDIDO_CONFIRMADO|");
      console.log("📝 Formato normalizado:", respuestaNormalizada);
    }

    const partes = respuestaNormalizada.split("|");
    console.log("📊 Partes:", partes);
    console.log("📊 Número de partes:", partes.length);

    // El formato esperado es: PEDIDO_CONFIRMADO|nombre|direccion|telefono|productos
    if (partes.length < 5) {
      console.log("⚠️ Formato inesperado, no se puede procesar el pedido");
      agregarMensajeBot(MENSAJE_ERROR_FORMATO_PEDIDO);
      return;
    }

    const nombre = partes[1];
    const direccion = partes[2];
    const telefono = partes[3];
    const productosRaw = partes.slice(4).join("|");

    console.log("📝 Datos extraídos:", { nombre, direccion, telefono, productosRaw });

    const items = productosRaw.includes(";") ? productosRaw.split(";") : [productosRaw];
    console.log("📦 Items detectados:", items);

    const productosValidos = parsearProductos(productosRaw);

    if (productosValidos.length === 0) {
      console.log("⚠️ No se pudo parsear ningún producto");
      agregarMensajeBot(MENSAJE_ERROR_PRODUCTOS_INVALIDOS);
      return;
    }

    // === REGISTRAR EN EL BACKEND ===
    // NO mostramos mensaje de resumen aquí para evitar duplicidad
    // El backend ya enviará su propio mensaje de confirmación
    if (productosValidos.length === 1) {
      const p = productosValidos[0];
      console.log("📝 Registrando pedido simple:", p);
      await registrarPedido(nombre, direccion, telefono, p.nombre, p.cantidad);
    } else {
      const descripcion = productosValidos.map((p) => `${p.cantidad} x ${p.nombre}`).join(", ");
      console.log("📝 Registrando pedido múltiple:", descripcion);
      await registrarPedido(nombre, direccion, telefono, descripcion, 0);
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
      const historial = messages.slice(-10).map((msg) => ({ text: msg.text, sender: msg.sender }));
      const data = await enviarMensaje(userText, sessionId, historial);
      const respuestaBot = data.respuesta;

      console.log("📨 Respuesta recibida:", respuestaBot);

      // Verificar si es un mensaje de confirmación de pedido
      // Aceptar tanto PEDIDO_CONFIRMADO| como PEDIDOCONFIRMADO|
      if (respuestaBot.includes("PEDIDO_CONFIRMADO|") || respuestaBot.includes("PEDIDOCONFIRMADO|")) {
        await procesarPosibleConfirmacionPedido(respuestaBot);
      } else {
        agregarMensajeBot(respuestaBot);
      }
    } catch (error) {
      console.error("❌ Error:", error);
      agregarMensajeBot(MENSAJE_ERROR_CONEXION);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return {
    isOpen,
    toggleChat,
    messages,
    inputValue,
    setInputValue,
    isLoading,
    handleSendMessage,
    handleKeyPress,
  };
}
