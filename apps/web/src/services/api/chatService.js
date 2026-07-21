import { postJSON } from "./httpClient";

// Envía el mensaje del usuario al endpoint /chat del backend.
// Devuelve el JSON tal cual lo manda el backend: { respuesta: "..." }
export async function enviarMensaje(texto, sessionId, historial) {
  return postJSON("/chat", {
    texto,
    session_id: sessionId,
    historial,
  });
}
