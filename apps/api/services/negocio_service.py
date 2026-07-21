"""Contexto del negocio: precios, plantilla de prompt, y estado
abierto/cerrado, con caché en memoria para no golpear Supabase en cada
mensaje del chat."""
from datetime import datetime, timedelta
from typing import Dict, Any

from clients import clients
from utils.async_helpers import ejecutar_en_hilo

PRECIOS = {
    "recarga": 1.00,
    "delivery": 1.00,
    "botellon_20l_normal": 10.00,
    "botellon_20l_rosca": 11.00,
    "botellon_12l": 9.50,
    "botellon_asa_rosca": 11.50,
    "dispensador_manual": 9.00,
    "hielo": 2.00,
}

PLANTILLA_CONTEXTO = """
Eres un asistente virtual de Minelva Los Morros.
{aviso_cierre}
INFORMACIÓN:
- Dirección: Av. Los Llanos, Edif. Solitario, diagonal a los Tribunales
- Teléfono: 0412-0336537
- Instagram: @aguaminelva
- Horarios: Lunes a Sábado 7am-6:30pm, Domingo 7am-2:30pm

PRECIOS (tasa BCV):
{lista_precios}

REGLAS ESTRICTAS PARA PEDIDOS:

1. Recolecta en orden: nombre, dirección, teléfono.

2. Cuando el usuario indique qué productos quiere, puedes recibir UNO o VARIOS productos en el mismo mensaje.

3. Al confirmar el pedido, DEBES generar EXACTAMENTE este formato (es CRÍTICO que sea idéntico):
   PEDIDO_CONFIRMADO|nombre|direccion|telefono|producto1,cantidad1;producto2,cantidad2

   ¡ATENCIÓN! Debe ser PEDIDO_CONFIRMADO (con GUION BAJO entre PEDIDO y CONFIRMADO). NO uses PEDIDOCONFIRMADO.

4. Si el usuario pide un solo producto, el formato es:
   PEDIDO_CONFIRMADO|nombre|direccion|telefono|producto,cantidad

5. REGLAS DEL FORMATO:
   - El nombre del producto debe ser el nombre CORTO (ej: "recarga", "botellon_20l_rosca", "hielo")
   - La cantidad debe ser SOLO el número
   - Los múltiples productos se separan con punto y coma (;)
   - Producto y cantidad se separan con coma (,)
   - NO uses espacios dentro del formato
   - NO uses la palabra "y" para separar productos

EJEMPLOS CORRECTOS:
- Un producto: PEDIDO_CONFIRMADO|Manuel|Calle 1|04121234567|recarga,4
- Múltiples: PEDIDO_CONFIRMADO|Manuel|Calle 1|04121234567|botellon_20l_rosca,2;botellon_20l_normal,1

6. Si el negocio está cerrado (ver aviso arriba), informa esto al cliente ANTES de tomar cualquier pedido nuevo, y NO generes PEDIDO_CONFIRMADO.

Responde en español, breve, sin formato Markdown.
"""

RESPUESTAS_FALLBACK = {
    "saludo": "¡Hola! Bienvenido a Minelva Los Morros. ¿En qué puedo ayudarte?",
    "precios": f"💰 Precios (tasa BCV): Recarga ${PRECIOS['recarga']:.2f}, Botellón 20L ${PRECIOS['botellon_20l_normal']:.2f}, Hielo ${PRECIOS['hielo']:.2f}, Delivery ${PRECIOS['delivery']:.2f}",
    "horario": "Horario: Lunes a Sábado 7am-6:30pm, Domingo 7am-2:30pm",
    "servicios": "Ofrecemos: recarga, venta de botellones, sanitización, delivery y hielo",
    "pedido": "📝 Para hacer un pedido, necesito: nombre, dirección, teléfono, producto y cantidad. ¿Me das tu nombre?",
    "ubicacion": "Estamos en Av. Los Llanos, Edif. Solitario, diagonal a los Tribunales",
    "gracias": "¡Gracias a ti! ¿Necesitas algo más?",
    "despedida": "¡Hasta luego! Que tengas un excelente día.",
}

# Palabras clave -> clave de respuesta en RESPUESTAS_FALLBACK
PALABRAS_CLAVE_FALLBACK = [
    (["hola", "buenas", "saludos"], "saludo"),
    (["precio", "cuesta", "cuánto", "costo", "valor"], "precios"),
    (["horario", "atencion", "abren"], "horario"),
    (["servicio", "ofrecen"], "servicios"),
    (["pedido", "domicilio", "delivery", "comprar"], "pedido"),
    (["direccion", "ubicacion", "donde"], "ubicacion"),
    (["gracias"], "gracias"),
    (["adios", "chao", "hasta luego"], "despedida"),
]

CACHE_CONTEXTO_SEGUNDOS = 120

_cache_contexto: Dict[str, Any] = {"texto": None, "expira": None}


def invalidar_cache_negocio():
    """Fuerza a que el próximo mensaje del chat recargue productos/estado desde Supabase."""
    _cache_contexto["texto"] = None
    _cache_contexto["expira"] = None


def _obtener_productos_sync():
    return (
        clients.supabase.table("productos")
        .select("*")
        .eq("disponible", True)
        .order("orden")
        .execute()
    )


def _obtener_estado_negocio_sync():
    return clients.supabase.table("estado_negocio").select("*").limit(1).execute()


async def construir_contexto_negocio() -> str:
    """Arma el prompt de sistema con los precios y el estado actuales.
    Usa caché en memoria; si Supabase falla o la tabla está vacía, cae
    en los PRECIOS fijos como respaldo para que el chatbot nunca se quede
    sin poder responder."""
    ahora = datetime.now()
    if _cache_contexto["texto"] and _cache_contexto["expira"] and ahora < _cache_contexto["expira"]:
        return _cache_contexto["texto"]

    lista_precios = ""
    aviso_cierre = ""

    if clients.supabase is not None:
        try:
            result = await ejecutar_en_hilo(_obtener_productos_sync)
            lista_precios = "\n".join(
                f"- {p['nombre']}: ${float(p['precio']):.2f}" for p in (result.data or [])
            )
        except Exception as e:
            print(f"⚠️ Error obteniendo productos de Supabase: {e}")

        try:
            result_estado = await ejecutar_en_hilo(_obtener_estado_negocio_sync)
            fila = (result_estado.data or [None])[0]
            if fila and not fila.get("abierto", True):
                mensaje_cierre = fila.get("mensaje") or "Hoy no estamos atendiendo pedidos."
                aviso_cierre = (
                    f"\nAVISO IMPORTANTE: El negocio está CERRADO en este momento. "
                    f"Motivo/mensaje para el cliente: \"{mensaje_cierre}\". "
                    f"Debes informar esto al cliente ANTES de tomar cualquier pedido nuevo.\n"
                )
        except Exception as e:
            print(f"⚠️ Error obteniendo estado del negocio: {e}")

    if not lista_precios:
        # Respaldo: si la tabla no existe todavía, está vacía, o Supabase falló
        lista_precios = "\n".join(f"- {nombre}: ${precio:.2f}" for nombre, precio in PRECIOS.items())

    texto = PLANTILLA_CONTEXTO.format(aviso_cierre=aviso_cierre, lista_precios=lista_precios)

    _cache_contexto["texto"] = texto
    _cache_contexto["expira"] = ahora + timedelta(seconds=CACHE_CONTEXTO_SEGUNDOS)
    return texto
