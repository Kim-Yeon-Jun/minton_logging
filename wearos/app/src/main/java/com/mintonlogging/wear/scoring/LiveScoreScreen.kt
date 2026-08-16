package com.mintonlogging.wear.scoring

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.wear.compose.material.Text

/**
 * TODO(다음 단계): 참가자 선택 후 GameApi.createGame()으로 game_status="in_progress" 경기를
 * 시작하고, 팀별 +/- 버튼으로 GameApi.updateTeamScore()를 호출해 절대 점수를 갱신한다.
 * 종료 시 GameApi.updateGameStatus()로 finished 처리한다. 지금은 골격 단계라 자리만 잡아둔다.
 */
@Composable
fun LiveScoreScreen() {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("TODO: 실시간 점수 기록 화면")
    }
}
