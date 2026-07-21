// Cliente HTTP único: centraliza la URL base y la forma de hacer POST en JSON.
// Antes, cada componente leía import.meta.env.VITE_API_URL y armaba el
// fetch por su cuenta; ahora todos usan esta misma función.

const API_URL = import.meta.env.VITE_API_URL;

export async function postJSON(endpoint, body) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  return response.json();
}
