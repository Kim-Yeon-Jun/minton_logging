package com.mintonlogging.wear.data.remote

import com.mintonlogging.wear.data.remote.dto.GameCreateRequest
import com.mintonlogging.wear.data.remote.dto.GameResponse
import com.mintonlogging.wear.data.remote.dto.GameStatusUpdateRequest
import com.mintonlogging.wear.data.remote.dto.GroupDetailResponse
import com.mintonlogging.wear.data.remote.dto.GroupResponse
import com.mintonlogging.wear.data.remote.dto.TeamScoreUpdateRequest
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * backend/api/groups.py, backend/api/games.py 대응.
 * 페어링으로 발급받은 JWT가 필요하므로, 이 인터페이스로 만든 Retrofit 클라이언트는
 * ApiClient.create()의 authInterceptor를 반드시 거쳐야 한다.
 */
interface GameApi {
    @GET("api/groups")
    suspend fun getGroups(): List<GroupResponse>

    @GET("api/groups/{groupKey}")
    suspend fun getGroupDetail(@Path("groupKey") groupKey: String): GroupDetailResponse

    @POST("api/games")
    suspend fun createGame(@Body request: GameCreateRequest): GameResponse

    @PATCH("api/games/{gameId}/status")
    suspend fun updateGameStatus(
        @Path("gameId") gameId: String,
        @Body request: GameStatusUpdateRequest
    ): GameResponse

    @PATCH("api/games/{gameId}/teams/{teamColor}/score")
    suspend fun updateTeamScore(
        @Path("gameId") gameId: String,
        @Path("teamColor") teamColor: String,
        @Body request: TeamScoreUpdateRequest
    ): GameResponse
}
