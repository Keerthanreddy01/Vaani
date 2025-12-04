package com.vaani.phone

import android.util.Log
import java.util.Locale

data class ClassificationResult(
    val intent: String,
    val entities: Map<String, String>,
    val confidence: Float
)

class VaaniIntentClassifier {
    
    companion object {
        const val TAG = "VaaniIntentClassifier"
        
        // App keywords
        val APP_KEYWORDS = mapOf(
            "whatsapp" to "com.whatsapp",
            "chrome" to "com.android.chrome",
            "gmail" to "com.google.android.gm",
            "maps" to "com.google.android.apps.maps",
            "youtube" to "com.google.android.youtube",
            "spotify" to "com.spotify.music",
            "facebook" to "com.facebook.katana",
            "instagram" to "com.instagram.android",
            "camera" to "com.android.camera2",
            "settings" to "com.android.settings",
            "calculator" to "com.android.calculator2",
            "calendar" to "com.google.android.calendar",
            "messages" to "com.google.android.apps.messaging",
            "phone" to "com.android.dialer",
            "contacts" to "com.android.contacts"
        )
    }
    
    fun classify(text: String): ClassificationResult? {
        val textLower = text.lowercase(Locale.getDefault())
        Log.d(TAG, "Classifying: $textLower")
        
        // Emergency SOS - HIGHEST PRIORITY
        if (textLower.matches(Regex(".*(emergency|help me|danger|sos|911|112).*"))) {
            return ClassificationResult("EMERGENCY_SOS", emptyMap(), 1.0f)
        }
        
        // App control - Multilingual
        if (textLower.contains("open") || textLower.contains("launch") || textLower.contains("start") ||
            textLower.contains("తెరువు") || textLower.contains("खोलो") || textLower.contains("திற") ||
            textLower.contains("cheyyi") || textLower.contains("karo") || textLower.contains("pannunga")) {
            val app = extractApp(textLower)
            if (app != null) {
                return ClassificationResult(
                    "OPEN_APP",
                    mapOf("app" to app),
                    1.0f
                )
            }
        }
        
        // Calling - Multilingual
        if (textLower.contains("call") || textLower.contains("కాల్") || textLower.contains("फोन") ||
            textLower.contains("அழை") || textLower.contains("chey") || textLower.contains("karo")) {
            val phoneNumber = extractPhoneNumber(textLower)
            val contactName = extractContactName(textLower)
            
            val entities = mutableMapOf<String, String>()
            if (phoneNumber != null) entities["phone_number"] = phoneNumber
            if (contactName != null) entities["contact_name"] = contactName
            
            if (entities.isNotEmpty()) {
                return ClassificationResult("CALL_CONTACT", entities, 1.0f)
            }
        }
        
        // Messaging
        if (textLower.contains("send") && (textLower.contains("message") || textLower.contains("text") || textLower.contains("sms"))) {
            val phoneNumber = extractPhoneNumber(textLower)
            val message = extractMessage(textLower)
            
            if (phoneNumber != null && message != null) {
                return ClassificationResult(
                    "SEND_MESSAGE",
                    mapOf("phone_number" to phoneNumber, "message" to message),
                    1.0f
                )
            }
        }
        
        // Navigation - Back
        if (textLower.matches(Regex(".*(go back|back|previous).*"))) {
            return ClassificationResult("GO_BACK", emptyMap(), 1.0f)
        }
        
        // Navigation - Home
        if (textLower.matches(Regex(".*(go home|home|main screen).*"))) {
            return ClassificationResult("GO_HOME", emptyMap(), 1.0f)
        }
        
        // Scrolling
        if (textLower.contains("scroll")) {
            val direction = when {
                textLower.contains("down") -> "down"
                textLower.contains("up") -> "up"
                else -> "down"
            }
            return ClassificationResult(
                "SCROLL_PAGE",
                mapOf("direction" to direction),
                1.0f
            )
        }
        
        // Swiping
        if (textLower.contains("swipe")) {
            val direction = when {
                textLower.contains("left") -> "left"
                textLower.contains("right") -> "right"
                textLower.contains("up") -> "up"
                textLower.contains("down") -> "down"
                else -> "left"
            }
            return ClassificationResult(
                "SWIPE_GESTURE",
                mapOf("direction" to direction),
                1.0f
            )
        }
        
        // Reading screen
        if (textLower.matches(Regex(".*(read|what's on|show me).*screen.*"))) {
            return ClassificationResult("READ_SCREEN", emptyMap(), 1.0f)
        }
        
        // Volume control
        if (textLower.contains("volume")) {
            val direction = when {
                textLower.contains("up") || textLower.contains("increase") -> "up"
                textLower.contains("down") || textLower.contains("decrease") -> "down"
                else -> "up"
            }
            return ClassificationResult(
                if (direction == "up") "VOLUME_UP" else "VOLUME_DOWN",
                emptyMap(),
                1.0f
            )
        }
        
        // Brightness control
        if (textLower.contains("brightness")) {
            val direction = when {
                textLower.contains("up") || textLower.contains("increase") -> "up"
                textLower.contains("down") || textLower.contains("decrease") -> "down"
                else -> "up"
            }
            return ClassificationResult(
                if (direction == "up") "BRIGHTNESS_UP" else "BRIGHTNESS_DOWN",
                emptyMap(),
                1.0f
            )
        }
        
        // Taking photo
        if (textLower.matches(Regex(".*(take|capture).*(photo|picture|selfie).*"))) {
            return ClassificationResult("TAKE_PHOTO", emptyMap(), 1.0f)
        }
        
        // Playing music
        if (textLower.matches(Regex(".*(play|start).*(music|song|audio).*"))) {
            return ClassificationResult("PLAY_MUSIC", emptyMap(), 1.0f)
        }
        
        // Typing - for text input
        if (textLower.startsWith("type ") || textLower.startsWith("write ") ||
            textLower.contains("టైప్") || textLower.contains("लिखो")) {
            val textToType = extractTextToType(textLower)
            if (textToType != null) {
                return ClassificationResult(
                    "TYPE_TEXT",
                    mapOf("text" to textToType),
                    1.0f
                )
            }
        }
        
        // Search commands
        if (textLower.contains("search for") || textLower.contains("find") ||
            textLower.contains("సెర్చ్") || textLower.contains("खोजो")) {
            val searchQuery = extractSearchQuery(textLower)
            if (searchQuery != null) {
                return ClassificationResult(
                    "SEARCH",
                    mapOf("query" to searchQuery),
                    1.0f
                )
            }
        }
        
        Log.d(TAG, "No intent matched for: $textLower")
        return null
    }
    
