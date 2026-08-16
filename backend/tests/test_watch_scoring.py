def _create_group_and_members(client, register_user):
    owner = register_user("owner")
    member = register_user("member")
    outsider = register_user("outsider")

    group_resp = client.post(
        "/api/groups",
        headers=owner["headers"],
        json={"group_name": "워치 점수기록 테스트", "description": None},
    )
    group_key = group_resp.json()["group_key"]
    client.post(f"/api/groups/{group_key}/join", headers=member["headers"], json={})
    return owner, member, outsider, group_key


def _start_live_game(client, owner, member, group_key):
    resp = client.post(
        "/api/games",
        headers=owner["headers"],
        json={
            "group_key": group_key,
            "game_type": "singles",
            "game_status": "in_progress",
            "participants": [
                {"user_id": owner["id"], "team_color": "A", "score": 0},
                {"user_id": member["id"], "team_color": "B", "score": 0},
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_game_with_explicit_status(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)
    assert game["game_status"] == "in_progress"


def test_create_game_defaults_to_finished_for_existing_clients(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    resp = client.post(
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
    assert resp.status_code == 201
    assert resp.json()["game_status"] == "finished"


def test_create_game_rejects_invalid_status(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    resp = client.post(
        "/api/games",
        headers=owner["headers"],
        json={
            "group_key": group_key,
            "game_type": "singles",
            "game_status": "not_a_real_status",
            "participants": [
                {"user_id": owner["id"], "team_color": "A", "score": 0},
                {"user_id": member["id"], "team_color": "B", "score": 0},
            ],
        },
    )
    assert resp.status_code == 400


def test_update_game_status(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)

    resp = client.patch(
        f"/api/games/{game['game_id']}/status",
        headers=member["headers"],
        json={"game_status": "finished"},
    )
    assert resp.status_code == 200
    assert resp.json()["game_status"] == "finished"

    invalid = client.patch(
        f"/api/games/{game['game_id']}/status",
        headers=member["headers"],
        json={"game_status": "bogus"},
    )
    assert invalid.status_code == 400

    forbidden = client.patch(
        f"/api/games/{game['game_id']}/status",
        headers=outsider["headers"],
        json={"game_status": "finished"},
    )
    assert forbidden.status_code == 403


def test_update_team_score_recomputes_winner(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)
    game_id = game["game_id"]

    resp = client.patch(
        f"/api/games/{game_id}/teams/A/score",
        headers=owner["headers"],
        json={"score": 21},
    )
    assert resp.status_code == 200
    body = resp.json()
    team_a = next(p for p in body["participants"] if p["team_color"] == "A")
    team_b = next(p for p in body["participants"] if p["team_color"] == "B")
    assert team_a["score"] == 21
    assert team_a["is_winner"] is True
    assert team_b["is_winner"] is False

    # 점수 정정: B팀이 역전하면 승자도 다시 계산되어야 한다.
    resp2 = client.patch(
        f"/api/games/{game_id}/teams/B/score",
        headers=member["headers"],
        json={"score": 25},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    team_a2 = next(p for p in body2["participants"] if p["team_color"] == "A")
    team_b2 = next(p for p in body2["participants"] if p["team_color"] == "B")
    assert team_b2["score"] == 25
    assert team_b2["is_winner"] is True
    assert team_a2["is_winner"] is False


def test_update_team_score_rejects_negative(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)

    resp = client.patch(
        f"/api/games/{game['game_id']}/teams/A/score",
        headers=owner["headers"],
        json={"score": -1},
    )
    assert resp.status_code == 422


def test_update_team_score_rejects_unknown_team(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)

    resp = client.patch(
        f"/api/games/{game['game_id']}/teams/C/score",
        headers=owner["headers"],
        json={"score": 5},
    )
    assert resp.status_code == 404


def test_update_team_score_requires_membership(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)

    resp = client.patch(
        f"/api/games/{game['game_id']}/teams/A/score",
        headers=outsider["headers"],
        json={"score": 5},
    )
    assert resp.status_code == 403


def test_update_team_score_blocked_when_soft_deleted(client, register_user):
    owner, member, outsider, group_key = _create_group_and_members(client, register_user)
    game = _start_live_game(client, owner, member, group_key)
    game_id = game["game_id"]

    assert client.delete(f"/api/games/{game_id}", headers=owner["headers"]).status_code == 200

    resp = client.patch(
        f"/api/games/{game_id}/teams/A/score",
        headers=owner["headers"],
        json={"score": 5},
    )
    assert resp.status_code == 400
