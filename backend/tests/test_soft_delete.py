def _create_group_and_game(client, register_user):
    owner = register_user("owner")
    member = register_user("member")

    group_resp = client.post(
        "/api/groups",
        headers=owner["headers"],
        json={"group_name": "소프트삭제 테스트", "description": None},
    )
    group_key = group_resp.json()["group_key"]
    client.post(f"/api/groups/{group_key}/join", headers=member["headers"], json={})

    game_resp = client.post(
        "/api/games",
        headers=owner["headers"],
        json={
            "group_key": group_key,
            "game_type": "singles",
            "participants": [
                {"user_id": owner["id"], "team_color": "A", "score": 21},
                {"user_id": member["id"], "team_color": "B", "score": 10},
            ],
        },
    )
    return owner, member, group_key, game_resp.json()["game_id"]


def test_soft_delete_moves_game_to_trash(client, register_user):
    owner, member, group_key, game_id = _create_group_and_game(client, register_user)

    assert client.delete(f"/api/games/{game_id}", headers=member["headers"]).status_code == 200

    active = client.get(f"/api/games/group/{group_key}", headers=owner["headers"]).json()
    trash = client.get(f"/api/games/group/{group_key}/trash", headers=owner["headers"]).json()

    assert active["total"] == 0
    assert trash["total"] == 1
    assert trash["items"][0]["game_id"] == game_id


def test_double_soft_delete_rejected(client, register_user):
    owner, member, group_key, game_id = _create_group_and_game(client, register_user)

    client.delete(f"/api/games/{game_id}", headers=owner["headers"])
    resp = client.delete(f"/api/games/{game_id}", headers=member["headers"])

    assert resp.status_code == 400


def test_edit_blocked_while_soft_deleted(client, register_user):
    owner, member, group_key, game_id = _create_group_and_game(client, register_user)
    client.delete(f"/api/games/{game_id}", headers=owner["headers"])

    resp = client.put(
        f"/api/games/{game_id}",
        headers=member["headers"],
        json={
            "group_key": group_key,
            "game_type": "singles",
            "participants": [
                {"user_id": owner["id"], "team_color": "A", "score": 1},
                {"user_id": member["id"], "team_color": "B", "score": 2},
            ],
        },
    )
    assert resp.status_code == 400


def test_restore_moves_game_back_to_active(client, register_user):
    owner, member, group_key, game_id = _create_group_and_game(client, register_user)
    client.delete(f"/api/games/{game_id}", headers=member["headers"])

    resp = client.post(f"/api/games/{game_id}/restore", headers=owner["headers"])
    assert resp.status_code == 200

    active = client.get(f"/api/games/group/{group_key}", headers=owner["headers"]).json()
    trash = client.get(f"/api/games/group/{group_key}/trash", headers=owner["headers"]).json()

    assert active["total"] == 1
    assert trash["total"] == 0


def test_permanent_delete_requires_soft_delete_first(client, register_user):
    owner, member, group_key, game_id = _create_group_and_game(client, register_user)

    resp = client.delete(f"/api/games/{game_id}/permanent", headers=owner["headers"])
    assert resp.status_code == 400


def test_permanent_delete_removes_row_completely(client, register_user, db_session):
    from models.game import Game

    owner, member, group_key, game_id = _create_group_and_game(client, register_user)
    client.delete(f"/api/games/{game_id}", headers=owner["headers"])

    resp = client.delete(f"/api/games/{game_id}/permanent", headers=member["headers"])
    assert resp.status_code == 200

    assert db_session.query(Game).filter(Game.game_id == game_id).first() is None

    trash = client.get(f"/api/games/group/{group_key}/trash", headers=owner["headers"]).json()
    assert trash["total"] == 0
