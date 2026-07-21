"""Endpoints públicos: / y /health."""
from datetime import datetime
from fastapi import APIRouter

from clients import clients
from utils.async_helpers import ejecutar_en_hilo

router = APIRouter()


@router.get("/")
async def root():
    return {"mensaje": "API del Chatbot Minelva funcionando", "status": "online", "version": "6.0.0"}


def _ping_supabase_sync():
    """Consulta mínima y barata: solo cuenta filas, no trae datos."""
    return clients.supabase.table("logs_conversacion").select("id_log", count="exact").limit(1).execute()


@router.get("/health")
async def health_check():
    """
    Endpoint de diagnóstico rápido. Úsalo para comprobar en vivo (o con un
    ping automático) que Supabase y Groq están activos y respondiendo.
    Ejemplo: https://tu-backend.onrender.com/health
    """
    estado = {
        "api": "ok",
        "groq": "no_configurado",
        "supabase": "no_configurado",
    }

    if clients.groq is not None:
        estado["groq"] = "ok"

    if clients.supabase is not None:
        inicio = datetime.now()
        try:
            await ejecutar_en_hilo(_ping_supabase_sync)
            ms = (datetime.now() - inicio).total_seconds() * 1000
            estado["supabase"] = f"ok ({ms:.0f}ms)"
        except Exception as e:
            estado["supabase"] = f"error: {e}"

    return estado
