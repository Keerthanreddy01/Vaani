package com.vaani.phone

import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

class VaaniMultilingualHelper(private val context: Context) {
    
    private var tts: TextToSpeech? = null
    private var selectedLanguage: String = "English (India)"
    private var assistantName: String = "VAANI"
    
    companion object {
        const val TAG = "VaaniMultilingual"
        
        val LANGUAGE_CODES = mapOf(
            "English (India)" to Locale("en", "IN"),
            "English (US)" to Locale.US,
            "English (UK)" to Locale.UK,
            "తెలుగు (Telugu)" to Locale("te", "IN"),
            "हिन्दी (Hindi)" to Locale("hi", "IN"),
            "தமிழ் (Tamil)" to Locale("ta", "IN"),
            "ಕನ್ನಡ (Kannada)" to Locale("kn", "IN"),
            "മലയാളം (Malayalam)" to Locale("ml", "IN"),
            "বাংলা (Bengali)" to Locale("bn", "IN"),
            "मराठी (Marathi)" to Locale("mr", "IN"),
            "ગુજરાતી (Gujarati)" to Locale("gu", "IN")
        )
    }
    
    init {
        loadPreferences()
        initializeTTS()
    }
    
    private fun loadPreferences() {
        val prefs = context.getSharedPreferences(OnboardingActivity.PREFS_NAME, Context.MODE_PRIVATE)
        selectedLanguage = prefs.getString(OnboardingActivity.KEY_LANGUAGE, "English (India)") ?: "English (India)"
        assistantName = prefs.getString(OnboardingActivity.KEY_ASSISTANT_NAME, "VAANI") ?: "VAANI"
    }
    
    private fun initializeTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val locale = LANGUAGE_CODES[selectedLanguage] ?: Locale("en", "IN")
                tts?.language = locale
            }
        }
    }
    
    fun getAssistantName(): String = assistantName
    
    fun getWakeWord(): String = "hey ${assistantName.lowercase()}"
    
    fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
    }
    
    fun getResponse(intent: String, success: Boolean): String {
        return when (selectedLanguage) {
            "తెలుగు (Telugu)" -> getTeluguResponse(intent, success)
            "हिन्दी (Hindi)" -> getHindiResponse(intent, success)
            "தமிழ் (Tamil)" -> getTamilResponse(intent, success)
            else -> getEnglishResponse(intent, success)
        }
    }
    
    private fun getEnglishResponse(intent: String, success: Boolean): String {
        if (!success) return "Sorry, I couldn't do that."
        
        return when (intent) {
            "OPEN_APP" -> "Opening app"
            "CALL_CONTACT" -> "Calling now"
            "SEND_MESSAGE" -> "Message sent"
            "GO_BACK" -> "Going back"
            "GO_HOME" -> "Going home"
            "SCROLL_PAGE" -> "Scrolling"
            "READ_SCREEN" -> "Reading screen"
            "VOLUME_UP" -> "Volume increased"
            "VOLUME_DOWN" -> "Volume decreased"
            "BRIGHTNESS_UP" -> "Brightness increased"
            "BRIGHTNESS_DOWN" -> "Brightness decreased"
            "TAKE_PHOTO" -> "Taking photo"
            "EMERGENCY_SOS" -> "Calling emergency services"
            else -> "Done"
        }
    }
    
    private fun getTeluguResponse(intent: String, success: Boolean): String {
        if (!success) return "క్షమించండి, నేను చేయలేకపోయాను."
        
        return when (intent) {
            "OPEN_APP" -> "యాప్ తెరుస్తున్నాను"
            "CALL_CONTACT" -> "కాల్ చేస్తున్నాను"
            "SEND_MESSAGE" -> "మెసేజ్ పంపాను"
            "GO_BACK" -> "వెనక్కి వెళ్తున్నాను"
            "GO_HOME" -> "హోమ్ కు వెళ్తున్నాను"
            "SCROLL_PAGE" -> "స్క్రోల్ చేస్తున్నాను"
            "READ_SCREEN" -> "స్క్రీన్ చదువుతున్నాను"
            "VOLUME_UP" -> "వాల్యూమ్ పెంచాను"
            "VOLUME_DOWN" -> "వాల్యూమ్ తగ్గించాను"
            "BRIGHTNESS_UP" -> "బ్రైట్‌నెస్ పెంచాను"
            "BRIGHTNESS_DOWN" -> "బ్రైట్‌నెస్ తగ్గించాను"
            "TAKE_PHOTO" -> "ఫోటో తీస్తున్నాను"
            "EMERGENCY_SOS" -> "ఎమర్జెన్సీ కి కాల్ చేస్తున్నాను"
            else -> "అయ్యింది"
        }
    }
    
    private fun getHindiResponse(intent: String, success: Boolean): String {
        if (!success) return "माफ़ करें, मैं ऐसा नहीं कर सका।"
        
        return when (intent) {
            "OPEN_APP" -> "ऐप खोल रहा हूं"
            "CALL_CONTACT" -> "कॉल कर रहा हूं"
            "SEND_MESSAGE" -> "मैसेज भेज दिया"
            "GO_BACK" -> "वापस जा रहा हूं"
            "GO_HOME" -> "होम पर जा रहा हूं"
            "SCROLL_PAGE" -> "स्क्रॉल कर रहा हूं"
            "READ_SCREEN" -> "स्क्रीन पढ़ रहा हूं"
            "VOLUME_UP" -> "आवाज़ बढ़ा दी"
            "VOLUME_DOWN" -> "आवाज़ कम कर दी"
            "BRIGHTNESS_UP" -> "चमक बढ़ा दी"
            "BRIGHTNESS_DOWN" -> "चमक कम कर दी"
            "TAKE_PHOTO" -> "फोटो ले रहा हूं"
            "EMERGENCY_SOS" -> "इमरजेंसी को कॉल कर रहा हूं"
            else -> "हो गया"
        }
    }
    
    private fun getTamilResponse(intent: String, success: Boolean): String {
        if (!success) return "மன்னிக்கவும், என்னால் அதை செய்ய முடியவில்லை."
        
        return when (intent) {
            "OPEN_APP" -> "ஆப் திறக்கிறேன்"
            "CALL_CONTACT" -> "அழைக்கிறேன்"
            "SEND_MESSAGE" -> "செய்தி அனுப்பினேன்"
            "GO_BACK" -> "பின்னால் செல்கிறேன்"
            "GO_HOME" -> "ஹோம் செல்கிறேன்"
            "SCROLL_PAGE" -> "ஸ்க்ரோல் செய்கிறேன்"
            "READ_SCREEN" -> "திரை படிக்கிறேன்"
            "VOLUME_UP" -> "ஒலி அதிகரித்தேன்"
            "VOLUME_DOWN" -> "ஒலி குறைத்தேன்"
            "BRIGHTNESS_UP" -> "பிரகாசம் அதிகரித்தேன்"
            "BRIGHTNESS_DOWN" -> "பிரகாசம் குறைத்தேன்"
            "TAKE_PHOTO" -> "புகைப்படம் எடுக்கிறேன்"
            "EMERGENCY_SOS" -> "அவசரத்திற்கு அழைக்கிறேன்"
            else -> "முடிந்தது"
        }
    }
    
    fun shutdown() {
        tts?.shutdown()
    }
}
