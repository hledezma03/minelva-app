"""Ayudantes para ejecutar código bloqueante (Supabase/Twilio) sin bloquear
el event loop de FastAPI, y para lanzar tareas en segundo plano."""
import asyncio
from typing import Callable, Any


async def ejecutar_en_hilo(fn: Callable, *args, tiempo_limite: float = 12.0, **kwargs) -> Any:
    """Corre una función SÍNCRONA (Supabase/Twilio) en un hilo aparte para
    no bloquear el event loop de FastAPI mientras se espera la red.

    Además aplica un límite de tiempo propio (independiente de la librería):
    si la operación no responde en `tiempo_limite` segundos, se cancela y
    se lanza TimeoutError, para que el servidor NUNCA se quede colgado
    esperando indefinidamente una respuesta que quizás nunca llegue.
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(fn, *args, **kwargs), timeout=tiempo_limite)
    except asyncio.TimeoutError:
        raise TimeoutError(f"La operación superó el límite de {tiempo_limite}s (posible problema de red)")


_tareas_segundo_plano: set = set()


def lanzar_en_segundo_plano(coro):
    """Crea una tarea en segundo plano SIN bloquear al usuario, pero
    guardando una referencia fuerte para que sí llegue a completarse."""
    tarea = asyncio.create_task(coro)
    _tareas_segundo_plano.add(tarea)
    tarea.add_done_callback(_tareas_segundo_plano.discard)
    return tarea
