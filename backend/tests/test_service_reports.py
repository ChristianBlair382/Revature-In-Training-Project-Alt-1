from tests.conftest import auth_header

def test_verify_service_report_files_matches_s3_objects():
    from scripts.verify_service_report import verify_service_report_files

    assert verify_service_report_files(
        {
            1: "s3://agricore-service-reports-cb2478/service_reports/present.pdf",
            2: "s3://agricore-service-reports-cb2478/service_reports/missing.pdf",
            3: "https://example.com/report.pdf",
        },
        {"service_reports/present.pdf"},
    ) == {1: True, 2: False, 3: False}

async def test_list_service_reports_requires_auth(client, seeded_users):
    failure_response = await client.get("/service_reports")
    assert failure_response.status_code == 401

    success_response = await client.get("/service_reports", headers=auth_header(seeded_users["auditor"]))
    assert success_response.status_code == 200

async def test_upload_service_report_file_returns_s3_url(
    client,
    seeded_users,
    monkeypatch,
):
    from app.routers import service_reports

    def fake_upload_to_s3(file_obj, filename, content_type):
        assert file_obj.read() == b"report contents"
        assert filename == "report.pdf"
        assert content_type == "application/pdf"
        return "s3://agricore-service-reports-cb2478/service_reports/test_report.pdf"

    monkeypatch.setattr(service_reports, "upload_to_s3", fake_upload_to_s3)

    denied_response = await client.post(
        "/service_reports/upload",
        files={"file": ("report.pdf", b"report contents", "application/pdf")},
        headers=auth_header(seeded_users["auditor"]),
    )
    assert denied_response.status_code == 403

    upload_response = await client.post(
        "/service_reports/upload",
        files={"file": ("report.pdf", b"report contents", "application/pdf")},
        headers=auth_header(seeded_users["admin"]),
    )
    assert upload_response.status_code == 201
    assert upload_response.json() == {
        "file_url": "s3://agricore-service-reports-cb2478/service_reports/test_report.pdf"
    }

async def test_service_report_verification_returns_each_reports_status(
    client,
    seeded_users,
    seeded_service_report,
    monkeypatch,
):
    from app.routers import service_reports

    def fake_verify_service_report_files(file_urls):
        assert file_urls == {seeded_service_report.id: "test_url"}
        return {seeded_service_report.id: False}

    monkeypatch.setattr(
        service_reports,
        "verify_service_report_files",
        fake_verify_service_report_files,
    )

    response = await client.get(
        "/service_reports/verification",
        headers=auth_header(seeded_users["auditor"]),
    )

    assert response.status_code == 200
    assert response.json() == [
        {"service_report_id": seeded_service_report.id, "verified": False}
    ]