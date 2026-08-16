package de.johannesbenedict.ironmancoach.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import de.johannesbenedict.ironmancoach.data.Activity
import de.johannesbenedict.ironmancoach.data.CheckinRequest
import de.johannesbenedict.ironmancoach.data.DailyMetric
import de.johannesbenedict.ironmancoach.data.PlannedWorkout
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

private enum class AppTab(val label: String, val icon: ImageVector) {
    DASHBOARD("Status", Icons.Default.Home),
    PLAN("Plan", Icons.Default.Star),
    CHECKIN("Check-in", Icons.Default.Check),
    CHAT("Coach", Icons.Default.AccountCircle),
    SETTINGS("Server", Icons.Default.Settings),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CoachApp(viewModel: CoachViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab by rememberSaveable { mutableStateOf(AppTab.DASHBOARD) }

    LaunchedEffect(state.connection) {
        if (state.connection == ConnectionStatus.NOT_CONFIGURED) tab = AppTab.SETTINGS
    }

    if (state.error != null) {
        AlertDialog(
            onDismissRequest = viewModel::clearError,
            confirmButton = { Button(onClick = viewModel::clearError) { Text("OK") } },
            title = { Text("Ironman Coach") },
            text = { Text(state.error.orEmpty()) },
        )
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = CoachBackground,
        topBar = {
            TopAppBar(
                modifier = Modifier.statusBarsPadding(),
                colors = TopAppBarDefaults.topAppBarColors(containerColor = CoachSurface),
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            Modifier.size(12.dp).background(connectionColor(state.connection), CircleShape),
                        )
                        Spacer(Modifier.width(10.dp))
                        Column {
                            Text("IRONMAN COACH", fontWeight = FontWeight.Black)
                            Text(
                                connectionLabel(state.connection),
                                color = CoachMuted,
                                style = MaterialTheme.typography.labelSmall,
                                fontFamily = FontFamily.Monospace,
                            )
                        }
                    }
                },
                actions = {
                    if (state.connection == ConnectionStatus.ONLINE) {
                        IconButton(onClick = viewModel::connectAndRefresh, enabled = !state.loading) {
                            if (state.loading) CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
                            else Icon(Icons.Default.Refresh, contentDescription = "Aktualisieren")
                        }
                    }
                },
            )
        },
        bottomBar = {
            NavigationBar(
                modifier = Modifier.navigationBarsPadding(),
                containerColor = CoachSurface,
            ) {
                AppTab.entries.forEach { destination ->
                    NavigationBarItem(
                        selected = tab == destination,
                        onClick = { tab = destination },
                        icon = { Icon(destination.icon, contentDescription = destination.label) },
                        label = { Text(destination.label, maxLines = 1) },
                    )
                }
            }
        },
    ) { insets ->
        Box(Modifier.fillMaxSize().padding(insets)) {
            when (tab) {
                AppTab.DASHBOARD -> DashboardScreen(state, viewModel::syncGarmin)
                AppTab.PLAN -> PlanScreen(state)
                AppTab.CHECKIN -> CheckinScreen(state, viewModel::submitCheckin)
                AppTab.CHAT -> ChatScreen(state, viewModel::sendMessage)
                AppTab.SETTINGS -> SettingsScreen(state, viewModel::saveSettings, viewModel::connectAndRefresh)
            }
        }
    }
}

@Composable
private fun DashboardScreen(state: CoachUiState, sync: () -> Unit) {
    val latest = state.metrics.lastOrNull()
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item { ScreenHeading("Telemetrie", "Dein aktueller Trainingszustand") }
        if (state.connection != ConnectionStatus.ONLINE) {
            item { SetupHint() }
        } else {
            item {
                MetricsGrid(latest)
            }
            item {
                Card(colors = CardDefaults.cardColors(containerColor = CoachPanel)) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Performance", color = CoachGold, fontWeight = FontWeight.Bold)
                        Text("CTL ${latest?.ctl.format()}  ·  ATL ${latest?.atl.format()}  ·  TSB ${latest?.tsb.format()}")
                        Text(
                            "Stand ${latest?.date ?: "–"}. Detailkurven bleiben in der Desktop-App verfügbar.",
                            color = CoachMuted,
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
            }
            item {
                Button(onClick = sync, enabled = !state.syncing, modifier = Modifier.fillMaxWidth()) {
                    if (state.syncing) CircularProgressIndicator(Modifier.size(18.dp), strokeWidth = 2.dp)
                    else Icon(Icons.Default.Refresh, null)
                    Spacer(Modifier.width(8.dp))
                    Text(if (state.syncing) "Garmin-Sync läuft…" else "Garmin jetzt synchronisieren")
                }
            }
            if (state.goals.isNotEmpty()) {
                item { SectionTitle("Ziele") }
                items(state.goals.take(3)) { goal ->
                    DataCard(goal.title, listOfNotNull(goal.eventDate, goal.targetMetric, goal.sport))
                }
            }
        }
    }
}

