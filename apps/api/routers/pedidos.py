"""Endpoint /pedido (creación de pedidos desde el chatbot)."""
from fastapi import APIRouter

from models.schemas import Pedido, RespuestaPedido
from services.pedido_service import registrar_pedido_en_db

router = APIRouter()


@router.post("/pedido")
async def pedido_endpoint(pedido: Pedido):
    pedido_id, mensaje = await registrar_pedido_en_db(pedido)
    return RespuestaPedido(mensaje=mensaje, pedido_id=pedido_id)
