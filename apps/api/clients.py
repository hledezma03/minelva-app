"""Clientes de servicios externos: Groq (IA) y Supabase (base de datos)."""
from typing import Optional
from groq import AsyncGroq
from supabase import create_client, Client

from config import config
from services.whatsapp_service import TWILIO_LIB_DISPONIBLE


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
