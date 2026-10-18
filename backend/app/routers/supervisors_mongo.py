from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies_mongo import require_permission
from app.orm_models.supervisor_mongo import Supervisor
from app.orm_models.user_mongo import User
from app.schemas.supervisor_mongo import (
    Supervisor_Create,
    Supervisor_Read,
    Supervisor_Update,
)

router = APIRouter(prefix="/supervisors", tags=["supervisors"])

def supervisor_not_found(supervisor_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Supervisor '{supervisor_id}' does not exist.",
    )

@router.get("", response_model=list[Supervisor_Read])
async def list_supervisors(
    _: User = Depends(require_permission("supervisors:read")),
) -> list[Supervisor]:
    return await Supervisor.find_all().sort("+id").to_list()

@router.get("/{supervisor_id}", response_model=Supervisor_Read)
async def find_supervisor_by_id(
    supervisor_id: PydanticObjectId,
    _: User = Depends(require_permission("supervisors:read")),
) -> Supervisor:
    target_supervisor = await Supervisor.get(supervisor_id)
    if target_supervisor is None:
        raise supervisor_not_found(supervisor_id)
    return target_supervisor

@router.patch("/{supervisor_id}", response_model=Supervisor_Read)
async def update_supervisor(
    supervisor_id: PydanticObjectId,
    payload: Supervisor_Update,
    _: User = Depends(require_permission("supervisors:update")),
) -> Supervisor:
    target_supervisor = await Supervisor.get(supervisor_id)
    if target_supervisor is None:
        raise supervisor_not_found(supervisor_id)

    for field, value in payload.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ).items():
        setattr(target_supervisor, field, value)

    await target_supervisor.save()
    return target_supervisor

@router.post(
    "",
    response_model=Supervisor_Read,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_supervisor(
    payload: Supervisor_Create,
    _: User = Depends(require_permission("supervisors:create")),
) -> Supervisor:
    new_supervisor = Supervisor(**payload.model_dump())
    await new_supervisor.insert()
    return new_supervisor

@router.delete(
    "/{supervisor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_supervisor(
    supervisor_id: PydanticObjectId,
    _: User = Depends(require_permission("supervisors:delete")),
) -> Response:
    target_supervisor = await Supervisor.get(supervisor_id)
    if target_supervisor is None:
        raise supervisor_not_found(supervisor_id)

    await target_supervisor.fetch_link(Supervisor.farms)
    if target_supervisor.farms:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a supervisor that is assigned to farms.",
        )

    await target_supervisor.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
