def _create_group(client, owner):
    resp = client.post(
        "/api/groups",
        headers=owner["headers"],
        json={"group_name": "테스트 그룹", "description": None},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["group_key"]


def _join_group(client, group_key, user):
    resp = client.post(f"/api/groups/{group_key}/join", headers=user["headers"], json={})
    assert resp.status_code == 200, resp.text


def _create_game(client, group_key, owner, member):
    payload = {
        "group_key": group_key,
        "game_type": "singles",
        "participants": [
            {"user_id": owner["id"], "team_color": "A", "score": 21},
            {"user_id": member["id"], "team_color": "B", "score": 10},
        ],
    }
    resp = client.post("/api/games", headers=owner["headers"], json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()["game_id"]


def test_non_member_cannot_create_game(client, register_user):
    owner = register_user("owner")
    outsider = register_user("outsider")
    group_key = _create_group(client, owner)

    payload = {
        "group_key": group_key,
        "game_type": "singles",
        "participants": [
            {"user_id": owner["id"], "team_color": "A", "score": 21},
            {"user_id": outsider["id"], "team_color": "B", "score": 10},
        ],
    }
    resp = client.post("/api/games", headers=outsider["headers"], json=payload)
    assert resp.status_code == 403


def test_member_can_edit_game_created_by_someone_else(client, register_user):
    owner = register_user("owner")
    member = register_user("member")
    group_key = _create_group(client, owner)
    _join_group(client, group_key, member)
    game_id = _create_game(client, group_key, owner, member)

    resp = client.put(
        f"/api/games/{game_id}",
        headers=member["headers"],
        json={
            "group_key": group_key,
            "game_type": "singles",
            "participants": [
                {"user_id": owner["id"], "team_color": "A", "score": 15},
                {"user_id": member["id"], "team_color": "B", "score": 21},
            ],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["participants"][0]["score"] == 15


def test_non_member_cannot_edit_delete_restore_or_permanently_delete(client, register_user):
    owner = register_user("owner")
    member = register_user("member")
    outsider = register_user("outsider")
    group_key = _create_group(client, owner)
    _join_group(client, group_key, member)
    game_id = _create_game(client, group_key, owner, member)

    edit_payload = {
        "group_key": group_key,
        "game_type": "singles",
        "participants": [
            {"user_id": owner["id"], "team_color": "A", "score": 1},
            {"user_id": member["id"], "team_color": "B", "score": 2},
        ],
    }
    assert client.put(f"/api/games/{game_id}", headers=outsider["headers"], json=edit_payload).status_code == 403
    assert client.delete(f"/api/games/{game_id}", headers=outsider["headers"]).status_code == 403

    # 그룹원이 소프트 삭제한 뒤에도 외부인은 복구/영구삭제를 할 수 없어야 한다.
    assert client.delete(f"/api/games/{game_id}", headers=owner["headers"]).status_code == 200
    assert client.post(f"/api/games/{game_id}/restore", headers=outsider["headers"]).status_code == 403
    assert client.delete(f"/api/games/{game_id}/permanent", headers=outsider["headers"]).status_code == 403


def test_group_scoped_endpoints_require_membership(client, register_user):
    owner = register_user("owner")
    outsider = register_user("outsider")
    group_key = _create_group(client, owner)

    assert client.get(f"/api/games/group/{group_key}", headers=outsider["headers"]).status_code == 403
    assert client.get(f"/api/groups/{group_key}/stats", headers=outsider["headers"]).status_code == 403


def test_create_group_uses_token_identity_not_body(client, register_user):
    user = register_user("owner")
    resp = client.post(
        "/api/groups",
        headers=user["headers"],
        json={"group_name": "신원위조테스트", "description": None},
    )
    assert resp.status_code == 201
    assert resp.json()["owner_id"] == user["id"]
