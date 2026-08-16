package com.mintonlogging.wear.pairing

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.wear.compose.material.Button
import androidx.wear.compose.material.CircularProgressIndicator
import androidx.wear.compose.material.MaterialTheme
import androidx.wear.compose.material.Text

@Composable
fun PairingScreen(viewModel: PairingViewModel, onPaired: () -> Unit) {
    val state by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        when (val current = state) {
            is PairingUiState.CheckingSavedSession,
            is PairingUiState.Loading -> {
                CircularProgressIndicator()
            }

            is PairingUiState.ShowingCode -> {
                Text(text = "이 코드를 폰/웹에서 입력하세요", textAlign = TextAlign.Center)
                Text(
                    text = current.userCode,
                    style = MaterialTheme.typography.title1,
                    textAlign = TextAlign.Center
                )
            }

            is PairingUiState.Paired -> {
                // 컴포지션 도중이 아니라 딱 한 번만 navigate 하도록 LaunchedEffect로 감싼다.
                LaunchedEffect(Unit) { onPaired() }
                Text(text = "연결되었습니다!", textAlign = TextAlign.Center)
            }

            is PairingUiState.Error -> {
                Text(text = current.message, textAlign = TextAlign.Center)
                Button(onClick = { viewModel.retry() }) {
                    Text("다시 시도")
                }
            }
        }
    }
}