@Composable
private fun MetricsGrid(metric: DailyMetric?) {
    BoxWithConstraints {
        val values = listOf(
            Triple("Readiness", metric?.trainingReadiness?.toString() ?: "–", CoachGold),
            Triple("Body Battery", metric?.bodyBattery?.toString() ?: "–", CoachGreen),
            Triple("HRV", metric?.hrv.format(" ms"), CoachCyan),
            Triple("Ruhepuls", metric?.rhr?.let { "$it bpm" } ?: "–", CoachRed),
        )
        if (maxWidth >= 600.dp) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                values.forEach { (label, value, color) -> MetricCard(label, value, color, Modifier.weight(1f)) }
            }
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                values.chunked(2).forEach { row ->
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        row.forEach { (label, value, color) -> MetricCard(label, value, color, Modifier.weight(1f)) }
                    }
                }
            }
        }
    }
}

@Composable
private fun MetricCard(label: String, value: String, color: Color, modifier: Modifier = Modifier) {
    Card(modifier, colors = CardDefaults.cardColors(containerColor = CoachPanel)) {
        Column(Modifier.padding(14.dp)) {
            Text(label.uppercase(), color = CoachMuted, style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace)
            Text(value, color = color, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun PlanScreen(state: CoachUiState) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item { ScreenHeading("Trainingsplan", "Geplante und absolvierte Einheiten") }
        if (state.connection != ConnectionStatus.ONLINE) item { SetupHint() }
        else {
            item { SectionTitle("Geplant") }
            if (state.workouts.isEmpty()) item { EmptyCard("Noch keine geplanten Einheiten.") }
            items(state.workouts, key = { "workout-${it.id}" }) { WorkoutCard(it) }
            item { SectionTitle("Zuletzt absolviert") }
            if (state.activities.isEmpty()) item { EmptyCard("Noch keine Garmin-Aktivitäten.") }
            items(state.activities.asReversed().take(20), key = { "activity-${it.id}" }) { ActivityCard(it) }
        }
    }
}

@Composable
private fun WorkoutCard(workout: PlannedWorkout) {
    val info = listOfNotNull(
        workout.sportLabel(), workout.durationMin?.let { "$it min" },
        workout.distanceKm?.let { "%.1f km".format(it) }, workout.targetZone,
    )
    DataCard(workout.title ?: workout.sportLabel(), listOf(workout.date) + info, workout.content)
}

@Composable
private fun ActivityCard(activity: Activity) {
    val info = listOfNotNull(
        activity.sport.replaceFirstChar { it.uppercase() }, activity.durationMin?.let { "${it.roundToInt()} min" },
        activity.distanceKm?.let { "%.1f km".format(it) }, activity.averageHeartRate?.let { "$it bpm" },
    )
    DataCard(activity.title ?: activity.sport, listOf(activity.date) + info)
}

@Composable
private fun CheckinScreen(state: CoachUiState, submit: (CheckinRequest) -> Unit) {
    var soreness by rememberSaveable { mutableFloatStateOf(3f) }
    var pain by rememberSaveable { mutableFloatStateOf(0f) }
    var motivation by rememberSaveable { mutableFloatStateOf(3f) }
    var energy by rememberSaveable { mutableFloatStateOf(3f) }
    var stress by rememberSaveable { mutableFloatStateOf(3f) }
    var painLocation by rememberSaveable { mutableStateOf("") }
    var minutes by rememberSaveable { mutableStateOf("") }
    var notes by rememberSaveable { mutableStateOf("") }
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        ScreenHeading("Tages-Check-in", LocalDate.now().format(DateTimeFormatter.ofPattern("dd.MM.yyyy")))
        ScaleInput("Muskelkater", soreness, 1f..5f) { soreness = it }
        ScaleInput("Schmerz", pain, 0f..10f) { pain = it }
        if (pain > 0) OutlinedTextField(painLocation, { painLocation = it }, label = { Text("Wo?") }, modifier = Modifier.fillMaxWidth())
        ScaleInput("Motivation", motivation, 1f..5f) { motivation = it }
        ScaleInput("Mentale Energie", energy, 1f..5f) { energy = it }
        ScaleInput("Alltagsstress", stress, 1f..5f) { stress = it }
        OutlinedTextField(
            minutes, { minutes = it.filter(Char::isDigit) }, label = { Text("Verfügbare Trainingszeit (Minuten)") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(notes, { notes = it }, label = { Text("Notizen") }, minLines = 3, modifier = Modifier.fillMaxWidth())
        Button(
            onClick = {
                submit(
                    CheckinRequest(
                        soreness = soreness.roundToInt(), painLocation = painLocation.ifBlank { null },
                        painLevel = pain.roundToInt(), motivation = motivation.roundToInt(),
                        mentalEnergy = energy.roundToInt(), availableTime = minutes.toIntOrNull(),
                        lifeStress = stress.roundToInt(), notes = notes.ifBlank { null },
                    ),
                )
            },
            enabled = state.connection == ConnectionStatus.ONLINE,
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Check-in speichern") }
        if (state.checkinSaved) Text("✓ Gespeichert", color = CoachGreen)
    }
}

@Composable
private fun ScaleInput(label: String, value: Float, range: ClosedFloatingPointRange<Float>, update: (Float) -> Unit) {
    Card(colors = CardDefaults.cardColors(containerColor = CoachPanel)) {
        Column(Modifier.padding(horizontal = 14.dp, vertical = 8.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(label)
                Text(value.roundToInt().toString(), color = CoachCyan, fontWeight = FontWeight.Bold)
            }
            Slider(value, update, valueRange = range, steps = (range.endInclusive - range.start).roundToInt() - 1)
        }
    }
}

@Composable
private fun ChatScreen(state: CoachUiState, send: (String) -> Unit) {
    var input by rememberSaveable { mutableStateOf("") }
    val listState = rememberLazyListState()
    LaunchedEffect(state.messages.size, state.messages.lastOrNull()?.content) {
        if (state.messages.isNotEmpty()) listState.animateScrollToItem(state.messages.lastIndex)
    }
    Column(Modifier.fillMaxSize().imePadding()) {
        LazyColumn(
            state = listState,
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            if (state.messages.isEmpty()) item { EmptyCard("Frag deinen Coach zum Training, zur Erholung oder zum Wochenplan.") }
            items(state.messages) { message -> MessageBubble(message.role == "user", message.content) }
        }
        HorizontalDivider()
        Row(Modifier.padding(10.dp), verticalAlignment = Alignment.Bottom) {
            OutlinedTextField(
                input, { input = it }, label = { Text("Nachricht an den Coach") },
                modifier = Modifier.weight(1f), maxLines = 5, enabled = state.connection == ConnectionStatus.ONLINE && !state.sending,
            )
            IconButton(
                onClick = { send(input); input = "" },
                enabled = input.isNotBlank() && state.connection == ConnectionStatus.ONLINE && !state.sending,
            ) {
                if (state.sending) CircularProgressIndicator(Modifier.size(22.dp), strokeWidth = 2.dp)
                else Icon(Icons.AutoMirrored.Filled.Send, "Senden", tint = CoachCyan)
            }
        }
    }
}

@Composable
private fun MessageBubble(isUser: Boolean, content: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start) {
        Card(
            modifier = Modifier.fillMaxWidth(0.88f),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(containerColor = if (isUser) CoachCyan.copy(alpha = .18f) else CoachPanel),
        ) {
            Text(content.ifBlank { "…" }, Modifier.padding(12.dp))
        }
    }
}

@Composable
private fun SettingsScreen(state: CoachUiState, save: (String, String) -> Unit, retry: () -> Unit) {
    var url by remember(state.settings.baseUrl) { mutableStateOf(state.settings.baseUrl) }
    var token by remember(state.settings.token) { mutableStateOf(state.settings.token) }
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        ScreenHeading("Server verbinden", "Die KI und Garmin-Daten bleiben auf deinem Mac-Backend")
        Card(colors = CardDefaults.cardColors(containerColor = CoachPanel)) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("So funktioniert es", color = CoachGold, fontWeight = FontWeight.Bold)
                Text("1. Mobile-Server auf dem Mac starten\n2. Mac-IP und Port 8766 eintragen\n3. Denselben Zugriffstoken einfügen")
                Text("Beispiel: http://192.168.178.20:8766", color = CoachCyan, fontFamily = FontFamily.Monospace)
                Text("HTTP nur im vertrauenswürdigen Heimnetz verwenden. Für Fernzugriff ist HTTPS mit zusätzlichem Netzwerkschutz nötig.", color = CoachMuted, style = MaterialTheme.typography.bodySmall)
            }
        }
        OutlinedTextField(url, { url = it }, label = { Text("Backend-Adresse") }, singleLine = true, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(
            token, { token = it }, label = { Text("Zugriffstoken") }, singleLine = true,
            visualTransformation = PasswordVisualTransformation(), modifier = Modifier.fillMaxWidth(),
        )
        Button(onClick = { save(url, token) }, enabled = url.isNotBlank(), modifier = Modifier.fillMaxWidth()) {
            Text("Speichern und verbinden")
        }
        OutlinedButton(onClick = retry, enabled = state.settings.isConfigured, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.Refresh, null)
            Spacer(Modifier.width(8.dp))
            Text("Verbindung erneut testen")
        }
        Text("Der Token wird mit Android Keystore verschlüsselt auf diesem Gerät gespeichert.", color = CoachMuted, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun ScreenHeading(title: String, subtitle: String) {
    Column {
        Text(title, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Black)
        Text(subtitle, color = CoachMuted)
    }
}

@Composable
private fun SectionTitle(title: String) {
    Text(title.uppercase(), color = CoachGold, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
}

@Composable
private fun DataCard(title: String, details: List<String>, body: String? = null) {
    Card(colors = CardDefaults.cardColors(containerColor = CoachPanel), modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(title, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text(details.joinToString("  ·  "), color = CoachCyan, style = MaterialTheme.typography.labelMedium)
            body?.takeIf { it.isNotBlank() }?.let { Text(it, color = CoachMuted, style = MaterialTheme.typography.bodySmall, maxLines = 4, overflow = TextOverflow.Ellipsis) }
        }
    }
}

@Composable
private fun EmptyCard(text: String) = DataCard(text, emptyList())

@Composable
private fun SetupHint() {
    Card(colors = CardDefaults.cardColors(containerColor = CoachPanel)) {
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("Backend nicht verbunden", color = CoachGold, fontWeight = FontWeight.Bold)
            Text("Öffne „Server“, trage die Adresse deines Mac-Backends und den Zugriffstoken ein.", color = CoachMuted)
        }
    }
}

private fun connectionColor(status: ConnectionStatus) = when (status) {
    ConnectionStatus.ONLINE -> CoachGreen
    ConnectionStatus.CONNECTING -> CoachGold
    ConnectionStatus.OFFLINE -> CoachRed
    ConnectionStatus.NOT_CONFIGURED -> CoachMuted
}

private fun connectionLabel(status: ConnectionStatus) = when (status) {
    ConnectionStatus.ONLINE -> "MOBILE API ONLINE"
    ConnectionStatus.CONNECTING -> "VERBINDE…"
    ConnectionStatus.OFFLINE -> "OFFLINE"
    ConnectionStatus.NOT_CONFIGURED -> "SERVER EINRICHTEN"
}

private fun Double?.format(suffix: String = ""): String = this?.let { "%.0f%s".format(it, suffix) } ?: "–"

private fun PlannedWorkout.sportLabel(): String = when (sport) {
    "swim" -> "Schwimmen"
    "bike", "cycling" -> "Radfahren"
    "run" -> "Laufen"
    "strength" -> "Kraft"
    "brick" -> "Koppeltraining"
    "rest" -> "Ruhetag"
    else -> sport.replaceFirstChar { it.uppercase() }
}
