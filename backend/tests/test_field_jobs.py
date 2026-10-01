from tests.conftest import auth_header

async def test_list_field_jobs_requires_auth(client, seeded_users):
    failure_response = await client.get("/field_jobs")
    assert failure_response.status_code == 401

    success_response = await client.get("/field_jobs", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200