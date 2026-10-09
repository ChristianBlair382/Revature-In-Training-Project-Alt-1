from tests.conftest import auth_header
from app.orm_models import Farm

async def test_list_field_jobs_requires_auth(client, seeded_users):
    failure_response = await client.get("/field_jobs")
    assert failure_response.status_code == 401

    success_response = await client.get("/field_jobs", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200

async def test_list_colocation_discrepencies(
    client,
    db_session,
    seeded_field_job,
    seeded_hand,
    seeded_farm,
    seeded_users,
):
    other_farm = Farm(
        name="other_farm",
        location_region="other_region",
        capacity=10,
        supervisor_id=seeded_farm.supervisor_id,
    )
    db_session.add(other_farm)
    await db_session.flush()
    seeded_hand.farm_id = other_farm.id
    await db_session.commit()

    response = await client.get(
        "/field_jobs/discrepencies",
        headers=auth_header(seeded_users["auditor"]),
    )

    assert response.status_code == 200
    assert [item["field_job_id"] for item in response.json()] == [seeded_field_job.id]
    assert response.json()[0]["equipment_farm_id"] != response.json()[0]["hand_farm_id"]