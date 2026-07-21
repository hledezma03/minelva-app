"""Registro de pedidos en Supabase + disparo de notificación WhatsApp."""
from datetime import datetime
from typing import Optional

from clients import clients
from utils.async_helpers import ejecutar_en_hilo, lanzar_en_segundo_plano
from utils.texto import solo_texto
from models.schemas import Pedido
from services.whatsapp_service import enviar_notificacion_whatsapp


def _insertar_pedido_sync(data: dict):
    return clients.supabase.table("pedidos").insert(data).execute()


async def registrar_pedido_en_db(pedido: Pedido) -> tuple[Optional[str], str]:
    """Registra un pedido en Supabase y dispara la notificación de WhatsApp."""
    if clients.supabase is None:
        print("❌ Supabase no está conectado")
        return None, "📞 Error técnico. Contacta por WhatsApp."

    if not all([pedido.nombre, pedido.direccion, pedido.telefono]):
        print("❌ Faltan datos obligatorios")
        return None, "⚠️ Faltan datos: nombre, dirección y teléfono."

    data = {
        "session_id": pedido.session_id,
        "nombre_cliente": solo_texto(pedido.nombre),
        "direccion_entrega": solo_texto(pedido.direccion),
        "telefono_contacto": solo_texto(pedido.telefono),
        "productos": [{"nombre": pedido.productos, "cantidad": pedido.cantidad}],
        "cantidad_total": pedido.cantidad,
        "estado": "pendiente",
        "fecha_creacion": datetime.now().isoformat(),
    }

    print(f"📝 Registrando pedido de {pedido.nombre} ({pedido.cantidad} x {pedido.productos})")

    try:
        result = await ejecutar_en_hilo(_insertar_pedido_sync, data)

        if not result.data:
            return None, "✅ Pedido recibido. Pronto nos contactaremos."

        fila = result.data[0]
        pedido_id = fila.get("id_pedido") or fila.get("id")

        # No crítico: se dispara en segundo plano, no bloquea la respuesta.
        # Usamos lanzar_en_segundo_plano (no asyncio.create_task directo)
        # para que la tarea SÍ llegue a completarse (ver comentario junto
        # a la definición de lanzar_en_segundo_plano).
        lanzar_en_segundo_plano(ejecutar_en_hilo(enviar_notificacion_whatsapp, data))

        mensaje_confirmacion = (
            f"✅ ¡Pedido registrado {pedido.nombre}! ✅\n\n"
            f"📋 Resumen:\n"
            f"• {pedido.cantidad} x {pedido.productos}\n"
            f"• Dirección: {pedido.direccion}\n\n"
            f"📞 Pronto te contactaremos."
        )
        return pedido_id, mensaje_confirmacion

    except Exception as e:
        print(f"❌ Error registrando pedido: {e}")
        # Causa más común: proyecto de Supabase pausado por inactividad
        # (plan free se pausa tras 7 días sin actividad) -> ConnectTimeout.
        return None, "❌ Error al registrar. Contacta por WhatsApp."
