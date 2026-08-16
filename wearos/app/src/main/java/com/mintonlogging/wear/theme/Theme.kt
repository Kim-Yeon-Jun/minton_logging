package com.mintonlogging.wear.theme

import androidx.compose.runtime.Composable
import androidx.wear.compose.material.Colors
import androidx.wear.compose.material.MaterialTheme

private val WearColorPalette = Colors(
    primary = MintonGreen,
    primaryVariant = MintonGreenDark,
    onPrimary = MintonBackground,
    background = MintonBackground,
    onBackground = MintonOnBackground
)

@Composable
fun MintonWearTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colors = WearColorPalette,
        content = content
    )
}
