# Run with: python -m scripts.seed_tables
# From: backend/ with venv active

import asyncio
from decimal import Decimal

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

        supervisor = Supervisor(name="Jordan Reyes")
        session.add(supervisor)
        await session.flush()

        farm = Farm(
            name="Green Valley Farm",
            location_region="Central Valley",
            capacity=1200,
            supervisor_id=supervisor.id,
        )
        session.add(farm)
        await session.flush()

        hands = [
            Hand(name="Casey Morgan", farm_id=farm.id),
            Hand(name="Riley Chen", farm_id=farm.id),
        ]
        equipment = [
            Equipment(
                serial_num="GV-TRACTOR-001",
                model="John Deere 5075E",
                status=EQUIPMENT_STATUS.IN_USE,
                fuel_lvl=Decimal("76.50"),
                farm_id=farm.id,
            ),
            Equipment(
                serial_num="GV-HARVESTER-001",
                model="Case IH 8250",
                status=EQUIPMENT_STATUS.IDLE,
                fuel_lvl=Decimal("42.00"),
                farm_id=farm.id,
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
                hand_id=hands[0].id,
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
    asyncio.run(seed_tables())