package de.johannesbenedict.ironmancoach.data

import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import okhttp3.HttpUrl.Companion.toHttpUrl

class ApiException(val statusCode: Int, message: String) : IOException(message)

class CoachApi(private val settings: ServerSettings) {
    private val json = Json { ignoreUnknownKeys = true; explicitNulls = false; coerceInputValues = true }
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()
    private val jsonType = "application/json; charset=utf-8".toMediaType()

    suspend fun health(): Health = get("health")
    suspend fun metrics(): List<DailyMetric> = get("metrics")
    suspend fun plan(): List<PlannedWorkout> = get("plan")
    suspend fun activities(): List<Activity> = get("activities")
    suspend fun goals(): List<AthleteGoal> = get("goals")
    suspend fun chatHistory(): List<ChatMessage> = get("chat/history", mapOf("limit" to "50"))

    suspend fun saveCheckin(checkin: CheckinRequest): SavedResponse = post(
        "checkin",
        json.encodeToString(checkin),
    )

    suspend fun syncGarmin(): String = withContext(Dispatchers.IO) {
        val request = request("sync/garmin", mapOf("days" to "7")).post(ByteArray(0).toRequestBody()).build()
        client.newBuilder().callTimeout(5, TimeUnit.MINUTES).build().newCall(request).execute().use { response ->
            response.requireSuccess().body?.string().orEmpty()
        }
    }

    fun streamChat(message: String): Flow<String> = flow {
        val body = json.encodeToString(mapOf("message" to message)).toRequestBody(jsonType)
        val request = request("chat").post(body).header("Accept", "text/event-stream").build()
        val streamClient = client.newBuilder().readTimeout(0, TimeUnit.SECONDS).build()
        streamClient.newCall(request).execute().use { response ->
            response.requireSuccess()
            val source = response.body?.source() ?: throw IOException("Leere Antwort vom Coach")
            while (!source.exhausted()) {
                val line = source.readUtf8Line() ?: break
                if (!line.startsWith("data:")) continue
                val payload = line.removePrefix("data:").trim()
                val event = runCatching { json.decodeFromString<SseEvent>(payload) }.getOrNull() ?: continue
                event.delta?.let { emit(it) }
                if (event.done) break
            }
        }
    }.flowOn(Dispatchers.IO)

    private suspend inline fun <reified T> get(
        path: String,
        query: Map<String, String> = emptyMap(),
    ): T = withContext(Dispatchers.IO) {
        client.newCall(request(path, query).get().build()).execute().use { response ->
            response.requireSuccess()
            json.decodeFromString(response.body?.string() ?: throw IOException("Leere Serverantwort"))
        }
    }

    private suspend inline fun <reified T> post(path: String, body: String): T = withContext(Dispatchers.IO) {
        val request = request(path).post(body.toRequestBody(jsonType)).build()
        client.newCall(request).execute().use { response ->
            response.requireSuccess()
            json.decodeFromString(response.body?.string() ?: throw IOException("Leere Serverantwort"))
        }
    }

    private fun request(path: String, query: Map<String, String> = emptyMap()): Request.Builder {
        check(settings.baseUrl.isNotBlank()) { "Bitte zuerst die Server-Adresse einrichten." }
        val base = (settings.baseUrl.trimEnd('/') + "/").toHttpUrl()
        val url = base.newBuilder().addPathSegments(path).apply {
            query.forEach { (key, value) -> addQueryParameter(key, value) }
        }.build()
        return Request.Builder().url(url).apply {
            if (settings.token.isNotBlank()) header("Authorization", "Bearer ${settings.token}")
        }
    }

    private fun Response.requireSuccess(): Response {
        if (isSuccessful) return this
        val raw = body?.string().orEmpty()
        val detail = Regex("\\\"detail\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"").find(raw)?.groupValues?.get(1)
        throw ApiException(code, detail ?: "Serverfehler HTTP $code")
    }
}
