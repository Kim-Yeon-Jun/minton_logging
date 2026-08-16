package com.mintonlogging.wear.data.auth

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "minton_wear_auth")

/**
 * 페어링으로 발급받은 JWT(access_token)를 기기에 보관한다.
 *
 * TODO: 골격 단계라 평문 DataStore를 쓴다. 실제 배포 전에는 androidx.security의
 * EncryptedFile/Tink 기반 저장으로 교체할 것.
 */
class TokenStore(context: Context) {

    private val dataStore = context.dataStore

    private object Keys {
        val ACCESS_TOKEN = stringPreferencesKey("access_token")
        val USER_ID = stringPreferencesKey("user_id")
        val USERNAME = stringPreferencesKey("username")
    }

    val accessToken: Flow<String?> = dataStore.data.map { it[Keys.ACCESS_TOKEN] }
    val username: Flow<String?> = dataStore.data.map { it[Keys.USERNAME] }

    suspend fun save(accessToken: String, userId: String, username: String) {
        dataStore.edit { prefs ->
            prefs[Keys.ACCESS_TOKEN] = accessToken
            prefs[Keys.USER_ID] = userId
            prefs[Keys.USERNAME] = username
        }
    }

    suspend fun clear() {
        dataStore.edit { it.clear() }
    }
}
