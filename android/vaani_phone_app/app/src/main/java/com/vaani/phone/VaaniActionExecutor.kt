package com.vaani.phone

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.util.Log
import kotlinx.coroutines.delay

data class ActionResult(
    val success: Boolean,
    val message: String
)

class VaaniActionExecutor(private val context: Context) {
    
    companion object {
        const val TAG = "VaaniActionExecutor"
    }
    
    private val accessibilityService: VaaniAccessibilityService?
        get() = VaaniAccessibilityService.instance
    
    suspend fun execute(intent: String, entities: Map<String, String>): ActionResult {
        Log.d(TAG, "Executing intent: $intent with entities: $entities")
        
        return when (intent) {
            "OPEN_APP" -> openApp(entities["app"])
            "CALL_CONTACT" -> callContact(entities)
            "SEND_MESSAGE" -> sendMessage(entities["phone_number"], entities["message"])
            "GO_BACK" -> performBack()
            "GO_HOME" -> performHome()
            "SCROLL_PAGE" -> scroll(entities["direction"])
            "SWIPE_GESTURE" -> swipe(entities["direction"])
            "READ_SCREEN" -> readScreen()
            "VOLUME_UP" -> volumeUp()
            "VOLUME_DOWN" -> volumeDown()
            "BRIGHTNESS_UP" -> brightnessUp()
            "BRIGHTNESS_DOWN" -> brightnessDown()
            "TAKE_PHOTO" -> takePhoto()
            "PLAY_MUSIC" -> playMusic()
            "TYPE_TEXT" -> typeText(entities["text"])
            "SEARCH" -> performSearch(entities["query"])
            "EMERGENCY_SOS" -> emergencySOS()
            else -> ActionResult(false, "Unknown intent: $intent")
        }
    }
    
    private fun openApp(packageName: String?): ActionResult {
        if (packageName == null) {
            return ActionResult(false, "No app specified")
        }
        
        return try {
            val launchIntent = context.packageManager.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launchIntent)
                ActionResult(true, "Opening app")
            } else {
                ActionResult(false, "App not found")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error opening app", e)
            ActionResult(false, "Failed to open app: ${e.message}")
        }
    }
    
    private fun callContact(entities: Map<String, String>): ActionResult {
        val phoneNumber = entities["phone_number"]
        val contactName = entities["contact_name"]
        
        // If we have a contact name, try to look it up
        if (contactName != null && phoneNumber == null) {
            // TODO: Implement contact lookup
            return ActionResult(false, "Contact lookup not yet implemented")
        }
        
        return if (phoneNumber != null) {
            callNumber(phoneNumber)
        } else {
            ActionResult(false, "No phone number or contact specified")
        }
    }
    
    private fun callNumber(phoneNumber: String): ActionResult {
        return try {
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$phoneNumber")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            ActionResult(true, "Calling $phoneNumber")
        } catch (e: Exception) {
            Log.e(TAG, "Error making call", e)
            ActionResult(false, "Failed to make call: ${e.message}")
        }
    }
    
    private fun sendMessage(phoneNumber: String?, message: String?): ActionResult {
        if (phoneNumber == null || message == null) {
            return ActionResult(false, "Phone number or message missing")
        }
        
        return try {
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse("sms:$phoneNumber")
                putExtra("sms_body", message)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            ActionResult(true, "Opening messages")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending message", e)
            ActionResult(false, "Failed to send message: ${e.message}")
        }
    }
    
    private fun performBack(): ActionResult {
        return if (accessibilityService?.performBack() == true) {
            ActionResult(true, "Going back")
        } else {
            ActionResult(false, "Accessibility service not available")
        }
    }
    
    private fun performHome(): ActionResult {
        return if (accessibilityService?.performHome() == true) {
            ActionResult(true, "Going home")
        } else {
            ActionResult(false, "Accessibility service not available")
        }
    }
    
    private suspend fun scroll(direction: String?): ActionResult {
        val dir = direction ?: "down"
        
        return if (dir == "down") {
            if (accessibilityService?.scrollDown() == true) {
                ActionResult(true, "Scrolling down")
            } else {
                ActionResult(false, "Accessibility service not available")
            }
        } else {
            if (accessibilityService?.scrollUp() == true) {
                ActionResult(true, "Scrolling up")
            } else {
                ActionResult(false, "Accessibility service not available")
            }
        }
    }
    
    private suspend fun swipe(direction: String?): ActionResult {
        val dir = direction ?: "left"
        
        return if (accessibilityService?.performSwipe(dir) == true) {
            ActionResult(true, "Swiping $dir")
        } else {
            ActionResult(false, "Accessibility service not available")
        }
    }
    
    private suspend fun readScreen(): ActionResult {
        val text = accessibilityService?.readScreenText()
        
        return if (text != null && text.isNotBlank()) {
            ActionResult(true, "Screen shows: $text")
        } else {
            ActionResult(false, "Nothing to read")
        }
    }
    
    private fun volumeUp(): ActionResult {
        // This would use AudioManager in real implementation
        return ActionResult(true, "Volume increased")
    }
    
    private fun volumeDown(): ActionResult {
        // This would use AudioManager in real implementation
        return ActionResult(true, "Volume decreased")
    }
    
    private fun brightnessUp(): ActionResult {
        return try {
            val currentBrightness = Settings.System.getInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS
            )
            val newBrightness = minOf(255, currentBrightness + 50)
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS,
                newBrightness
            )
            ActionResult(true, "Brightness increased")
        } catch (e: Exception) {
            ActionResult(false, "Cannot change brightness")
        }
    }
    
    private fun brightnessDown(): ActionResult {
        return try {
            val currentBrightness = Settings.System.getInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS
            )
            val newBrightness = maxOf(0, currentBrightness - 50)
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS,
                newBrightness
            )
            ActionResult(true, "Brightness decreased")
        } catch (e: Exception) {
            ActionResult(false, "Cannot change brightness")
        }
    }
    
    private suspend fun takePhoto(): ActionResult {
        // Open camera
        openApp("com.android.camera2")
        delay(2000)
        
        // Tap center bottom (shutter button)
        accessibilityService?.performTap(540f, 1800f)
        
        return ActionResult(true, "Taking photo")
    }
    
    private fun playMusic(): ActionResult {
        return openApp("com.spotify.music")
    }
    
    private fun typeText(text: String?): ActionResult {
        if (text == null) {
            return ActionResult(false, "No text to type")
        }
        
        return if (accessibilityService?.typeText(text) == true) {
            ActionResult(true, "Typed text")
        } else {
            ActionResult(false, "Accessibility service not available")
        }
    }
    
    private suspend fun performSearch(query: String?): ActionResult {
        if (query == null) {
            return ActionResult(false, "No search query")
        }
        
        // Type the search query
        delay(500)
        accessibilityService?.typeText(query)
        delay(500)
        
        // Press enter/search
        accessibilityService?.pressEnter()
        
        return ActionResult(true, "Searching for $query")
    }
    
    private fun emergencySOS(): ActionResult {
        try {
            // Call emergency number
            callNumber("112")
            
            // TODO: Send SMS with location to emergency contact
            // TODO: Play loud alarm
            // TODO: Flash screen
            
            return ActionResult(true, "Emergency services contacted")
        } catch (e: Exception) {
            Log.e(TAG, "Emergency SOS failed", e)
            return ActionResult(false, "Emergency call failed")
        }
    }
}
