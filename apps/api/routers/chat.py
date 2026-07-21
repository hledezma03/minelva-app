"""Endpoint /chat."""
from fastapi import APIRouter

from models.schemas import Mensaje
from utils.texto import solo_texto
from services.ia_service import _response_cache, get_cache_key, guardar_en_cache, procesar_con_ia
from services.log_service import log_en_segundo_plano

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(mensaje: Mensaje):
    texto = solo_texto(mensaje.texto)
    if not texto:
        return {"respuesta": "Por favor, escribe un mensaje válido."}

    cache_key = get_cache_key(texto)
    if cache_key in _response_cache:
        respuesta = _response_cache[cache_key]
        log_en_segundo_plano(mensaje.session_id, texto, respuesta, uso_ia=False)
        return {"respuesta": respuesta}

    respuesta = await procesar_con_ia(texto, mensaje.historial)
    guardar_en_cache(cache_key, respuesta)
    log_en_segundo_plano(mensaje.session_id, texto, respuesta, uso_ia=True)
    return {"respuesta": respuesta}
