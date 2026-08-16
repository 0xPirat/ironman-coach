package de.johannesbenedict.ironmancoach.data

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject

class ModelsTest {
    private val json = Json { ignoreUnknownKeys = true }

    @Test
    fun `backend snake case metric fields decode`() {
        val metric = json.decodeFromString<DailyMetric>(
            """{"date":"2026-08-16","sleep_hours":7.5,"body_battery":81,"training_readiness":72,"future":true}""",
        )
        assertEquals(7.5, metric.sleepHours)
        assertEquals(81, metric.bodyBattery)
        assertEquals(72, metric.trainingReadiness)
    }

    @Test
    fun `checkin encodes backend field names`() {
        val payload = json.encodeToString(CheckinRequest(mentalEnergy = 4, availableTime = 75))
        val objectValue = json.parseToJsonElement(payload).jsonObject
        assertEquals("4", objectValue.getValue("mental_energy").toString())
        assertEquals("75", objectValue.getValue("available_time").toString())
    }
}
