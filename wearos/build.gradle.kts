// 루트 프로젝트에는 플러그인만 선언(apply false)하고, 실제 적용은 app/build.gradle.kts에서 한다.
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.kotlin.serialization) apply false
}
