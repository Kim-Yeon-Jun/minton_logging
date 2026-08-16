package com.mintonlogging.wear.data.remote

import com.mintonlogging.wear.data.remote.dto.DeviceCodeRequest
import com.mintonlogging.wear.data.remote.dto.DeviceCodeResponse
import com.mintonlogging.wear.data.remote.dto.DeviceTokenRequest
import com.mintonlogging.wear.data.remote.dto.DeviceTokenResponse
import retrofit2.http.Body
import retrofit2.http.POST

/** backend/api/device.py 대응. 로그인 전(토큰 없이) 호출하는 엔드포인트들이다. */
interface DeviceApi {
    @POST("api/device/code")
    suspend fun createDeviceCode(@Body request: DeviceCodeRequest): DeviceCodeResponse

    @POST("api/device/token")
    suspend fun pollToken(@Body request: DeviceTokenRequest): DeviceTokenResponse
}
