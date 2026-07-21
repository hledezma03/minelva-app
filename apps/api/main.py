"""
API del Chatbot Minelva Los Morros
Versión 6.0 - Refactorizada: async no bloqueante + código sin repetición
"""

import os
import re
import hashlib
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Callable, Any

from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from groq import AsyncGroq
from supabase import create_client, Client

# Twilio es opcional: si el paquete no está instalado, la app debe seguir
# funcionando (solo se deshabilitan las notificaciones de WhatsApp).
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_LIB_DISPONIBLE = True
except ImportError as e:
    TwilioClient = None
    TWILIO_LIB_DISPONIBLE = False
    print(f"⚠️ Librería 'twilio' no disponible ({e}). Notificaciones WhatsApp deshabilitadas.")

load_dotenv()


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS: str = os.getenv("ADMIN_PASS", "minelva2026")
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

    TWILIO_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    TWILIO_TO: str = os.getenv("ADMIN_WHATSAPP_NUMBER", "")

    CACHE_MAX_SIZE: int = 100
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MAX_TOKENS: int = 350
    TEMPERATURE: float = 0.7

    ESTADOS_VALIDOS = ["pendiente", "pagado", "entregado", "cancelado"]


config = Config()

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


# ============================================================
# 2. CLIENTES EXTERNOS (Groq, Supabase)
# ============================================================

class Clients:
    groq: Optional[AsyncGroq] = None
    supabase: Optional[Client] = None


clients = Clients()


def init_clients():
    """Inicializa las conexiones a servicios externos con logs de depuración."""
    print("=" * 50)
    print("🔍 VERIFICANDO VARIABLES DE ENTORNO:")
    print(f"   GROQ_API_KEY: {'✅ OK' if config.GROQ_API_KEY else '❌ NO ENCONTRADA'}")
    print(f"   SUPABASE_URL: {config.SUPABASE_URL[:30] + '...' if config.SUPABASE_URL else '❌ NO ENCONTRADA'}")
    print(f"   SUPABASE_KEY: {'✅ OK' if config.SUPABASE_KEY else '❌ NO ENCONTRADA'}")
    print(f"   TWILIO_ACCOUNT_SID: {'✅ OK' if config.TWILIO_SID else '❌ NO ENCONTRADA'}")
    print(f"   Librería twilio instalada: {'✅ SI' if TWILIO_LIB_DISPONIBLE else '❌ NO'}")
    print("=" * 50)

    if config.GROQ_API_KEY.startswith("gsk_"):
        try:
            clients.groq = AsyncGroq(api_key=config.GROQ_API_KEY)
            print("✅ Groq configurado correctamente (modo async)")
        except Exception as e:
            print(f"⚠️ Error configurando Groq: {e}")
    else:
        print("⚠️ GROQ_API_KEY no encontrada o inválida")

    if config.SUPABASE_URL and config.SUPABASE_KEY:
        try:
            clients.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            print("✅ Supabase conectado correctamente")
        except Exception as e:
            print(f"⚠️ Error conectando a Supabase: {e}")
    else:
        print("⚠️ SUPABASE_URL o SUPABASE_KEY no encontradas")


# ============================================================
# 3. MODELOS DE DATOS
# ============================================================

class Mensaje(BaseModel):
    texto: str
    session_id: str
    historial: List[Dict[str, str]] = []


class Pedido(BaseModel):
    session_id: str
    nombre: str
    direccion: str
    telefono: str
    productos: str
    cantidad: int


class RespuestaPedido(BaseModel):
    mensaje: str
    pedido_id: Optional[str] = None


