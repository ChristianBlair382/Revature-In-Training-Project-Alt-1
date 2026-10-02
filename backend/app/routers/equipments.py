from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import Equipment, EQUIPMENT_STATUS, User, USER_ROLE
from app.schemas import Equipment_Create, Equipment_Read, Equipment_Update_Status, Equipment_Update

router = APIRouter(prefix="/equipments", tags=["equipments"])

# GET Routers

@router.get("", response_model=list[Equipment_Read])
async def list_equipments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Equipment).order_by(Equipment.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{equipment_id}", response_model=Equipment_Read)
async def find_equipment_by_id(
    equipment_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_equipment = await db.get(Equipment, equipment_id)

    if (not target_equipment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment '{equipment_id}' does not exist."
        )
    return target_equipment

# PATCH Routers

@router.patch("/{target_equipment_id}/status", response_model=Equipment_Read)
async def update_equipment_status(
    target_equipment_id: int,
    payload: Equipment_Update_Status,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH))
):
    target_equipment = await db.get(Equipment, target_equipment_id)
    if (not target_equipment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment '{target_equipment_id}' does not exist."
        )
    
    target_equipment.update_status(payload.status)

    await db.commit()
    await db.refresh(target_equipment)
    return target_equipment

@router.patch("/{target_equipment_id}", response_model=Equipment_Read)
async def update_equipment(
    target_equipment_id: int,
    payload: Equipment_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_equipment = await db.get(Equipment, target_equipment_id)
    if (not target_equipment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment '{target_equipment_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_equipment, field, value)

    await db.commit()
    await db.refresh(target_equipment)
    return target_equipment

# POST Routers

@router.post("", response_model=Equipment_Read, status_code=status.HTTP_201_CREATED)
async def create_new_equipment(
    payload: Equipment_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_equipment = Equipment(**payload.model_dump())
    db.add(new_equipment)
    await db.commit()
    await db.refresh(new_equipment)
    return new_equipment

# DELETE Routers

@router.delete("/{target_equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    target_equipment_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_equipment = await db.get(Equipment, target_equipment_id)
    if (not target_equipment):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment '{target_equipment_id}' does not exist."
        )

    await db.delete(target_equipment)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)