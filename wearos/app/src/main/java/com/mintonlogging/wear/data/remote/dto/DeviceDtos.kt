package com.mintonlogging.wear.data.remote.dto

import kotlinx.serialization.Serializable

// backend/api/device.py 의 Pydantic 스키마와 1:1로 대응한다.

@Serializable
data class DeviceCodeRequest(
    val device_name: String? = null
)

@Serializable
data class DeviceCodeResponse(
    val device_code: String,
    val user_code: String,
    val expires_in: Int
)

@Serializable
data class DeviceTokenRequest(
    val device_code: String
)

@Serializable
data class DeviceTokenResponse(
    val access_token: String,
    val token_type: String = "bearer",
    val id: String,
    val username: String,
    val name: String? = null,
    val group_key: String? = null
)