class ProductoInput(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""
    precio: float
    categoria: Optional[str] = "general"
    disponible: bool = True
    orden: Optional[int] = 0


class EstadoNegocioInput(BaseModel):
    abierto: bool
    mensaje: Optional[str] = ""


# ============================================================
# 4. UTILIDADES
# ============================================================

_response_cache: Dict[str, str] = {}


def get_cache_key(texto: str) -> str:
    normalizado = " ".join(texto.lower().split())
    return hashlib.md5(normalizado.encode()).hexdigest()


def guardar_en_cache(clave: str, valor: str):
    _response_cache[clave] = valor
    if len(_response_cache) > config.CACHE_MAX_SIZE:
        del _response_cache[next(iter(_response_cache))]


def limpiar_markdown(texto: str) -> str:
    if not texto:
        return ""
    patrones = [
        (r'\*\*(.*?)\*\*', r'\1'),
        (r'\*(.*?)\*', r'\1'),
        (r'__(.*?)__', r'\1'),
        (r'_(.*?)_', r'\1'),
        (r'^\s*[\*\-+]\s+', ''),
        (r'^\s*\d+\.\s+', ''),
    ]
    for patron, reemplazo in patrones:
        flags = re.MULTILINE if patron.startswith('^') else 0
        texto = re.sub(patron, reemplazo, texto, flags=flags)
    return re.sub(r'\s+', ' ', texto).strip()


def solo_texto(texto: Optional[str]) -> str:
    return texto.strip() if texto else ""


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


# ============================================================
# CONTEXTO DINÁMICO DEL NEGOCIO (productos + estado, con caché)
# ============================================================

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


# ============================================================
# 5. RESPUESTAS DE RESPALDO (sin IA)
# ============================================================

async def respuesta_fallback(mensaje: str) -> str:
    texto = mensaje.lower()
    for palabras, clave in PALABRAS_CLAVE_FALLBACK:
        if any(p in texto for p in palabras):
            return RESPUESTAS_FALLBACK[clave]
    return "Para más información, contáctanos por WhatsApp al 0412-0336537."


# ============================================================
# 6. IA (Groq)
# ============================================================

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


# ============================================================
# 7. LOGS DE CONVERSACIÓN (Supabase, en segundo plano)
# ============================================================

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


# ============================================================
# 8. NOTIFICACIÓN WHATSAPP (Twilio, en segundo plano)
# ============================================================

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
https://minelva-chatbot-backend.onrender.com/admin/login
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


# ============================================================
# 9. PEDIDOS (Supabase)
# ============================================================

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


# ============================================================
# 10. ADMIN: AUTENTICACIÓN Y AYUDANTES DE SUPABASE
# ============================================================

def _requiere_admin(request: Request) -> Optional[dict]:
    """Retorna un dict de error si no hay sesión de admin activa, o None si está autorizado."""
    if not request.session.get("admin", False):
        return {"error": "No autorizado", "auth_required": True}
    return None


async def _consulta_supabase(fn: Callable) -> tuple[Any, Optional[str]]:
    """Ejecuta una consulta de Supabase en un hilo aparte y normaliza los errores."""
    if clients.supabase is None:
        return None, "Base de datos no disponible"
    try:
        return await ejecutar_en_hilo(fn), None
    except Exception as e:
        return None, str(e)


def _html_login(mostrar_error: bool = False) -> str:
    error_html = '<div class="error">Usuario o contraseña incorrectos</div>' if mostrar_error else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Minelva</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-box {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 350px; text-align: center; }}
            h2 {{ color: #0077B6; margin-bottom: 20px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ background: #0077B6; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }}
            button:hover {{ background: #005f8f; }}
            .error {{ color: red; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Panel Administrativo Minelva</h2>
            <form method="post" action="/admin/login">
                <input type="text" name="username" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Ingresar</button>
                {error_html}
            </form>
        </div>
    </body>
    </html>
    """


# ============================================================
# 11. APLICACIÓN FASTAPI
# ============================================================

app = FastAPI(
    title="API Chatbot Minelva",
    description="Agente conversacional para Minelva Los Morros",
    version="6.0.0",
)

app.add_middleware(SessionMiddleware, secret_key=config.SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

init_clients()


# ---------------- Endpoints públicos ----------------

@app.get("/")
async def root():
    return {"mensaje": "API del Chatbot Minelva funcionando", "status": "online", "version": "6.0.0"}


def _ping_supabase_sync():
    """Consulta mínima y barata: solo cuenta filas, no trae datos."""
    return clients.supabase.table("logs_conversacion").select("id_log", count="exact").limit(1).execute()


@app.get("/health")
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


@app.post("/chat")
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


@app.post("/pedido")
async def pedido_endpoint(pedido: Pedido):
    pedido_id, mensaje = await registrar_pedido_en_db(pedido)
    return RespuestaPedido(mensaje=mensaje, pedido_id=pedido_id)


# ---------------- Endpoints admin: autenticación ----------------

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page():
    return _html_login()


@app.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...), request: Request = None):
    if username == config.ADMIN_USER and password == config.ADMIN_PASS:
        request.session["admin"] = True
        return RedirectResponse(url="/static/admin.html", status_code=303)
    return HTMLResponse(content=_html_login(mostrar_error=True), status_code=401)


@app.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login")


# ---------------- Endpoints admin: pedidos ----------------

@app.get("/admin/pedidos")
async def admin_get_pedidos(request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").select("*").order("fecha_creacion", desc=True).execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    return {"pedidos": result.data}


@app.get("/admin/pedidos/{pedido_id}")
async def admin_get_pedido(pedido_id: str, request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").select("*").eq("id_pedido", pedido_id).execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"pedido": result.data[0]}
    return {"error": "Pedido no encontrado"}


@app.put("/admin/pedidos/{pedido_id}/estado")
async def admin_update_estado(pedido_id: str, estado: str, request: Request):
    if error := _requiere_admin(request):
        return error
    if estado not in config.ESTADOS_VALIDOS:
        return {"error": f"Estado inválido. Opciones: {', '.join(config.ESTADOS_VALIDOS)}"}

    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").update({"estado": estado}).eq("id_pedido", pedido_id).execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"mensaje": f"Pedido actualizado a {estado}", "pedido": result.data[0]}
    return {"error": "Pedido no encontrado"}


@app.delete("/admin/pedidos/{pedido_id}")
async def admin_delete_pedido(pedido_id: str, request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").delete().eq("id_pedido", pedido_id).execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"mensaje": "Pedido eliminado correctamente"}
    return {"error": "Pedido no encontrado"}


# ---------------- Endpoints admin: productos y precios ----------------

@app.get("/admin/productos")
async def admin_get_productos(request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").select("*").order("orden").execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    return {"productos": result.data}


@app.post("/admin/productos")
async def admin_crear_producto(producto: ProductoInput, request: Request):
    if error := _requiere_admin(request):
        return error
    data = producto.model_dump()
    data["fecha_actualizacion"] = datetime.now().isoformat()

    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").insert(data).execute() # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    invalidar_cache_negocio()
    return {"mensaje": "Producto creado", "producto": result.data[0] if result.data else None}


@app.put("/admin/productos/{producto_id}")
async def admin_editar_producto(producto_id: str, producto: ProductoInput, request: Request):
    if error := _requiere_admin(request):
        return error
    data = producto.model_dump()
    data["fecha_actualizacion"] = datetime.now().isoformat()

    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").update(data).eq("id_producto", producto_id).execute()
    )
    if error_msg:
        return {"error": error_msg}
    invalidar_cache_negocio()
    if result.data:
        return {"mensaje": "Producto actualizado", "producto": result.data[0]}
    return {"error": "Producto no encontrado"}


@app.delete("/admin/productos/{producto_id}")
async def admin_eliminar_producto(producto_id: str, request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").delete().eq("id_producto", producto_id).execute()
    )
    if error_msg:
        return {"error": error_msg}
    invalidar_cache_negocio()
    if result.data:
        return {"mensaje": "Producto eliminado correctamente"}
    return {"error": "Producto no encontrado"}


# ---------------- Endpoints admin: estado del negocio ----------------

@app.get("/admin/estado-negocio")
async def admin_get_estado_negocio(request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("estado_negocio").select("*").limit(1).execute()
    )
    if error_msg:
        return {"error": error_msg}
    fila = (result.data or [None])[0]
    return {"estado": fila or {"abierto": True, "mensaje": ""}}


@app.put("/admin/estado-negocio")
async def admin_actualizar_estado_negocio(estado: EstadoNegocioInput, request: Request):
    if error := _requiere_admin(request):
        return error
    data = {
        "id": 1,
        "abierto": estado.abierto,
        "mensaje": estado.mensaje or "",
        "fecha_actualizacion": datetime.now().isoformat(),
    }
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("estado_negocio").upsert(data).execute()
    )
    if error_msg:
        return {"error": error_msg}
    invalidar_cache_negocio()
    return {"mensaje": "Estado del negocio actualizado", "estado": result.data[0] if result.data else data}


# ============================================================
# 12. EJECUCIÓN LOCAL
# ============================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)