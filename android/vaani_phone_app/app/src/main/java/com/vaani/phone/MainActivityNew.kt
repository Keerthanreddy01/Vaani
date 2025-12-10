package com.vaani.phone

import android.Manifest
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class MainActivityNew : AppCompatActivity() {
    
    private lateinit var wakeWordInput: EditText
    private lateinit var currentWakeWordText: TextView
    private lateinit var serviceSwitch: Switch
    private lateinit var statusText: TextView
    private lateinit var testButton: Button
    private lateinit var permissionsButton: Button
    private lateinit var saveWakeWordButton: Button
    private lateinit var helpButton: Button
    
    private lateinit var prefs: SharedPreferences
    
    private val PERMISSION_REQUEST_CODE = 100
    private val OVERLAY_PERMISSION_REQUEST_CODE = 101
    private val ACCESSIBILITY_PERMISSION_REQUEST_CODE = 102
    
    private val requiredPermissions = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.CALL_PHONE,
        Manifest.permission.SEND_SMS,
        Manifest.permission.READ_CONTACTS
    )
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main_new)
        
        prefs = getSharedPreferences("VaaniPrefs", MODE_PRIVATE)
        
        initializeViews()
        setupListeners()
        loadSettings()
        updateServiceStatus()
        checkSetup()
    }
    
    private fun initializeViews() {
        wakeWordInput = findViewById(R.id.wakeWordInput)
        currentWakeWordText = findViewById(R.id.currentWakeWordText)
        serviceSwitch = findViewById(R.id.serviceSwitch)
        statusText = findViewById(R.id.statusText)
        testButton = findViewById(R.id.testButton)
        permissionsButton = findViewById(R.id.permissionsButton)
        saveWakeWordButton = findViewById(R.id.saveWakeWordButton)
        helpButton = findViewById(R.id.helpButton)
    }
    
    private fun setupListeners() {
        serviceSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                if (checkAllPermissions()) {
                    startVaaniService()
                } else {
                    serviceSwitch.isChecked = false
                    requestAllPermissions()
                }
            } else {
                stopVaaniService()
            }
        }
        
        saveWakeWordButton.setOnClickListener {
            saveWakeWord()
        }
        
        testButton.setOnClickListener {
            testWakeWord()
        }
        
        permissionsButton.setOnClickListener {
            showPermissionsDialog()
        }
        
        helpButton.setOnClickListener {
            showHelpDialog()
        }
    }
    
    private fun loadSettings() {
        val savedWakeWord = prefs.getString("wake_word", "Vaani") ?: "Vaani"
        wakeWordInput.setText(savedWakeWord)
        currentWakeWordText.text = "Current: \"$savedWakeWord\""
    }
    
    private fun saveWakeWord() {
        val wakeWord = wakeWordInput.text.toString().trim()
        
        if (wakeWord.isEmpty()) {
            Toast.makeText(this, "Please enter a wake word", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (wakeWord.length < 2) {
            Toast.makeText(this, "Wake word must be at least 2 characters", Toast.LENGTH_SHORT).show()
            return
        }
        
        prefs.edit().putString("wake_word", wakeWord).apply()
        currentWakeWordText.text = "Current: \"$wakeWord\""
        Toast.makeText(this, "Wake word saved: $wakeWord", Toast.LENGTH_SHORT).show()
        
        // Restart service if running
        if (isServiceRunning()) {
            AlertDialog.Builder(this)
                .setTitle("Restart Service?")
                .setMessage("Service needs to restart to use the new wake word. Restart now?")
                .setPositiveButton("Yes") { _, _ ->
                    stopVaaniService()
                    android.os.Handler(mainLooper).postDelayed({
                        startVaaniService()
                    }, 500)
                }
                .setNegativeButton("Later", null)
                .show()
        }
    }
    
    private fun testWakeWord() {
        val wakeWord = wakeWordInput.text.toString().trim()
        if (wakeWord.isEmpty()) {
            Toast.makeText(this, "Please enter a wake word first", Toast.LENGTH_SHORT).show()
            return
        }
        
        AlertDialog.Builder(this)
            .setTitle("Test Wake Word")
            .setMessage("To test your wake word \"$wakeWord\":\n\n" +
                    "1. Save the wake word\n" +
                    "2. Enable the service\n" +
                    "3. Say \"$wakeWord\" followed by a command\n\n" +
                    "Example: \"$wakeWord, open WhatsApp\"")
            .setPositiveButton("Got it", null)
            .show()
    }
    
    private fun checkSetup() {
        // Check Vosk model
        val voskManager = VoskManager.getInstance(this)
        if (!voskManager.isModelReady()) {
            statusText.text = "📥 Downloading speech model..."
            voskManager.downloadModel { success ->
                runOnUiThread {
                    if (success) {
                        statusText.text = "✓ Model ready"
                        Toast.makeText(this, "Speech model downloaded!", Toast.LENGTH_SHORT).show()
                    } else {
                        statusText.text = "✗ Model download failed"
                    }
                }
            }
        }
    }
    
    private fun startVaaniService() {
        val intent = Intent(this, VaaniService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        updateServiceStatus()
        Toast.makeText(this, "Vaani service started", Toast.LENGTH_SHORT).show()
    }
    
    private fun stopVaaniService() {
        val intent = Intent(this, VaaniService::class.java)
        stopService(intent)
        updateServiceStatus()
        Toast.makeText(this, "Vaani service stopped", Toast.LENGTH_SHORT).show()
    }
    
    private fun isServiceRunning(): Boolean {
        return prefs.getBoolean("service_running", false)
    }
    
    private fun updateServiceStatus() {
        android.os.Handler(mainLooper).postDelayed({
            if (isServiceRunning()) {
                val wakeWord = prefs.getString("wake_word", "Vaani") ?: "Vaani"
                statusText.text = "✓ Listening for \"$wakeWord\""
                statusText.setTextColor(ContextCompat.getColor(this, android.R.color.holo_green_dark))
                serviceSwitch.isChecked = true
            } else {
                statusText.text = "✗ Service stopped"
                statusText.setTextColor(ContextCompat.getColor(this, android.R.color.holo_red_dark))
                serviceSwitch.isChecked = false
            }
        }, 300)
    }
    
    private fun checkAllPermissions(): Boolean {
        // Check regular permissions
        for (permission in requiredPermissions) {
            if (ContextCompat.checkSelfPermission(this, permission) 
                != PackageManager.PERMISSION_GRANTED) {
                return false
            }
        }
        
        // Check overlay permission
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(this)) {
                return false
            }
        }
        
        // Check accessibility permission
        if (!isAccessibilityServiceEnabled()) {
            return false
        }
        
        return true
    }
    
    private fun isAccessibilityServiceEnabled(): Boolean {
        val service = "${packageName}/${VaaniAccessibilityService::class.java.name}"
        val enabledServices = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )
        return enabledServices?.contains(service) == true
    }
    
    private fun requestAllPermissions() {
        showPermissionsDialog()
    }
    
    private fun showPermissionsDialog() {
        AlertDialog.Builder(this)
            .setTitle("Setup Required")
            .setMessage("Vaani needs several permissions to work:\n\n" +
                    "✓ Microphone - Listen to your voice\n" +
                    "✓ Phone - Make calls\n" +
                    "✓ SMS - Send messages\n" +
                    "✓ Contacts - Find contacts\n" +
                    "✓ Overlay - Show visual feedback\n" +
                    "✓ Accessibility - Control apps\n\n" +
                    "Grant all permissions?")
            .setPositiveButton("Grant") { _, _ ->
                requestPermissionsStep()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun requestPermissionsStep() {
        // Step 1: Regular permissions
        val notGranted = requiredPermissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }.toTypedArray()
        
        if (notGranted.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, notGranted, PERMISSION_REQUEST_CODE)
            return
        }
        
        // Step 2: Overlay permission
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivityForResult(intent, OVERLAY_PERMISSION_REQUEST_CODE)
            return
        }
        
        // Step 3: Accessibility service
        if (!isAccessibilityServiceEnabled()) {
            startActivityForResult(
                Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS),
                ACCESSIBILITY_PERMISSION_REQUEST_CODE
            )
            return
        }
        
        Toast.makeText(this, "All permissions granted!", Toast.LENGTH_SHORT).show()
    }
    
    private fun showHelpDialog() {
        AlertDialog.Builder(this)
            .setTitle("How to Use Vaani")
            .setMessage("""
                1. Choose Your Wake Word
                   Enter any name you like (e.g., "Vaani", "Assistant", "Hey Google")
                   
                2. Save & Enable
                   Save the wake word and turn on the service
                   
                3. Use Commands
                   Say: "[Wake Word], [Command]"
                   
                Examples:
                • "Vaani, open WhatsApp"
                • "Vaani, call Mom"
                • "Vaani, send message to John"
                • "Vaani, go back"
                • "Vaani, what time is it"
                
                Supported Apps:
                WhatsApp, YouTube, Chrome, Gmail, Maps, Camera, Settings, and more!
            """.trimIndent())
            .setPositiveButton("Got it", null)
            .show()
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                Toast.makeText(this, "Permissions granted", Toast.LENGTH_SHORT).show()
                requestPermissionsStep() // Continue to next step
            } else {
                Toast.makeText(this, "Some permissions denied. Vaani may not work properly.", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        when (requestCode) {
            OVERLAY_PERMISSION_REQUEST_CODE -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && Settings.canDrawOverlays(this)) {
                    Toast.makeText(this, "Overlay permission granted", Toast.LENGTH_SHORT).show()
                    requestPermissionsStep() // Continue to next step
                } else {
                    Toast.makeText(this, "Overlay permission needed for visual feedback", Toast.LENGTH_LONG).show()
                }
            }
            ACCESSIBILITY_PERMISSION_REQUEST_CODE -> {
                if (isAccessibilityServiceEnabled()) {
                    Toast.makeText(this, "Accessibility service enabled", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Accessibility service needed to control apps", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        updateServiceStatus()
    }
}
