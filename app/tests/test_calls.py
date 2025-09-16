from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_outbound_create_list_update_transcript():
    # Create outbound call
    payload = {
        "caller_number": "+911112223334",
        "receiver_number": "+919998887776",
        "provider_call_id": "OUT-999"
    }
    r = client.post("/calls/outbound", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    call_id = created["id"]
    assert created["status"] == "queued"

    # List calls
    r2 = client.get("/calls?limit=10")
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(it["id"] == call_id for it in items)

    # Update status
    r3 = client.patch(f"/calls/{call_id}/status", json={"status": "in-progress"})
    assert r3.status_code == 200
    assert r3.json()["status"] == "in-progress"

    # Append transcript
    r4 = client.post(f"/calls/{call_id}/append-transcript", json={"text": "Hello there"})
    assert r4.status_code == 200
    assert "Hello there" in r4.json()["transcript"]
