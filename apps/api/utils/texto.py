"""Utilidades de manejo de texto."""
import re
from typing import Optional


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
