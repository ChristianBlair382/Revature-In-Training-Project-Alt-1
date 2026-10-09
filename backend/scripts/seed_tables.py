# Run with: python -m scripts.seed_tables
# From: backend/ with venv active

import asyncio
import sys
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.database import AsyncSessionLocal
from app.orm_models import (
    EQUIPMENT_STATUS,
    FIELD_JOB_PRIORITY,
    FIELD_JOB_STATUS,
    USER_ROLE,
    Equipment,
    Farm,
    Field_Job,
    Hand,
    Service_Report,
    Supervisor,
    User,
)
from app.security import encrypt_password

async def seed_tables() -> None:
    async with AsyncSessionLocal() as session:
        session.add_all([
            User(username="admin", hashed_password=encrypt_password("Admin123!"), role=USER_ROLE.FOA),
            User(username="field_hand", hashed_password=encrypt_password("FieldHand123!"), role=USER_ROLE.FH),
            User(username="auditor", hashed_password=encrypt_password("Auditor123!"), role=USER_ROLE.AUD),
        ])

        supervisors = [
            Supervisor(name="Jordan Reyes"),
            Supervisor(name="Hamilton Powers"),
        ]
        session.add_all(supervisors)
        await session.flush()

        farms = [
            Farm(
                name="Green Valley Farm",
                location_region="Central Valley",
                capacity=1200,
                supervisor_id=supervisors[0].id,
            ),
            Farm(
                name="Rolling Hills Farm",
                location_region="Central Valley",
                capacity=1050,
                supervisor_id=supervisors[1].id,
            ),
        ]
        session.add_all(farms)
        await session.flush()

        hands = [
            Hand(name="Casey Morgan", farm_id=farms[0].id),
            Hand(name="Adele Peterson", farm_id=farms[0].id),
            Hand(name="Riley Chen", farm_id=farms[1].id),
        ]
        equipment = [
            Equipment(
                serial_num="GV-TRACTOR-001",
                model="John Deere 5075E",
                status=EQUIPMENT_STATUS.IN_USE,
                fuel_lvl=Decimal("76.50"),
                farm_id=farms[0].id,
            ),
            Equipment(
                serial_num="GV-HARVESTER-001",
                model="Case IH 8250",
                status=EQUIPMENT_STATUS.IDLE,
                fuel_lvl=Decimal("42.00"),
                farm_id=farms[1].id,
            ),
            Equipment(
                serial_num="GV-AGRIGATOR-001",
                model="Xevious 3950",
                status=EQUIPMENT_STATUS.IDLE,
                fuel_lvl=Decimal("13.00"),
                farm_id=farms[1].id,
            ),
        ]
        session.add_all([*hands, *equipment])
        await session.flush()

        field_jobs = [
            Field_Job(
                title="Irrigate north field",
                priority=FIELD_JOB_PRIORITY.CRITICAL,
                status=FIELD_JOB_STATUS.IN_PROGRESS,
                equipment_id=equipment[0].id,
                hand_id=hands[2].id,
            ),
            Field_Job(
                title="Inspect harvesting equipment",
                priority=FIELD_JOB_PRIORITY.MEDIUM,
                status=FIELD_JOB_STATUS.PENDING,
                equipment_id=equipment[1].id,
                hand_id=hands[1].id,
            ),
        ]
        session.add_all(field_jobs)
        await session.flush()

        session.add_all([
            Service_Report(
                file_url="https://example.com/service-reports/irrigation-check.pdf",
                notes="Irrigation lines checked; pressure is within operating range.",
                field_job_id=field_jobs[0].id,
            ),
            Service_Report(
                file_url="https://example.com/service-reports/harvester-inspection.pdf",
                notes="Pre-season inspection completed; no repairs required.",
                field_job_id=field_jobs[1].id,
            ),
        ])
        await session.commit()

if __name__ == "__main__":
    try:
        asyncio.run(seed_tables())
    except IntegrityError:
        print(
            "Seeding failed: the database rejected a constant, possibly because "
            "seed data already exists or conflicts with existing records.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None