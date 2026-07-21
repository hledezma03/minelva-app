"""
API del Chatbot Minelva Los Morros
Versión 6.0 - Refactorizada: async no bloqueante + estructura modular
(config, clients, models, services, routers)
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

from config import config
from clients import init_clients
from routers import public, chat, pedidos
from routers.admin import auth as admin_auth
from routers.admin import pedidos as admin_pedidos
from routers.admin import productos as admin_productos
from routers.admin import negocio as admin_negocio

# ============================================================
# APLICACIÓN FASTAPI
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

# ---------------- Registro de routers ----------------

app.include_router(public.router)
app.include_router(chat.router)
app.include_router(pedidos.router)
app.include_router(admin_auth.router)
app.include_router(admin_pedidos.router)
app.include_router(admin_productos.router)
app.include_router(admin_negocio.router)


# ============================================================
# EJECUCIÓN LOCAL
# ============================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