    private fun extractApp(text: String): String? {
        for ((keyword, packageName) in APP_KEYWORDS) {
            if (text.contains(keyword)) {
                return packageName
            }
        }
        return null
    }
    
    private fun extractPhoneNumber(text: String): String? {
        // Extract 10-digit phone number
        val regex = Regex("\\b\\d{10}\\b")
        val match = regex.find(text)
        return match?.value
    }
    
    private fun extractMessage(text: String): String? {
        // Extract text after "saying" or "message"
        val sayingMatch = Regex("saying (.+)").find(text)
        if (sayingMatch != null) {
            return sayingMatch.groupValues[1].trim()
        }
        
        val messageMatch = Regex("message (.+)").find(text)
        if (messageMatch != null) {
            return messageMatch.groupValues[1].trim()
        }
        
        return null
    }
    
    private fun extractContactName(text: String): String? {
        // Extract contact names (amma, appa, mom, dad, etc.)
        val commonNames = listOf("amma", "appa", "mom", "dad", "brother", "sister")
        for (name in commonNames) {
            if (text.contains(name)) {
                return name
            }
        }
        return null
    }
    
    private fun extractTextToType(text: String): String? {
        val typeMatch = Regex("type:? (.+)", RegexOption.IGNORE_CASE).find(text)
        if (typeMatch != null) {
            return typeMatch.groupValues[1].trim()
        }
        
        val writeMatch = Regex("write:? (.+)", RegexOption.IGNORE_CASE).find(text)
        if (writeMatch != null) {
            return writeMatch.groupValues[1].trim()
        }
        
        return null
    }
    
    private fun extractSearchQuery(text: String): String? {
        val searchMatch = Regex("search for (.+)", RegexOption.IGNORE_CASE).find(text)
        if (searchMatch != null) {
            return searchMatch.groupValues[1].trim()
        }
        
        val findMatch = Regex("find (.+)", RegexOption.IGNORE_CASE).find(text)
        if (findMatch != null) {
            return findMatch.groupValues[1].trim()
        }
        
        return null
    }
}
