import { postJSON } from "./httpClient";

// Registra un pedido en el backend (endpoint /pedido).
// Devuelve el JSON tal cual lo manda el backend: { mensaje, pedido_id }
export async function registrarPedido(bodyData) {
  return postJSON("/pedido", bodyData);
}
