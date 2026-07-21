"""Procesamiento de mensajes con IA (Groq), caché de respuestas y
respaldo sin IA cuando Groq no está disponible."""
import hashlib
from typing import List, Dict

from config import config
from clients import clients
from utils.texto import limpiar_markdown
from services.negocio_service import (
    construir_contexto_negocio,
    RESPUESTAS_FALLBACK,
    PALABRAS_CLAVE_FALLBACK,
)

_response_cache: Dict[str, str] = {}


def get_cache_key(texto: str) -> str:
    normalizado = " ".join(texto.lower().split())
    return hashlib.md5(normalizado.encode()).hexdigest()


def guardar_en_cache(clave: str, valor: str):
    _response_cache[clave] = valor
    if len(_response_cache) > config.CACHE_MAX_SIZE:
        del _response_cache[next(iter(_response_cache))]


async def respuesta_fallback(mensaje: str) -> str:
    texto = mensaje.lower()
    for palabras, clave in PALABRAS_CLAVE_FALLBACK:
        if any(p in texto for p in palabras):
            return RESPUESTAS_FALLBACK[clave]
    return "Para más información, contáctanos por WhatsApp al 0412-0336537."


async def procesar_con_ia(mensaje: str, historial: List[Dict]) -> str:
    if clients.groq is None:
        return await respuesta_fallback(mensaje)

    contexto_negocio = await construir_contexto_negocio()

    historial_texto = "\n".join(
        f"{'Usuario' if msg.get('sender') == 'user' else 'Asistente'}: {msg.get('text', '')}"
        for msg in (historial or [])[-10:]
    )
    prompt = f"{contexto_negocio}\n\nHistorial:\n{historial_texto}\n\nUsuario: {mensaje}\n\nAsistente:"

    try:
        completion = await clients.groq.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": contexto_negocio},
                {"role": "user", "content": prompt},
            ],
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        respuesta = completion.choices[0].message.content
        return limpiar_markdown(respuesta) if respuesta else await respuesta_fallback(mensaje)
    except Exception as e:
        print(f"❌ Error en Groq: {e}")
        return await respuesta_fallback(mensaje)
