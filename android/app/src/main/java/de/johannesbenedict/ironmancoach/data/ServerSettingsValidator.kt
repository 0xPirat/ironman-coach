package de.johannesbenedict.ironmancoach.data

import java.net.URI

/** Prevents accidentally sending health data and bearer tokens over public HTTP. */
object ServerSettingsValidator {
    fun validate(baseUrl: String, token: String): String? {
        val uri = runCatching { URI(baseUrl.trim()) }.getOrNull()
            ?: return "Die Server-Adresse ist ungültig."
        if (uri.scheme !in setOf("http", "https") || uri.host.isNullOrBlank()) {
            return "Die Adresse muss mit http:// oder https:// beginnen."
        }
        if (token.trim().length < 32) {
            return "Der Mobile-API-Token muss mindestens 32 Zeichen lang sein."
        }
        if (uri.scheme == "http" && !isPrivateHost(uri.host)) {
            return "Öffentliche Server-Adressen benötigen HTTPS. HTTP ist nur für private LAN-Adressen erlaubt."
        }
        return null
    }

    private fun isPrivateHost(host: String): Boolean {
        val normalized = host.lowercase().removePrefix("[").removeSuffix("]")
        if (normalized == "localhost" || normalized.endsWith(".local")) return true
        if (normalized == "::1" || normalized.startsWith("fc") ||
            normalized.startsWith("fd") || normalized.startsWith("fe80:")) return true
        val parts = normalized.split('.').mapNotNull(String::toIntOrNull)
        if (parts.size != 4 || parts.any { it !in 0..255 }) return false
        return parts[0] == 10 || parts[0] == 127 ||
            (parts[0] == 192 && parts[1] == 168) ||
            (parts[0] == 172 && parts[1] in 16..31)
    }
}
