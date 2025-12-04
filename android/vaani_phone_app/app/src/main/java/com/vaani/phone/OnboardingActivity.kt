package com.vaani.phone

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class OnboardingActivity : AppCompatActivity() {
    
    private var currentStep = 0
    private lateinit var assistantName: String
    private lateinit var selectedLanguage: String
    
    // UI Elements
    private lateinit var stepContainer: LinearLayout
    private lateinit var titleText: TextView
    private lateinit var subtitleText: TextView
    private lateinit var nextButton: Button
    
    // Step 1: Welcome
    private lateinit var welcomeContainer: LinearLayout
    
    // Step 2: Name Selection
    private lateinit var nameContainer: LinearLayout
    private lateinit var nameInput: EditText
    private lateinit var nameExamples: TextView
    
    // Step 3: Language Selection
    private lateinit var languageContainer: LinearLayout
    private lateinit var languageSpinner: Spinner
    
    // Step 4: Permissions
    private lateinit var permissionsContainer: LinearLayout
    private lateinit var permissionsList: LinearLayout
    
    // Step 5: Complete
    private lateinit var completeContainer: LinearLayout
    
    companion object {
        const val PREFS_NAME = "VaaniPrefs"
        const val KEY_ONBOARDING_COMPLETE = "onboarding_complete"
        const val KEY_ASSISTANT_NAME = "assistant_name"
        const val KEY_LANGUAGE = "language"
        const val REQUEST_PERMISSIONS = 100
        const val REQUEST_OVERLAY = 101
        const val REQUEST_ACCESSIBILITY = 102
        
        val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_CONTACTS,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
        
        val LANGUAGES = arrayOf(
            "English (India)",
            "English (US)",
            "English (UK)",
            "తెలుగు (Telugu)",
            "हिन्दी (Hindi)",
            "தமிழ் (Tamil)",
            "ಕನ್ನಡ (Kannada)",
            "മലയാളം (Malayalam)",
            "বাংলা (Bengali)",
            "मराठी (Marathi)",
            "ગુજરાતી (Gujarati)"
        )
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Check if onboarding is already complete
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        if (prefs.getBoolean(KEY_ONBOARDING_COMPLETE, false)) {
            // Skip to main activity
            startMainActivity()
            return
        }
        
        setContentView(R.layout.activity_onboarding)
        
        initializeViews()
        showStep(0)
    }
    
    private fun initializeViews() {
        stepContainer = findViewById(R.id.stepContainer)
        titleText = findViewById(R.id.titleText)
        subtitleText = findViewById(R.id.subtitleText)
        nextButton = findViewById(R.id.nextButton)
        
        welcomeContainer = findViewById(R.id.welcomeContainer)
        nameContainer = findViewById(R.id.nameContainer)
        languageContainer = findViewById(R.id.languageContainer)
        permissionsContainer = findViewById(R.id.permissionsContainer)
        completeContainer = findViewById(R.id.completeContainer)
        
        nameInput = findViewById(R.id.nameInput)
        nameExamples = findViewById(R.id.nameExamples)
        languageSpinner = findViewById(R.id.languageSpinner)
        permissionsList = findViewById(R.id.permissionsList)
        
        // Setup language spinner
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, LANGUAGES)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        languageSpinner.adapter = adapter
        
        nextButton.setOnClickListener {
            handleNext()
        }
    }
    
    private fun showStep(step: Int) {
        currentStep = step
        
        // Hide all containers
        welcomeContainer.visibility = View.GONE
        nameContainer.visibility = View.GONE
        languageContainer.visibility = View.GONE
        permissionsContainer.visibility = View.GONE
        completeContainer.visibility = View.GONE
        
        when (step) {
            0 -> showWelcome()
            1 -> showNameSelection()
            2 -> showLanguageSelection()
            3 -> showPermissions()
            4 -> showComplete()
        }
    }
    
    private fun showWelcome() {
        titleText.text = "Welcome to VAANI"
        subtitleText.text = "Your Personal Voice Assistant"
        welcomeContainer.visibility = View.VISIBLE
        nextButton.text = "Get Started"
    }
    
    private fun showNameSelection() {
        titleText.text = "Choose Your Assistant Name"
        subtitleText.text = "What would you like to call your assistant?"
        nameContainer.visibility = View.VISIBLE
        nextButton.text = "Continue"
        
        nameExamples.text = "Examples: Ravi, Chitti, Buddy, Anaya, VAANI\n\n" +
                "You'll say: \"Hey [Name]\" to activate your assistant"
    }
    
    private fun showLanguageSelection() {
        titleText.text = "Choose Your Language"
        subtitleText.text = "Select the language you prefer to use"
        languageContainer.visibility = View.VISIBLE
        nextButton.text = "Continue"
    }
    
    private fun showPermissions() {
        titleText.text = "Enable Permissions"
        subtitleText.text = "VAANI needs these to help you"
        permissionsContainer.visibility = View.VISIBLE
        nextButton.text = "Grant Permissions"
        
        // Build permissions list
        permissionsList.removeAllViews()
        
        addPermissionItem("🎤 Microphone", "To hear your voice commands", true)
        addPermissionItem("♿ Accessibility", "To control your phone", true)
        addPermissionItem("📱 Overlay", "To show the assistant orb", true)
        addPermissionItem("📞 Phone", "To make calls for you", false)
        addPermissionItem("💬 Messages", "To send messages", false)
        addPermissionItem("📧 Contacts", "To find people", false)
        addPermissionItem("📍 Location", "For emergency SOS", false)
    }
    
    private fun addPermissionItem(icon: String, description: String, required: Boolean) {
        val itemView = layoutInflater.inflate(R.layout.permission_item, permissionsList, false)
        itemView.findViewById<TextView>(R.id.permissionIcon).text = icon
        itemView.findViewById<TextView>(R.id.permissionDescription).text = description
        itemView.findViewById<TextView>(R.id.permissionRequired).text = if (required) "Required" else "Optional"
        permissionsList.addView(itemView)
    }
    
    private fun showComplete() {
        titleText.text = "You're All Set!"
        subtitleText.text = "VAANI is ready to assist you"
        completeContainer.visibility = View.VISIBLE
        nextButton.text = "Start Using VAANI"
        
        // Show wake word
        val wakeWordText = findViewById<TextView>(R.id.wakeWordText)
        wakeWordText.text = "Say \"Hey $assistantName\" to activate your assistant"
    }
    
    private fun handleNext() {
        when (currentStep) {
            0 -> {
                // Welcome -> Name
                showStep(1)
            }
            1 -> {
                // Name -> Language
                val name = nameInput.text.toString().trim()
                if (name.isEmpty()) {
                    Toast.makeText(this, "Please enter a name for your assistant", Toast.LENGTH_SHORT).show()
                    return
                }
                assistantName = name
                showStep(2)
            }
            2 -> {
                // Language -> Permissions
                selectedLanguage = languageSpinner.selectedItem.toString()
                showStep(3)
            }
            3 -> {
                // Permissions -> Request them
                requestAllPermissions()
            }
            4 -> {
                // Complete -> Save and go to main
                saveOnboardingComplete()
                startMainActivity()
            }
        }
    }
    
    private fun requestAllPermissions() {
        // Request runtime permissions
        val missingPermissions = REQUIRED_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        
        if (missingPermissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missingPermissions.toTypedArray(), REQUEST_PERMISSIONS)
        } else {
            // Check overlay permission
            checkOverlayPermission()
        }
    }
    
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == REQUEST_PERMISSIONS) {
            // Check if all granted
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            
            if (allGranted) {
                checkOverlayPermission()
            } else {
                Toast.makeText(this, "Some permissions were denied. VAANI may not work fully.", Toast.LENGTH_LONG).show()
                // Still proceed
                checkOverlayPermission()
            }
        }
    }
    
    private fun checkOverlayPermission() {
        if (!Settings.canDrawOverlays(this)) {
            // Request overlay permission
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
            startActivityForResult(intent, REQUEST_OVERLAY)
        } else {
            checkAccessibilityPermission()
        }
    }
    
    private fun checkAccessibilityPermission() {
        if (!isAccessibilityServiceEnabled()) {
            // Show accessibility settings
            Toast.makeText(this, "Please enable VAANI in Accessibility Settings", Toast.LENGTH_LONG).show()
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            startActivityForResult(intent, REQUEST_ACCESSIBILITY)
        } else {
            // All permissions granted, move to complete
            showStep(4)
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        when (requestCode) {
            REQUEST_OVERLAY -> {
                checkAccessibilityPermission()
            }
            REQUEST_ACCESSIBILITY -> {
                // Check if enabled
                if (isAccessibilityServiceEnabled()) {
                    showStep(4)
                } else {
                    Toast.makeText(this, "Accessibility service is required. Please enable it.", Toast.LENGTH_LONG).show()
                    // Show again
                    checkAccessibilityPermission()
                }
            }
        }
    }
    
    private fun isAccessibilityServiceEnabled(): Boolean {
        val service = "${packageName}/${VaaniAccessibilityService::class.java.name}"
        val enabledServices = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )
        return enabledServices?.contains(service) == true
    }
    
    private fun saveOnboardingComplete() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().apply {
            putBoolean(KEY_ONBOARDING_COMPLETE, true)
            putString(KEY_ASSISTANT_NAME, assistantName)
            putString(KEY_LANGUAGE, selectedLanguage)
            apply()
        }
    }
    
    private fun startMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
}
