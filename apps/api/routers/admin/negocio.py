"""Endpoints admin: estado del negocio (abierto/cerrado)."""
from datetime import datetime
from fastapi import APIRouter, Request

from clients import clients
from models.schemas import EstadoNegocioInput
from services.admin_service import _requiere_admin, _consulta_supabase
from services.negocio_service import invalidar_cache_negocio

router = APIRouter()


@router.get("/admin/estado-negocio")
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


@router.put("/admin/estado-negocio")
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
