from tests.conftest import auth_header

async def test_list_supervisors_requires_auth(client, seeded_users):
    failure_response = await client.get("/supervisors")
    assert failure_response.status_code == 401

    success_response = await client.get("/supervisors", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200