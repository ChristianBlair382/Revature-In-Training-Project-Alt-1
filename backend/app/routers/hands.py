from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import Hand, User, USER_ROLE
from app.schemas import Hand_Create, Hand_Read, Hand_Update

router = APIRouter(prefix="/hands", tags=["hands"])

# GET Routers

@router.get("", response_model=list[Hand_Read])
async def list_hands(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Hand).order_by(Hand.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{hand_id}", response_model=Hand_Read)
async def find_hand_by_id(
    hand_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_hand = await db.get(Hand, hand_id)

    if (not target_hand):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hand '{hand_id}' does not exist."
        )
    return target_hand

# PATCH Routers

@router.patch("/{hand_id}", response_model=Hand_Read)
async def update_hand(
    hand_id: int,
    payload: Hand_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_hand = await db.get(Hand, hand_id)
    if (not target_hand):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hand '{hand_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_hand, field, value)

    await db.commit()
    await db.refresh(target_hand)
    return target_hand

# POST Routers

@router.post("", response_model=Hand_Read, status_code=status.HTTP_201_CREATED)
async def create_new_hand(
    payload: Hand_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_hand = Hand(**payload.model_dump)
    db.add(new_hand)
    await db.commit()
    await db.refresh(new_hand)
    return new_hand

# DELETE Routers

@router.delete("/{target_hand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hand(
    target_hand_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_hand = await db.get(Hand, target_hand_id)
    if (not target_hand):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hand '{target_hand_id}' does not exist."
        )

    await db.delete(target_hand)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)