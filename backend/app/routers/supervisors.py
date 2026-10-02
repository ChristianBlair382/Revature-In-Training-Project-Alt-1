from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import Supervisor, User, USER_ROLE
from app.schemas import Supervisor_Create, Supervisor_Read, Supervisor_Update

router = APIRouter(prefix="/supervisors", tags=["supervisors"])

# GET Routers

@router.get("", response_model=list[Supervisor_Read])
async def list_supervisors(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Supervisor).order_by(Supervisor.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{supervisor_id}", response_model=Supervisor_Read)
async def find_supervisor_by_id(
    supervisor_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_supervisor = await db.get(Supervisor, supervisor_id)

    if (not target_supervisor):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor '{supervisor_id}' does not exist."
        )
    return target_supervisor

# PATCH Routers

@router.patch("/{supervisor_id}", response_model=Supervisor_Read)
async def update_supervisor(
    supervisor_id: int,
    payload: Supervisor_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_supervisor = await db.get(Supervisor, supervisor_id)
    if (not target_supervisor):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor '{supervisor_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_supervisor, field, value)

    await db.commit()
    await db.refresh(target_supervisor)
    return target_supervisor

# POST Routers

@router.post("", response_model=Supervisor_Read, status_code=status.HTTP_201_CREATED)
async def create_new_supervisor(
    payload: Supervisor_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_supervisor = Supervisor(**payload.model_dump())
    db.add(new_supervisor)
    await db.commit()
    await db.refresh(new_supervisor)
    return new_supervisor

# DELETE Routers

@router.delete("/{target_supervisor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supervisor(
    target_supervisor_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_supervisor = await db.get(Supervisor, target_supervisor_id)
    if (not target_supervisor):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor '{target_supervisor_id}' does not exist."
        )

    await db.delete(target_supervisor)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)