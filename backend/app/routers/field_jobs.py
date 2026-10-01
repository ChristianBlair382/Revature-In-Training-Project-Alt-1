from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import (
    Field_Job,
    FIELD_JOB_STATUS, 
    FIELD_JOB_PRIORITY, 
    Equipment, 
    Hand, 
    User, 
    USER_ROLE
)
from app.schemas import (
    Field_Job_Create, 
    Field_Job_Read, 
    Field_Job_Discrepency_Read, 
    Field_Job_Update_Status, 
    Field_Job_Update_Priority,
    Field_Job_Update
)

router = APIRouter(prefix="/field_jobs", tags=["field_jobs"])

# GET Routers

@router.get("", response_model=list[Field_Job_Read])
async def list_field_jobs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Field_Job).order_by(Field_Job.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/{field_job_id}", response_model=Field_Job_Read)
async def find_field_job_by_id(
    field_job_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_field_job = await db.get(Field_Job, field_job_id)

    if (not target_field_job):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{field_job_id}' does not exist."
        )
    return target_field_job

@router.get("/discrepencies", response_model=list[Field_Job_Discrepency_Read])
async def isolate_colocation_discrepencies(
    priority: FIELD_JOB_PRIORITY | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = (
        select(
            Field_Job.id.label("field_job_id"),
            Field_Job.title,
            Field_Job.equipment_id,
            Field_Job.hand_id,
            Equipment.farm_id.label("equipment_farm_id"),
            Hand.farm_id.label("hand_farm_id")
        )
        .join(Equipment, Equipment.id == Field_Job.equipment_id)
        .join(Hand, Hand.id == Field_Job.hand_id)
        .where(Equipment.farm_id != Hand.farm_id)
        .order_by(Field_Job.id)
    )

    if (priority is not None):
        db_command = db_command.where(Field_Job.priority == priority)

    output = await db.execute(db_command)
    return list(output.mappings().all())

# PATCH Routers

@router.patch("/{field_job_id}/status", response_model=Field_Job_Read)
async def update_field_job_status(
    field_job_id: int,
    payload: Field_Job_Update_Status,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH))
):
    target_field_job = await db.get(Field_Job, field_job_id)
    if (not target_field_job):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{field_job_id}' does not exist."
        )
    
    target_field_job.update_status(payload.status)

    await db.commit()
    await db.refresh(target_field_job)
    return target_field_job

@router.patch("/{field_job_id}/priority", response_model=Field_Job_Read)
async def update_field_job_priority(
    field_job_id: int,
    payload: Field_Job_Update_Priority,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH))
):
    target_field_job = await db.get(Field_Job, field_job_id)
    if (not target_field_job):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{field_job_id}' does not exist."
        )

    target_field_job.update_priority(payload.priority)

    await db.commit()
    await db.refresh(target_field_job)
    return target_field_job

@router.patch("/{field_job_id}", response_model=Field_Job_Read)
async def update_field_job(
    field_job_id: int,
    payload: Field_Job_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_field_job = await db.get(Field_Job, field_job_id)
    if (not target_field_job):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{field_job_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_field_job, field, value)

    await db.commit()
    await db.refresh(target_field_job)
    return target_field_job

# POST Routers

@router.post("", response_model=Field_Job_Read, status_code=status.HTTP_201_CREATED)
async def create_new_field_job(
    payload: Field_Job_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    new_field_job = Field_Job(**payload.model_dump)
    db.add(new_field_job)
    await db.commit()
    await db.refresh(new_field_job)
    return new_field_job

# DELETE Routers

@router.delete("/{target_field_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field_job(
    target_field_job_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_field_job = await db.get(Field_Job, target_field_job_id)
    if (not target_field_job):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{target_field_job_id}' does not exist."
        )

    await db.delete(target_field_job)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)