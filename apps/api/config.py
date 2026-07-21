"""
Configuración centralizada de la aplicación.
Lee todas las variables de entorno en un solo lugar.
"""
import os
import secrets


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
