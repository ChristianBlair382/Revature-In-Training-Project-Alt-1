from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import User, USER_ROLE
from app.schemas import User_Create, User_Read, User_Update

router = APIRouter(prefix="/users", tags=["users"])

# GET Routers

@router.get("", response_model=list[User_Read])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(User).order_by(User.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{user_id}", response_model=User_Read)
async def find_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_user = await db.get(User, user_id)

    if (not target_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' does not exist."
        )
    return target_user

# PATCH Routers

@router.patch("/{user_id}", response_model=User_Read)
async def update_user(
    user_id: int,
    payload: User_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_user = await db.get(User, user_id)
    if (not target_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_user, field, value)

    await db.commit()
    await db.refresh(target_user)
    return target_user

# POST Routers

@router.post("", response_model=User_Read, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    payload: User_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_user = User(**payload.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# DELETE Routers

@router.delete("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    target_user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_user = await db.get(User, target_user_id)
    if (not target_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{target_user_id}' does not exist."
        )

    await db.delete(target_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)