from test_api import ORDER, signup


def place(client):
    signup(client)
    r = client.post("/api/orders", json=ORDER)
    assert r.status_code == 200, r.text
    return r.json()["order"]["id"]


def stored():
    import anyio

    from app import db

    return anyio.run(db.get_store_sms)


def test_demo_mode_stores_the_text_and_sends_nothing(client, monkeypatch):
    from app import sms

    def boom(text):  # a gateway must not be touched when it is not configured
        raise AssertionError("SMS gateway called without configuration")

    monkeypatch.setattr(sms, "_deliver", boom)
    place(client)

    entries = stored()
    assert len(entries) == 1
    assert entries[0]["delivery"] == "demo"
    assert "Local Rice" in entries[0]["text"]


def test_live_mode_texts_the_store(client, monkeypatch):
    from app import config, sms

    monkeypatch.setattr(config, "SMS_PROVIDER", "termii")
    monkeypatch.setattr(config, "SMS_API_KEY", "test-key")
    monkeypatch.setattr(config, "SMS_SENDER_ID", "OGS")
    monkeypatch.setattr(config, "STORE_PHONE", "+2348030000000")

    sent = {}

    def ok(text):
        sent["text"] = text
        return True, '{"code":"ok"}'

    monkeypatch.setattr(sms, "_deliver", ok)
    place(client)

    assert "Local Rice" in sent["text"]
    assert stored()[0]["delivery"] == "sent"


def test_a_failing_gateway_does_not_break_checkout(client, monkeypatch):
    from app import config, sms

    monkeypatch.setattr(config, "SMS_PROVIDER", "africastalking")
    monkeypatch.setattr(config, "SMS_API_KEY", "test-key")
    monkeypatch.setattr(config, "SMS_SENDER_ID", "OGS")
    monkeypatch.setattr(config, "STORE_PHONE", "+2348030000000")
    monkeypatch.setattr(config, "AT_USERNAME", "sandbox")

    def down(text):
        raise RuntimeError("gateway timeout")

    monkeypatch.setattr(sms, "_deliver", down)
    order_id = place(client)

    assert order_id
    entries = stored()
    assert entries[0]["delivery"] == "failed"
    assert "gateway timeout" in entries[0]["deliveryError"]
