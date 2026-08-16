package com.mintonlogging.wear.data.remote.dto

import kotlinx.serialization.Serializable

// backend/api/groups.py, backend/api/games.py 의 Pydantic 스키마 중
// 워치 MVP(그룹 선택 -> 참가자 선택 -> 실시간 점수 기록)에 필요한 것만 대응한다.
// comment/like 등 워치에서 안 쓰는 필드는 그대로 두되(응답 파싱은 되어야 하므로) 쓰지 않는다.

@Serializable
data class GroupResponse(
    val group_key: String,
    val group_name: String,
    val description: String? = null,
    val owner_id: String? = null,
    val member_count: Int = 0,
    val created_at: String
)

@Serializable
data class GroupMemberResponse(
    val user_id: String,
    val username: String,
    val name: String? = null,
    val role: String,
    val joined_at: String
)

@Serializable
data class GroupDetailResponse(
    val group_key: String,
    val group_name: String,
    val description: String? = null,
    val owner_id: String? = null,
    val created_at: String,
    val members: List<GroupMemberResponse> = emptyList()
)

@Serializable
data class GameParticipantInput(
    val user_id: String,
    val team_color: String,
    val score: Int = 0
)

@Serializable
data class GameCreateRequest(
    val group_key: String,
    val game_type: String = "doubles",
    // 워치에서 만드는 경기는 항상 실시간 기록 시작이므로 기본값을 in_progress로 둔다.
    // (웹 클라이언트는 이 필드를 아예 안 보내면 백엔드 기본값인 finished가 적용된다.)
    val game_status: String = "in_progress",
    val court_number: Int? = null,
    val video_url: String? = null,
    val played_at: String? = null,
    val participants: List<GameParticipantInput>
)

@Serializable
data class GameParticipantResponse(
    val user_id: String,
    val username: String,
    val name: String? = null,
    val team_color: String,
    val score: Int,
    val is_winner: Boolean? = null
)

@Serializable
data class GameResponse(
    val game_id: String,
    val group_key: String,
    val game_type: String,
    val game_status: String,
    val court_number: Int? = null,
    val video_url: String? = null,
    val played_at: String,
    val created_at: String,
    val deleted_at: String? = null,
    val participants: List<GameParticipantResponse> = emptyList(),
    val comment_count: Int = 0,
    val like_count: Int = 0,
    val liked_by_me: Boolean = false
)

@Serializable
data class GameStatusUpdateRequest(
    val game_status: String
)

@Serializable
data class TeamScoreUpdateRequest(
    val score: Int
)
