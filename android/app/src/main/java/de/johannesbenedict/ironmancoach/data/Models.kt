package de.johannesbenedict.ironmancoach.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Health(val status: String, val service: String? = null, val date: String? = null)

@Serializable
data class DailyMetric(
    val date: String,
    val hrv: Double? = null,
    val rhr: Int? = null,
    @SerialName("sleep_hours") val sleepHours: Double? = null,
    @SerialName("body_battery") val bodyBattery: Int? = null,
    @SerialName("training_readiness") val trainingReadiness: Int? = null,
    val ctl: Double? = null,
    val atl: Double? = null,
    val tsb: Double? = null,
    val vo2max: Double? = null,
)

@Serializable
data class PlannedWorkout(
    val id: Int,
    val date: String,
    val sport: String,
    val title: String? = null,
    @SerialName("duration_min") val durationMin: Int? = null,
    @SerialName("distance_km") val distanceKm: Double? = null,
    @SerialName("target_zone") val targetZone: String? = null,
    val content: String? = null,
    val priority: String? = null,
    val status: String? = null,
)

@Serializable
data class Activity(
    val id: Int,
    val date: String,
    val sport: String,
    val title: String? = null,
    @SerialName("duration_min") val durationMin: Double? = null,
    @SerialName("distance_km") val distanceKm: Double? = null,
    @SerialName("avg_hr") val averageHeartRate: Int? = null,
    @SerialName("training_load") val trainingLoad: Double? = null,
)

@Serializable
data class AthleteGoal(
    val id: Int,
    val title: String,
    val sport: String,
    @SerialName("event_date") val eventDate: String? = null,
    @SerialName("target_metric") val targetMetric: String? = null,
    val priority: Int? = null,
)

@Serializable
data class ChatMessage(
    val role: String,
    val content: String,
)

@Serializable
data class CheckinRequest(
    val date: String? = null,
    val soreness: Int? = null,
    @SerialName("pain_location") val painLocation: String? = null,
    @SerialName("pain_level") val painLevel: Int? = null,
    val motivation: Int? = null,
    @SerialName("mental_energy") val mentalEnergy: Int? = null,
    @SerialName("available_time") val availableTime: Int? = null,
    @SerialName("life_stress") val lifeStress: Int? = null,
    val notes: String? = null,
)

@Serializable
data class SavedResponse(val saved: Boolean = false, val date: String? = null)

@Serializable
data class SseEvent(val delta: String? = null, val done: Boolean = false)

data class ServerSettings(val baseUrl: String = "", val token: String = "") {
    val isConfigured: Boolean get() = baseUrl.isNotBlank()
}
