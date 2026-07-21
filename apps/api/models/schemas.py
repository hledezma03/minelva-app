"""Modelos de datos (Pydantic) usados por la API."""
from typing import List, Optional, Dict
from pydantic import BaseModel


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
