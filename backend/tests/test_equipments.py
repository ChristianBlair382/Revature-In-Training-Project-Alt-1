from tests.conftest import auth_header

async def test_list_equipments_requires_auth(client, seeded_users):
    failure_response = await client.get("/equipments")
    assert failure_response.status_code == 401

    success_response = await client.get("/equipments", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200