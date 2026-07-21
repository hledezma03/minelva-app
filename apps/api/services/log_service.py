"""Registro de logs de conversación en Supabase, en segundo plano."""
from datetime import datetime

from clients import clients
from utils.async_helpers import ejecutar_en_hilo, lanzar_en_segundo_plano


def _insertar_log_sync(session_id: str, mensaje: str, respuesta: str, uso_ia: bool):
    clients.supabase.table("logs_conversacion").insert({
        "session_id": session_id,
        "mensaje_usuario": mensaje,
        "respuesta_bot": respuesta,
        "uso_ia": uso_ia,
        "timestamp": datetime.now().isoformat(),
    }).execute()


async def guardar_log(session_id: str, mensaje: str, respuesta: str, uso_ia: bool = True):
    if clients.supabase is None:
        print("⚠️ Supabase no disponible - log no guardado")
        return
    try:
        await ejecutar_en_hilo(_insertar_log_sync, session_id, mensaje, respuesta, uso_ia)
    except Exception as e:
        print(f"⚠️ Error guardando log: {e}")


def log_en_segundo_plano(session_id: str, mensaje: str, respuesta: str, uso_ia: bool):
    """Dispara el guardado del log sin bloquear la respuesta al usuario."""
    lanzar_en_segundo_plano(guardar_log(session_id, mensaje, respuesta, uso_ia))
