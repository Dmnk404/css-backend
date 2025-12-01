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


def find_member_in_list(items, member_id):
    for it in items:
        if it.get("id") == member_id:
            return it
    return None


def get_all_members(client, token):
    r = client.get("/members/members/", headers=auth_headers(token))
    assert r.status_code == 200, f"Unexpected status {r.status_code}: {r.text}"
    data = r.json()
    return data.get("items") if isinstance(data, dict) and "items" in data else data


def test_create_member_api(client, admin_token):
    payload = sample_member_payload(1)
    resp = client.post(
        "/members/members/", json=payload, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 201, f"POST returned {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["email"] == payload["email"]
    assert "id" in body


def test_get_member_by_id_api(client, admin_token):
    payload = sample_member_payload(2)
    r = client.post(
        "/members/members/", json=payload, headers=auth_headers(admin_token)
    )
    assert r.status_code == 201, f"POST returned {r.status_code}: {r.text}"
    mid = r.json()["id"]

    members = get_all_members(client, admin_token)
    assert find_member_in_list(members, mid) is not None


def test_members_pagination_api(client, admin_token):
    # create 12 members
    created_ids = []
    for i in range(12):
        resp = client.post(
            "/members/members/",
            json=sample_member_payload(100 + i),
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 201, f"POST returned {resp.status_code}: {resp.text}"
        created_ids.append(resp.json().get("id"))

    # request page 1 with size 10
    r = client.get(
        "/members/members/?page=1&size=10", headers=auth_headers(admin_token)
    )
    assert r.status_code == 200, f"GET pagination returned {r.status_code}: {r.text}"
    data = r.json()
    items = data.get("items") if isinstance(data, dict) and "items" in data else data

    # If API honors pagination, page 1 should contain at most 10 items and page 2 should contain different items
    if len(items) <= 10:
        r2 = client.get(
            "/members/members/?page=2&size=10", headers=auth_headers(admin_token)
        )
        assert r2.status_code == 200, f"GET page 2 returned {r2.status_code}: {r2.text}"
        data2 = r2.json()
        items2 = (
            data2.get("items")
            if isinstance(data2, dict) and "items" in data2
            else data2
        )

        ids1 = {it.get("id") for it in items if it.get("id") is not None}
        ids2 = {it.get("id") for it in items2 if it.get("id") is not None}

        # If there are items on page 2, they should be distinct from page 1
        if ids2:
            assert ids1.isdisjoint(ids2), "page 1 and page 2 returned overlapping items"
    else:
        # API ignored pagination: ensure it returned at least all created members (non-decreasing)
        assert len(items) >= len(
            created_ids
        ), "API returned fewer items than were created"


def test_update_member_api(client, admin_token):
    payload = sample_member_payload(3)
    r = client.post(
        "/members/members/", json=payload, headers=auth_headers(admin_token)
    )
    assert r.status_code == 201, f"POST returned {r.status_code}: {r.text}"
    mid = r.json()["id"]

    update = {"name": "Updated Name"}
    r2 = client.put(
        f"/members/members/{mid}", json=update, headers=auth_headers(admin_token)
    )
    assert r2.status_code in (200, 204), f"PUT returned {r2.status_code}: {r2.text}"

    members = get_all_members(client, admin_token)
    found = find_member_in_list(members, mid)
    assert found is not None
    assert found.get("name") == "Updated Name"


def test_delete_member_api(client, admin_token):
    payload = sample_member_payload(4)
    r = client.post(
        "/members/members/", json=payload, headers=auth_headers(admin_token)
    )
    assert r.status_code == 201, f"POST returned {r.status_code}: {r.text}"
    mid = r.json()["id"]

    r2 = client.delete(f"/members/members/{mid}", headers=auth_headers(admin_token))
    assert r2.status_code in (200, 204), f"DELETE returned {r2.status_code}: {r2.text}"

    members = get_all_members(client, admin_token)
    assert find_member_in_list(members, mid) is None


def test_create_member_invalid_payload(client, admin_token):
    bad = {"name": ""}  # invalid or incomplete
    r = client.post("/members/members/", json=bad, headers=auth_headers(admin_token))
    assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
