package com.mintonlogging.wear.data.remote

import com.mintonlogging.wear.BuildConfig
import com.mintonlogging.wear.data.auth.TokenStore
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

/**
 * 백엔드(backend/main.py, prefix "/api")와 통신하는 Retrofit 인스턴스를 만든다.
 * base URL은 app/build.gradle.kts의 debug/release buildType에서 BuildConfig.API_BASE_URL로 설정한다.
 *
 * 저장된 토큰이 있으면 모든 요청에 Authorization 헤더를 자동으로 붙인다 — /api/device/code처럼
 * 토큰이 없는 시점에 호출하는 엔드포인트에도 걸리지만, 헤더가 없을 뿐이니 무해하다.
 */
object ApiClient {

    private val json = Json { ignoreUnknownKeys = true }

    fun create(tokenStore: TokenStore): Retrofit {
        val authInterceptor = Interceptor { chain ->
            val token = runBlocking { tokenStore.accessToken.firstOrNull() }
            val request = chain.request().newBuilder().apply {
                if (!token.isNullOrBlank()) {
                    addHeader("Authorization", "Bearer $token")
                }
            }.build()
            chain.proceed(request)
        }

        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .build()

        val contentType = "application/json".toMediaType()

        return Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()
    }
}
