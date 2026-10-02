from tests.conftest import auth_header

async def test_list_equipments_requires_auth(client, seeded_users):
    failure_response = await client.get("/equipments")
    assert failure_response.status_code == 401

    success_response = await client.get("/equipments", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200

async def test_list_equipments_includes_default_low_fuel_check(
    client, db_session, seeded_users, seeded_equipment
):
    seeded_equipment.fuel_lvl = 20
    await db_session.commit()

    response = await client.get("/equipments", headers=auth_header(seeded_users["auditor"]))

    assert response.status_code == 200
    assert response.json()[0]["low_fuel"] is True
    assert seeded_equipment.is_low_fuel(threshold=19) is False