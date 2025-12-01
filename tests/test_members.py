def sample_member_payload(index: int = 0) -> dict:
    return {
        "name": f"Member {index}",
        "birth_date": "1990-01-01",
        "address": f"Street {index} 1",
        "city": "Berlin",
        "postal_code": "10115",
        "email": f"member{index}@example.com",
    }


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_fixtures_are_available(admin_token, member_token, existing_member_id):
    # Basic assertions that fixtures produce usable artifacts
    assert isinstance(admin_token, str) and len(admin_token) > 0
    assert isinstance(member_token, str) and len(member_token) > 0
    assert isinstance(existing_member_id, int) and existing_member_id > 0


def test_create_and_list_member(client, admin_token):
    # create a member and ensure it appears in the listing
    payload = sample_member_payload(999)
    resp = client.post(
        "/members/members/", json=payload, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 201, f"POST returned {resp.status_code}: {resp.text}"
    created = resp.json()
    # list members and look for created id
    r = client.get("/members/members/", headers=auth_headers(admin_token))
    assert r.status_code == 200
    data = r.json()
    items = data.get("items") if isinstance(data, dict) and "items" in data else data
    assert any(it.get("id") == created.get("id") for it in items)
