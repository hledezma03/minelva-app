"""Ayudantes compartidos por los endpoints /admin/*: verificación de
sesión, envoltorio de consultas a Supabase, y la página HTML de login."""
from typing import Callable, Any, Optional
from fastapi import Request

from clients import clients
from utils.async_helpers import ejecutar_en_hilo


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
