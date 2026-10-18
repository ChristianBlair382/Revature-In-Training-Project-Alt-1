from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pymongo.errors import DuplicateKeyError

from app.dependencies_mongo import require_permission
from app.orm_models.equipment_mongo import Equipment
from app.orm_models.farm_mongo import Farm
from app.orm_models.user_mongo import User
from app.schemas.equipment_mongo import (
    Equipment_Create,
    Equipment_Read,
    Equipment_Update,
    Equipment_Update_Status,
)

router = APIRouter(prefix="/equipments", tags=["equipments"])

def equipment_not_found(equipment_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Equipment '{equipment_id}' does not exist.",
    )

async def get_farm(farm_id: PydanticObjectId) -> Farm:
    farm = await Farm.get(farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm '{farm_id}' does not exist.",
        )
    return farm

def duplicate_serial_number() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Equipment serial number already exists.",
    )

@router.get("", response_model=list[Equipment_Read])
async def list_equipments(
    _: User = Depends(require_permission("equipments:read")),
) -> list[Equipment]:
    return await Equipment.find_all().sort("+id").to_list()

@router.get("/{equipment_id}", response_model=Equipment_Read)
async def find_equipment_by_id(
    equipment_id: PydanticObjectId,
    _: User = Depends(require_permission("equipments:read")),
) -> Equipment:
    target_equipment = await Equipment.get(equipment_id)
    if target_equipment is None:
        raise equipment_not_found(equipment_id)
    return target_equipment

@router.patch("/{equipment_id}/status", response_model=Equipment_Read)
async def update_equipment_status(
    equipment_id: PydanticObjectId,
    payload: Equipment_Update_Status,
    _: User = Depends(require_permission("equipments:update")),
) -> Equipment:
    target_equipment = await Equipment.get(equipment_id)
    if target_equipment is None:
        raise equipment_not_found(equipment_id)

    target_equipment.update_status(payload.status)
    await target_equipment.save()
    return target_equipment

@router.patch("/{equipment_id}", response_model=Equipment_Read)
async def update_equipment(
    equipment_id: PydanticObjectId,
    payload: Equipment_Update,
    _: User = Depends(require_permission("equipments:update")),
) -> Equipment:
    target_equipment = await Equipment.get(equipment_id)
    if target_equipment is None:
        raise equipment_not_found(equipment_id)

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "farm_id" in changes:
        changes["farm"] = await get_farm(changes.pop("farm_id"))

    for field, value in changes.items():
        setattr(target_equipment, field, value)

    try:
        await target_equipment.save()
    except DuplicateKeyError as exc:
        raise duplicate_serial_number() from exc
    return target_equipment

@router.post("", response_model=Equipment_Read, status_code=status.HTTP_201_CREATED)
async def create_new_equipment(
    payload: Equipment_Create,
    _: User = Depends(require_permission("equipments:create")),
) -> Equipment:
    equipment_data = payload.model_dump()
    farm = await get_farm(equipment_data.pop("farm_id"))
    new_equipment = Equipment(**equipment_data, farm=farm)
    try:
        await new_equipment.insert()
    except DuplicateKeyError as exc:
        raise duplicate_serial_number() from exc
    return new_equipment

@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: PydanticObjectId,
    _: User = Depends(require_permission("equipments:delete")),
) -> Response:
    target_equipment = await Equipment.get(equipment_id)
    if target_equipment is None:
        raise equipment_not_found(equipment_id)

    await target_equipment.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
