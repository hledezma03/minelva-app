"""Endpoints admin: gestión de pedidos."""
from fastapi import APIRouter, Request

from config import config
from clients import clients
from services.admin_service import _requiere_admin, _consulta_supabase

router = APIRouter()


@router.get("/admin/pedidos")
async def admin_get_pedidos(request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").select("*").order("fecha_creacion", desc=True).execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    return {"pedidos": result.data}


@router.get("/admin/pedidos/{pedido_id}")
async def admin_get_pedido(pedido_id: str, request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").select("*").eq("id_pedido", pedido_id).execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"pedido": result.data[0]}
    return {"error": "Pedido no encontrado"}


@router.put("/admin/pedidos/{pedido_id}/estado")
async def admin_update_estado(pedido_id: str, estado: str, request: Request):
    if error := _requiere_admin(request):
        return error
    if estado not in config.ESTADOS_VALIDOS:
        return {"error": f"Estado inválido. Opciones: {', '.join(config.ESTADOS_VALIDOS)}"}

    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").update({"estado": estado}).eq("id_pedido", pedido_id).execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"mensaje": f"Pedido actualizado a {estado}", "pedido": result.data[0]}
    return {"error": "Pedido no encontrado"}


@router.delete("/admin/pedidos/{pedido_id}")
async def admin_delete_pedido(pedido_id: str, request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("pedidos").delete().eq("id_pedido", pedido_id).execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    if result.data:
        return {"mensaje": "Pedido eliminado correctamente"}
    return {"error": "Pedido no encontrado"}
