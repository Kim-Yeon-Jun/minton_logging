package com.mintonlogging.wear.group

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.wear.compose.material.Text

/**
 * TODO(다음 단계): GameApi.getGroups()로 내 그룹 목록을 불러와 하나를 고르고,
 * getGroupDetail()의 멤버 목록에서 참가자(단식 2명/복식 4명)를 선택한 뒤
 * scoring 화면으로 넘어가는 흐름을 구현한다. 지금은 골격 단계라 자리만 잡아둔다.
 */
@Composable
fun GroupSelectScreen() {
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("TODO: 그룹/참가자 선택 화면")
    }
}
