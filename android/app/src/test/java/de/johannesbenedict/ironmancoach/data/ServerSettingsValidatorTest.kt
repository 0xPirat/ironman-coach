package de.johannesbenedict.ironmancoach.data

import kotlin.test.Test
import kotlin.test.assertNotNull
import kotlin.test.assertNull

class ServerSettingsValidatorTest {
    private val token = "x".repeat(32)

    @Test
    fun `allows private LAN HTTP and public HTTPS`() {
        assertNull(ServerSettingsValidator.validate("http://192.168.178.20:8766", token))
        assertNull(ServerSettingsValidator.validate("http://172.16.1.2:8766", token))
        assertNull(ServerSettingsValidator.validate("http://10.0.2.2:8766", token))
        assertNull(ServerSettingsValidator.validate("https://coach.example.com", token))
    }

    @Test
    fun `rejects public cleartext and short token`() {
        assertNotNull(ServerSettingsValidator.validate("http://coach.example.com", token))
        assertNotNull(ServerSettingsValidator.validate("https://coach.example.com", "short"))
    }
}
