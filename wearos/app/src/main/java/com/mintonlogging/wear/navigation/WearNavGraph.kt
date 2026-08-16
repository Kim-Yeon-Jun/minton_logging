package com.mintonlogging.wear.navigation

import androidx.compose.runtime.Composable
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController
import com.mintonlogging.wear.group.GroupSelectScreen
import com.mintonlogging.wear.pairing.PairingScreen
import com.mintonlogging.wear.pairing.PairingViewModel

object WearDestinations {
    const val PAIRING = "pairing"
    const val GROUP_SELECT = "group_select"
}

/**
 * 항상 PAIRING에서 시작한다 — PairingViewModel이 저장된 토큰 유무를 먼저 확인해서
 * 이미 페어링된 상태면 즉시 Paired 상태로 전환되어 GROUP_SELECT로 넘어간다
 * (MainActivity에서 매번 블로킹 호출로 토큰을 미리 확인할 필요가 없게 하기 위함).
 */
@Composable
fun WearNavGraph(pairingViewModel: PairingViewModel) {
    val navController = rememberSwipeDismissableNavController()

    SwipeDismissableNavHost(
        navController = navController,
        startDestination = WearDestinations.PAIRING
    ) {
        composable(WearDestinations.PAIRING) {
            PairingScreen(
                viewModel = pairingViewModel,
                onPaired = {
                    navController.navigate(WearDestinations.GROUP_SELECT) {
                        popUpTo(WearDestinations.PAIRING) { inclusive = true }
                    }
                }
            )
        }
        composable(WearDestinations.GROUP_SELECT) {
            GroupSelectScreen()
        }
    }
}
