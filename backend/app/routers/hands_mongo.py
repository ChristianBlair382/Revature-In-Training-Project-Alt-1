from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies_mongo import require_permission
from app.orm_models.farm_mongo import Farm
from app.orm_models.hand_mongo import Hand
from app.orm_models.user_mongo import User
from app.schemas.hand_mongo import Hand_Create, Hand_Read, Hand_Update

router = APIRouter(prefix="/hands", tags=["hands"])

def hand_not_found(hand_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hand '{hand_id}' does not exist.",
    )

async def get_farm(farm_id: PydanticObjectId) -> Farm:
    farm = await Farm.get(farm_id)
    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm '{farm_id}' does not exist.",
        )
    return farm

@router.get("", response_model=list[Hand_Read])
async def list_hands(
    _: User = Depends(require_permission("hands:read")),
) -> list[Hand]:
    return await Hand.find_all().sort("+id").to_list()

@router.get("/{hand_id}", response_model=Hand_Read)
async def find_hand_by_id(
    hand_id: PydanticObjectId,
    _: User = Depends(require_permission("hands:read")),
) -> Hand:
    target_hand = await Hand.get(hand_id)
    if target_hand is None:
        raise hand_not_found(hand_id)
    return target_hand

@router.patch("/{hand_id}", response_model=Hand_Read)
async def update_hand(
    hand_id: PydanticObjectId,
    payload: Hand_Update,
    _: User = Depends(require_permission("hands:update")),
) -> Hand:
    target_hand = await Hand.get(hand_id)
    if target_hand is None:
        raise hand_not_found(hand_id)

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "farm_id" in changes:
        changes["farm"] = await get_farm(changes.pop("farm_id"))

    for field, value in changes.items():
        setattr(target_hand, field, value)

    await target_hand.save()
    return target_hand

@router.post("", response_model=Hand_Read, status_code=status.HTTP_201_CREATED)
async def create_new_hand(
    payload: Hand_Create,
    _: User = Depends(require_permission("hands:create")),
) -> Hand:
    hand_data = payload.model_dump()
    farm = await get_farm(hand_data.pop("farm_id"))
    new_hand = Hand(**hand_data, farm=farm)
    await new_hand.insert()
    return new_hand

@router.delete("/{hand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hand(
    hand_id: PydanticObjectId,
    _: User = Depends(require_permission("hands:delete")),
) -> Response:
    target_hand = await Hand.get(hand_id)
    if target_hand is None:
        raise hand_not_found(hand_id)

    await target_hand.fetch_link(Hand.field_jobs)
    if target_hand.field_jobs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a hand that is assigned to field jobs.",
        )

    await target_hand.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
