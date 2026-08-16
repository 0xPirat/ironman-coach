package de.johannesbenedict.ironmancoach.data

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/** Stores the endpoint normally and the bearer token encrypted with Android Keystore. */
class SecureSettingsStore(context: Context) {
    private val preferences = context.getSharedPreferences("server_settings", Context.MODE_PRIVATE)

    fun load(): ServerSettings = ServerSettings(
        baseUrl = preferences.getString(KEY_URL, "").orEmpty(),
        token = preferences.getString(KEY_TOKEN, null)?.let(::decrypt).orEmpty(),
    )

    fun save(settings: ServerSettings) {
        val normalized = settings.baseUrl.trim().trimEnd('/')
        preferences.edit()
            .putString(KEY_URL, normalized)
            .putString(KEY_TOKEN, encrypt(settings.token.trim()))
            .apply()
    }

    private fun key(): SecretKey {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").run {
            init(
                KeyGenParameterSpec.Builder(
                    KEY_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT,
                )
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .build(),
            )
            generateKey()
        }
    }

    private fun encrypt(value: String): String {
        if (value.isEmpty()) return ""
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, key())
        val joined = cipher.iv + cipher.doFinal(value.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(joined, Base64.NO_WRAP)
    }

    private fun decrypt(value: String): String = runCatching {
        if (value.isEmpty()) return ""
        val joined = Base64.decode(value, Base64.NO_WRAP)
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, joined.copyOfRange(0, IV_SIZE)))
        String(cipher.doFinal(joined.copyOfRange(IV_SIZE, joined.size)), Charsets.UTF_8)
    }.getOrDefault("")

    private companion object {
        const val KEY_URL = "base_url"
        const val KEY_TOKEN = "token_encrypted"
        const val KEY_ALIAS = "ironman_coach_mobile_api"
        const val TRANSFORMATION = "AES/GCM/NoPadding"
        const val IV_SIZE = 12
    }
}
