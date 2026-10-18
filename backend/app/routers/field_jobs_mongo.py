from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies_mongo import require_permission
from app.orm_models.equipment_mongo import Equipment
from app.orm_models.field_job_mongo import Field_Job
from app.orm_models.hand_mongo import Hand
from app.orm_models.user_mongo import User
from app.schemas.field_job_mongo import (
    Field_Job_Create,
    Field_Job_Discrepency_Read,
    Field_Job_Read,
    Field_Job_Update,
    Field_Job_Update_Priority,
    Field_Job_Update_Status,
)
from app.orm_models.enums import FIELD_JOB_PRIORITY

router = APIRouter(prefix="/field_jobs", tags=["field_jobs"])

def field_job_not_found(field_job_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Field Job '{field_job_id}' does not exist.",
    )

async def get_equipment(equipment_id: PydanticObjectId) -> Equipment:
    equipment = await Equipment.get(equipment_id)
    if equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment '{equipment_id}' does not exist.",
        )
    return equipment

async def get_hand(hand_id: PydanticObjectId) -> Hand:
    hand = await Hand.get(hand_id)
    if hand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hand '{hand_id}' does not exist.",
        )
    return hand

@router.get("", response_model=list[Field_Job_Read])
async def list_field_jobs(
    _: User = Depends(require_permission("field_jobs:read")),
) -> list[Field_Job]:
    return await Field_Job.find_all().sort("+id").to_list()

@router.get(
    "/discrepencies",
    response_model=list[Field_Job_Discrepency_Read],
)
async def isolate_colocation_discrepencies(
    priority: FIELD_JOB_PRIORITY | None = None,
    _: User = Depends(require_permission("field_jobs:read")),
) -> list[Field_Job_Discrepency_Read]:
    query = Field_Job.find_all()
    if priority is not None:
        query = Field_Job.find(Field_Job.priority == priority)
    field_jobs = await query.sort("+id").to_list()
    discrepancies: list[Field_Job_Discrepency_Read] = []

    for field_job in field_jobs:
        await field_job.fetch_link(Field_Job.equipment)
        await field_job.fetch_link(Field_Job.hand)
        equipment = field_job.equipment
        hand = field_job.hand
        await equipment.fetch_link(Equipment.farm)
        await hand.fetch_link(Hand.farm)

        equipment_farm = getattr(equipment.farm, "ref", equipment.farm)
        hand_farm = getattr(hand.farm, "ref", hand.farm)
        if equipment_farm.id != hand_farm.id:
            discrepancies.append(
                Field_Job_Discrepency_Read(
                    field_job_id=field_job.id,
                    title=field_job.title,
                    equipment_id=equipment.id,
                    hand_id=hand.id,
                    equipment_farm_id=equipment_farm.id,
                    hand_farm_id=hand_farm.id,
                )
            )
    return discrepancies

@router.get("/{field_job_id}", response_model=Field_Job_Read)
async def find_field_job_by_id(
    field_job_id: PydanticObjectId,
    _: User = Depends(require_permission("field_jobs:read")),
) -> Field_Job:
    target_field_job = await Field_Job.get(field_job_id)
    if target_field_job is None:
        raise field_job_not_found(field_job_id)
    return target_field_job

@router.patch("/{field_job_id}/status", response_model=Field_Job_Read)
async def update_field_job_status(
    field_job_id: PydanticObjectId,
    payload: Field_Job_Update_Status,
    _: User = Depends(require_permission("field_jobs:update")),
) -> Field_Job:
    target_field_job = await Field_Job.get(field_job_id)
    if target_field_job is None:
        raise field_job_not_found(field_job_id)

    target_field_job.update_status(payload.status)
    await target_field_job.save()
    return target_field_job

@router.patch("/{field_job_id}/priority", response_model=Field_Job_Read)
async def update_field_job_priority(
    field_job_id: PydanticObjectId,
    payload: Field_Job_Update_Priority,
    _: User = Depends(require_permission("field_jobs:update")),
) -> Field_Job:
    target_field_job = await Field_Job.get(field_job_id)
    if target_field_job is None:
        raise field_job_not_found(field_job_id)

    target_field_job.update_priority(payload.priority)
    await target_field_job.save()
    return target_field_job

@router.patch("/{field_job_id}", response_model=Field_Job_Read)
async def update_field_job(
    field_job_id: PydanticObjectId,
    payload: Field_Job_Update,
    _: User = Depends(require_permission("field_jobs:update")),
) -> Field_Job:
    target_field_job = await Field_Job.get(field_job_id)
    if target_field_job is None:
        raise field_job_not_found(field_job_id)

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "equipment_id" in changes:
        changes["equipment"] = await get_equipment(changes.pop("equipment_id"))
    if "hand_id" in changes:
        changes["hand"] = await get_hand(changes.pop("hand_id"))

    for field, value in changes.items():
        setattr(target_field_job, field, value)

    await target_field_job.save()
    return target_field_job

@router.post(
    "",
    response_model=Field_Job_Read,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_field_job(
    payload: Field_Job_Create,
    _: User = Depends(require_permission("field_jobs:create")),
) -> Field_Job:
    job_data = payload.model_dump()
    equipment = await get_equipment(job_data.pop("equipment_id"))
    hand = await get_hand(job_data.pop("hand_id"))
    new_field_job = Field_Job(**job_data, equipment=equipment, hand=hand)
    await new_field_job.insert()
    return new_field_job

@router.delete("/{field_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field_job(
    field_job_id: PydanticObjectId,
    _: User = Depends(require_permission("field_jobs:delete")),
) -> Response:
    target_field_job = await Field_Job.get(field_job_id)
    if target_field_job is None:
        raise field_job_not_found(field_job_id)

    await target_field_job.fetch_link(Field_Job.service_reports)
    if target_field_job.service_reports:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a field job that has service reports.",
        )

    await target_field_job.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
