package de.johannesbenedict.ironmancoach.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import de.johannesbenedict.ironmancoach.data.Activity
import de.johannesbenedict.ironmancoach.data.AthleteGoal
import de.johannesbenedict.ironmancoach.data.ChatMessage
import de.johannesbenedict.ironmancoach.data.CheckinRequest
import de.johannesbenedict.ironmancoach.data.CoachApi
import de.johannesbenedict.ironmancoach.data.DailyMetric
import de.johannesbenedict.ironmancoach.data.PlannedWorkout
import de.johannesbenedict.ironmancoach.data.SecureSettingsStore
import de.johannesbenedict.ironmancoach.data.ServerSettings
import de.johannesbenedict.ironmancoach.data.ServerSettingsValidator
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class ConnectionStatus { NOT_CONFIGURED, CONNECTING, ONLINE, OFFLINE }

data class CoachUiState(
    val settings: ServerSettings = ServerSettings(),
    val connection: ConnectionStatus = ConnectionStatus.NOT_CONFIGURED,
    val metrics: List<DailyMetric> = emptyList(),
    val workouts: List<PlannedWorkout> = emptyList(),
    val activities: List<Activity> = emptyList(),
    val goals: List<AthleteGoal> = emptyList(),
    val messages: List<ChatMessage> = emptyList(),
    val loading: Boolean = false,
    val syncing: Boolean = false,
    val sending: Boolean = false,
    val checkinSaved: Boolean = false,
    val error: String? = null,
)

class CoachViewModel(application: Application) : AndroidViewModel(application) {
    private val store = SecureSettingsStore(application)
    private val _state = MutableStateFlow(CoachUiState(settings = store.load()))
    val state: StateFlow<CoachUiState> = _state.asStateFlow()

    private fun api() = CoachApi(_state.value.settings)

    init {
        if (_state.value.settings.isConfigured) connectAndRefresh()
    }

    fun clearError() = _state.update { it.copy(error = null) }

    fun saveSettings(baseUrl: String, token: String) {
        val normalized = baseUrl.trim().trimEnd('/')
        val validationError = ServerSettingsValidator.validate(normalized, token)
        if (validationError != null) {
            _state.update { it.copy(error = validationError) }
            return
        }
        val settings = ServerSettings(normalized, token.trim())
        store.save(settings)
        _state.update {
            CoachUiState(settings = settings, connection = ConnectionStatus.CONNECTING)
        }
        connectAndRefresh()
    }

    fun connectAndRefresh() = viewModelScope.launch {
        if (!_state.value.settings.isConfigured) {
            _state.update { it.copy(connection = ConnectionStatus.NOT_CONFIGURED) }
            return@launch
        }
        _state.update { it.copy(connection = ConnectionStatus.CONNECTING, loading = true, error = null) }
        runCatching {
            val client = api()
            client.health()
            val metrics = async { client.metrics() }
            val workouts = async { client.plan() }
            val activities = async { client.activities() }
            val goals = async { client.goals() }
            val history = async { client.chatHistory() }
            RefreshResult(metrics.await(), workouts.await(), activities.await(), goals.await(), history.await())
        }.onSuccess { result ->
            _state.update {
                it.copy(
                    connection = ConnectionStatus.ONLINE,
                    loading = false,
                    metrics = result.metrics,
                    workouts = result.workouts,
                    activities = result.activities,
                    goals = result.goals,
                    messages = result.messages,
                )
            }
        }.onFailure { fail(it, "Verbindung fehlgeschlagen") }
    }

    fun syncGarmin() = viewModelScope.launch {
        _state.update { it.copy(syncing = true, error = null) }
        runCatching { api().syncGarmin() }
            .onSuccess {
                _state.update { it.copy(syncing = false) }
                connectAndRefresh()
            }
            .onFailure {
                _state.update { state -> state.copy(syncing = false) }
                fail(it, "Garmin-Sync fehlgeschlagen")
            }
    }

    fun submitCheckin(checkin: CheckinRequest) = viewModelScope.launch {
        _state.update { it.copy(checkinSaved = false, error = null) }
        runCatching { api().saveCheckin(checkin) }
            .onSuccess { _state.update { it.copy(checkinSaved = true) } }
            .onFailure { fail(it, "Check-in konnte nicht gespeichert werden") }
    }

    fun sendMessage(text: String) {
        val trimmed = text.trim()
        if (trimmed.isEmpty() || _state.value.sending) return
        val assistantIndex = _state.value.messages.size + 1
        _state.update {
            it.copy(
                sending = true,
                error = null,
                messages = it.messages + ChatMessage("user", trimmed) + ChatMessage("assistant", ""),
            )
        }
        viewModelScope.launch {
            api().streamChat(trimmed)
                .catch { throwable ->
                    _state.update { current ->
                        val messages = current.messages.toMutableList()
                        val existing = messages.getOrNull(assistantIndex)?.content.orEmpty()
                        if (assistantIndex in messages.indices) {
                            messages[assistantIndex] = ChatMessage("assistant", existing + "\n\n[Verbindungsfehler]")
                        }
                        current.copy(sending = false, messages = messages)
                    }
                    fail(throwable, "Coach nicht erreichbar")
                }
                .collect { delta ->
                    _state.update { current ->
                        val messages = current.messages.toMutableList()
                        if (assistantIndex in messages.indices) {
                            val existing = messages[assistantIndex]
                            messages[assistantIndex] = existing.copy(content = existing.content + delta)
                        }
                        current.copy(messages = messages)
                    }
                }
            _state.update { it.copy(sending = false) }
        }
    }

    private fun fail(throwable: Throwable, prefix: String) {
        val detail = throwable.message?.takeIf { it.isNotBlank() } ?: throwable::class.simpleName.orEmpty()
        _state.update {
            it.copy(
                connection = if (it.connection == ConnectionStatus.CONNECTING) ConnectionStatus.OFFLINE else it.connection,
                loading = false,
                error = "$prefix: $detail",
            )
        }
    }

    private data class RefreshResult(
        val metrics: List<DailyMetric>,
        val workouts: List<PlannedWorkout>,
        val activities: List<Activity>,
        val goals: List<AthleteGoal>,
        val messages: List<ChatMessage>,
    )
}
