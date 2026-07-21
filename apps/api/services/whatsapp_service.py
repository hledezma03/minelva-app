"""Notificaciones por WhatsApp (Twilio)."""
from config import config

# Twilio es opcional: si el paquete no está instalado, la app debe seguir
# funcionando (solo se deshabilitan las notificaciones de WhatsApp).
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_LIB_DISPONIBLE = True
except ImportError as e:
    TwilioClient = None
    TWILIO_LIB_DISPONIBLE = False
    print(f"⚠️ Librería 'twilio' no disponible ({e}). Notificaciones WhatsApp deshabilitadas.")


def _con_prefijo_whatsapp(numero: str) -> str:
    return numero if numero.startswith("whatsapp:") else f"whatsapp:{numero}"


def enviar_notificacion_whatsapp(pedido_data: dict) -> bool:
    """Envía notificación por WhatsApp si Twilio está disponible y configurado."""
    if not TWILIO_LIB_DISPONIBLE:
        print("ℹ️ Librería twilio no instalada - omitiendo notificación")
        return True

    if not all([config.TWILIO_SID, config.TWILIO_TOKEN, config.TWILIO_FROM, config.TWILIO_TO]):
        print("ℹ️ Twilio no configurado - omitiendo notificación")
        return True

    try:
        productos = pedido_data.get("productos", [])
        if isinstance(productos, list):
            productos_texto = "".join(
                f"• {p.get('cantidad', 1)} x {p.get('nombre', 'Producto')}\n" for p in productos
            )
        else:
            productos_texto = str(productos)

        mensaje = f"""
🔔 *NUEVO PEDIDO - Minelva Los Morros* 🔔

👤 *Cliente:* {pedido_data.get('nombre_cliente', 'N/A')}
📍 *Dirección:* {pedido_data.get('direccion_entrega', 'N/A')}
📞 *Teléfono:* {pedido_data.get('telefono_contacto', 'N/A')}

📦 *Productos:*
{productos_texto}
💳 *Estado:* Pendiente de pago

🌐 *Ver en panel:*
https://minelva-app.onrender.com/admin/login
"""
        client = TwilioClient(config.TWILIO_SID, config.TWILIO_TOKEN)
        message = client.messages.create(
            from_=_con_prefijo_whatsapp(config.TWILIO_FROM),
            body=mensaje,
            to=_con_prefijo_whatsapp(config.TWILIO_TO),
        )
        print(f"✅ Notificación WhatsApp enviada: {message.sid}")
        return True
    except Exception as e:
        print(f"⚠️ Error en notificación WhatsApp (no crítico): {e}")
        return False
