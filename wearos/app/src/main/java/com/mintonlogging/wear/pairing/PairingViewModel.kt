package com.mintonlogging.wear.pairing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.mintonlogging.wear.data.auth.TokenStore
import com.mintonlogging.wear.data.remote.DeviceApi
import com.mintonlogging.wear.data.remote.dto.DeviceCodeRequest
import com.mintonlogging.wear.data.remote.dto.DeviceTokenRequest
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch
import retrofit2.HttpException

sealed interface PairingUiState {
    data object CheckingSavedSession : PairingUiState
    data object Loading : PairingUiState
    data class ShowingCode(val userCode: String) : PairingUiState
    data object Paired : PairingUiState
    data class Error(val message: String) : PairingUiState
}

private const val POLL_INTERVAL_MS = 3000L

/**
 * backend/api/device.py 의 OAuth Device Authorization Grant 흐름을 구현한다:
 * 1) createDeviceCode 로 (device_code, user_code) 발급
 * 2) 화면에 user_code 를 띄움 -> 사용자가 폰/웹에서 입력해 승인
 * 3) pollToken 으로 device_code 폴링, 승인되면 JWT 를 받아 TokenStore 에 저장
 */
class PairingViewModel(
    private val deviceApi: DeviceApi,
    private val tokenStore: TokenStore
) : ViewModel() {

    private val _uiState = MutableStateFlow<PairingUiState>(PairingUiState.CheckingSavedSession)
    val uiState: StateFlow<PairingUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val existingToken = tokenStore.accessToken.firstOrNull()
            if (!existingToken.isNullOrBlank()) {
                _uiState.value = PairingUiState.Paired
            } else {
                startPairing()
            }
        }
    }

    fun retry() {
        viewModelScope.launch { startPairing() }
    }

    private suspend fun startPairing() {
        _uiState.value = PairingUiState.Loading
        try {
            val issued = deviceApi.createDeviceCode(DeviceCodeRequest(device_name = "Wear OS"))
            _uiState.value = PairingUiState.ShowingCode(issued.user_code)
            pollForApproval(issued.device_code)
        } catch (e: Exception) {
            _uiState.value = PairingUiState.Error(e.message ?: "페어링 코드 발급에 실패했습니다.")
        }
    }

    private suspend fun pollForApproval(deviceCode: String) {
        while (true) {
            delay(POLL_INTERVAL_MS)
            try {
                val token = deviceApi.pollToken(DeviceTokenRequest(deviceCode))
                tokenStore.save(token.access_token, token.id, token.username)
                _uiState.value = PairingUiState.Paired
                return
            } catch (e: HttpException) {
                // 400 authorization_pending: 계속 폴링.
                // 400 expired_code(코드 만료/이미 사용됨): 처음부터 다시 시작.
                // TODO: 지금은 에러 바디를 문자열로만 확인한다 - 정식 에러 응답 DTO로 파싱하도록 개선할 것.
                val body = e.response()?.errorBody()?.string().orEmpty()
                if (e.code() == 400 && body.contains("expired_code")) {
                    startPairing()
                    return
                }
                if (e.code() != 400) {
                    _uiState.value = PairingUiState.Error("페어링 확인 중 오류가 발생했습니다.")
                    return
                }
                // authorization_pending -> 루프 계속
            }
        }
    }
}
