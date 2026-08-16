package de.johannesbenedict.ironmancoach.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val CoachBackground = Color(0xFF080D16)
val CoachSurface = Color(0xFF101A29)
val CoachPanel = Color(0xFF142437)
val CoachCyan = Color(0xFF70C9FF)
val CoachRed = Color(0xFFE94B64)
val CoachGold = Color(0xFFE6B760)
val CoachGreen = Color(0xFF6BDB91)
val CoachMuted = Color(0xFF93A3B8)

private val CoachColors = darkColorScheme(
    primary = CoachCyan,
    secondary = CoachGold,
    tertiary = CoachRed,
    background = CoachBackground,
    surface = CoachSurface,
    surfaceVariant = CoachPanel,
    onPrimary = CoachBackground,
    onBackground = Color(0xFFE9F2FA),
    onSurface = Color(0xFFE9F2FA),
    outline = Color(0xFF34485F),
    error = CoachRed,
)

@Composable
fun IronmanCoachTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = CoachColors, content = content)
}
