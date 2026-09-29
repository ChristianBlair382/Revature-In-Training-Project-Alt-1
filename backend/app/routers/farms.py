from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import Farm, User, USER_ROLE
from app.schemas import Farm_Create, Farm_Read

router = APIRouter(prefix="/farms", tags=["farms"])

@router.get("", response_model=list[Farm_Read])
async def list_farms(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Farm).order_by(Farm.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{farm.id}", response_model=Farm_Read)
async def find_farm_by_id(
    farm_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_farm = await db.get(Farm, farm_id)

    if (not target_farm):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm '{farm_id}' does not exist."
        )
    return target_farm

@router.post("", response_model=Farm_Read, status_code=status.HTTP_201_CREATED)
async def create_new_farm(
    payload: Farm_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_farm = Farm(**payload.model_dump)
    db.add(new_farm)
    await db.commit()
    await db.refresh(new_farm)
    return new_farm