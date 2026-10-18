# Run with: python -m scripts.seed_tables_mongo
# From: backend/ with the Mongo dependencies installed

import asyncio
import sys
from decimal import Decimal

from pymongo.errors import DuplicateKeyError

from app.database_mongo import close_mongo_connection, connect_to_mongo
from app.orm_models.enums import (
    EQUIPMENT_STATUS,
    FIELD_JOB_PRIORITY,
    FIELD_JOB_STATUS,
    USER_ROLE,
)
from app.orm_models.equipment_mongo import Equipment
from app.orm_models.farm_mongo import Farm
from app.orm_models.field_job_mongo import Field_Job
from app.orm_models.hand_mongo import Hand
from app.orm_models.service_report_mongo import Service_Report
from app.orm_models.supervisor_mongo import Supervisor
from app.orm_models.user_mongo import User
from app.security import encrypt_password
from scripts.seed_permissions_mongo import seed_permissions

async def get_or_create(model, field: str, value: str, **values):
    document = await model.find_one(getattr(model, field) == value)
    if document is not None:
        return document

    document = model(**{field: value}, **values)
    await document.insert()
    return document

async def seed_users() -> None:
    users = (
        ("admin", "Admin123!", USER_ROLE.FOA),
        ("field_hand", "FieldHand123!", USER_ROLE.FH),
        ("auditor", "Auditor123!", USER_ROLE.AUD),
    )
    for username, password, role in users:
        existing_user = await User.find_one(User.username == username)
        if existing_user is None:
            await User(
                username=username,
                hashed_password=encrypt_password(password),
                role=role,
            ).insert()

async def seed_domain_documents() -> None:
    supervisors = [
        await get_or_create(Supervisor, "name", name)
        for name in ("Jordan Reyes", "Hamilton Powers")
    ]

    farms = []
    for name, location_region, capacity, supervisor in (
        ("Green Valley Farm", "Central Valley", 1200, supervisors[0]),
        ("Rolling Hills Farm", "Central Valley", 1050, supervisors[1]),
    ):
        farm = await Farm.find_one(Farm.name == name)
        if farm is None:
            farm = Farm(
                name=name,
                location_region=location_region,
                capacity=capacity,
                supervisor=supervisor,
            )
            await farm.insert()
        farms.append(farm)

    hands = [
        await get_or_create(Hand, "name", name, farm=farm)
        for name, farm in (
            ("Casey Morgan", farms[0]),
            ("Adele Peterson", farms[0]),
            ("Riley Chen", farms[1]),
        )
    ]

    equipment_specs = (
        (
            "GV-TRACTOR-001",
            "John Deere 5075E",
            EQUIPMENT_STATUS.IN_USE,
            Decimal("76.50"),
            farms[0],
        ),
        (
            "GV-HARVESTER-001",
            "Case IH 8250",
            EQUIPMENT_STATUS.IDLE,
            Decimal("42.00"),
            farms[1],
        ),
        (
            "GV-AGRIGATOR-001",
            "Xevious 3950",
            EQUIPMENT_STATUS.IDLE,
            Decimal("13.00"),
            farms[1],
        ),
    )
    equipment = []
    for serial_num, model, status, fuel_lvl, farm in equipment_specs:
        item = await Equipment.find_one(Equipment.serial_num == serial_num)
        if item is None:
            item = Equipment(
                serial_num=serial_num,
                model=model,
                status=status,
                fuel_lvl=fuel_lvl,
                farm=farm,
            )
            await item.insert()
        equipment.append(item)

    field_job_specs = (
        (
            "Irrigate north field",
            FIELD_JOB_PRIORITY.CRITICAL,
            FIELD_JOB_STATUS.IN_PROGRESS,
            equipment[0],
            hands[2],
        ),
        (
            "Inspect harvesting equipment",
            FIELD_JOB_PRIORITY.MEDIUM,
            FIELD_JOB_STATUS.PENDING,
            equipment[1],
            hands[1],
        ),
    )
    field_jobs = []
    for title, priority, status, equipment_item, hand in field_job_specs:
        job = await Field_Job.find_one(Field_Job.title == title)
        if job is None:
            job = Field_Job(
                title=title,
                priority=priority,
                status=status,
                equipment=equipment_item,
                hand=hand,
            )
            await job.insert()
        field_jobs.append(job)

    report_specs = (
        (
            "https://example.com/service-reports/irrigation-check.pdf",
            "Irrigation lines checked; pressure is within operating range.",
            field_jobs[0],
        ),
        (
            "https://example.com/service-reports/harvester-inspection.pdf",
            "Pre-season inspection completed; no repairs required.",
            field_jobs[1],
        ),
    )
    for file_url, notes, field_job in report_specs:
        report = await Service_Report.find_one(Service_Report.file_url == file_url)
        if report is None:
            await Service_Report(
                file_url=file_url,
                notes=notes,
                field_job=field_job,
            ).insert()

async def seed_tables() -> None:
    await connect_to_mongo()
    try:
        await seed_permissions()
        await seed_users()
        await seed_domain_documents()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    try:
        asyncio.run(seed_tables())
        print(
            "MongoDB data seeded."
        )
    except DuplicateKeyError:
        print(
            "MongoDB rejected duplicate seed data. Check unique indexes and "
            "existing documents.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
