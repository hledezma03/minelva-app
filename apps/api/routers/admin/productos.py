"""Endpoints admin: gestión de productos y precios."""
from datetime import datetime
from fastapi import APIRouter, Request

from clients import clients
from models.schemas import ProductoInput
from services.admin_service import _requiere_admin, _consulta_supabase
from services.negocio_service import invalidar_cache_negocio

router = APIRouter()


@router.get("/admin/productos")
async def admin_get_productos(request: Request):
    if error := _requiere_admin(request):
        return error
    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").select("*").order("orden").execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    return {"productos": result.data}


@router.post("/admin/productos")
async def admin_crear_producto(producto: ProductoInput, request: Request):
    if error := _requiere_admin(request):
        return error
    data = producto.model_dump()
    data["fecha_actualizacion"] = datetime.now().isoformat()

    result, error_msg = await _consulta_supabase(
        lambda: clients.supabase.table("productos").insert(data).execute()  # type: ignore
    )
    if error_msg:
        return {"error": error_msg}
    invalidar_cache_negocio()
    return {"mensaje": "Producto creado", "producto": result.data[0] if result.data else None}


@router.put("/admin/productos/{producto_id}")
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


@router.delete("/admin/productos/{producto_id}")
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
