package com.mintonlogging.wear

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.CreationExtras
import com.mintonlogging.wear.data.auth.TokenStore
import com.mintonlogging.wear.data.remote.ApiClient
import com.mintonlogging.wear.data.remote.DeviceApi
import com.mintonlogging.wear.navigation.WearNavGraph
import com.mintonlogging.wear.pairing.PairingViewModel
import com.mintonlogging.wear.theme.MintonWearTheme

class MainActivity : ComponentActivity() {

    // TODO(다음 단계): 화면이 늘어나면 Hilt 등 DI로 옮긴다. 지금은 골격이라 손으로 조립한다.
    private val tokenStore by lazy { TokenStore(applicationContext) }
    private val deviceApi by lazy { ApiClient.create(tokenStore).create(DeviceApi::class.java) }

    private val pairingViewModel by viewModels<PairingViewModel>(
        factoryProducer = {
            object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>, extras: CreationExtras): T {
                    return PairingViewModel(deviceApi, tokenStore) as T
                }
            }
        }
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MintonWearTheme {
                WearNavGraph(pairingViewModel = pairingViewModel)
            }
        }
    }
}
