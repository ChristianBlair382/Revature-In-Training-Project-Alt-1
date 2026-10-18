from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies_mongo import require_permission
from app.orm_models.farm_mongo import Farm
from app.orm_models.supervisor_mongo import Supervisor
from app.orm_models.user_mongo import User
from app.schemas.farm_mongo import Farm_Create, Farm_Read, Farm_Update

router = APIRouter(prefix="/farms", tags=["farms"])

def farm_not_found(farm_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Farm '{farm_id}' does not exist.",
    )

async def get_supervisor(supervisor_id: PydanticObjectId) -> Supervisor:
    supervisor = await Supervisor.get(supervisor_id)
    if supervisor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor '{supervisor_id}' does not exist.",
        )
    return supervisor

@router.get("", response_model=list[Farm_Read])
async def list_farms(
    _: User = Depends(require_permission("farms:read")),
) -> list[Farm]:
    return await Farm.find_all().sort("+id").to_list()

@router.get("/{farm_id}", response_model=Farm_Read)
async def find_farm_by_id(
    farm_id: PydanticObjectId,
    _: User = Depends(require_permission("farms:read")),
) -> Farm:
    target_farm = await Farm.get(farm_id)
    if target_farm is None:
        raise farm_not_found(farm_id)
    return target_farm

@router.patch("/{farm_id}", response_model=Farm_Read)
async def update_farm(
    farm_id: PydanticObjectId,
    payload: Farm_Update,
    _: User = Depends(require_permission("farms:update")),
) -> Farm:
    target_farm = await Farm.get(farm_id)
    if target_farm is None:
        raise farm_not_found(farm_id)

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "supervisor_id" in changes:
        changes["supervisor"] = await get_supervisor(changes.pop("supervisor_id"))

    for field, value in changes.items():
        setattr(target_farm, field, value)

    await target_farm.save()
    return target_farm

@router.post("", response_model=Farm_Read, status_code=status.HTTP_201_CREATED)
async def create_new_farm(
    payload: Farm_Create,
    _: User = Depends(require_permission("farms:create")),
) -> Farm:
    farm_data = payload.model_dump()
    supervisor = await get_supervisor(farm_data.pop("supervisor_id"))
    new_farm = Farm(**farm_data, supervisor=supervisor)
    await new_farm.insert()
    return new_farm

@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(
    farm_id: PydanticObjectId,
    _: User = Depends(require_permission("farms:delete")),
) -> Response:
    target_farm = await Farm.get(farm_id)
    if target_farm is None:
        raise farm_not_found(farm_id)

    await target_farm.fetch_link(Farm.equipments)
    await target_farm.fetch_link(Farm.hands)
    if target_farm.equipments or target_farm.hands:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a farm that still has equipment or hands.",
        )

    await target_farm.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
