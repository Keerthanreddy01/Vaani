package com.vaani.phone

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.speech.tts.TextToSpeech
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.*

class MainActivity : AppCompatActivity(), VaaniVoiceService.StatusListener {
    
    private lateinit var statusText: TextView
    private lateinit var commandText: TextView
    private lateinit var startButton: Button
    private lateinit var settingsButton: Button
    
    private var tts: TextToSpeech? = null
    private var isServiceRunning = false
    
    companion object {
        const val REQUEST_PERMISSIONS = 100
        const val REQUEST_ACCESSIBILITY = 101
        
        val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.CALL_PHONE,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_CONTACTS
        )
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        statusText = findViewById(R.id.statusText)
        commandText = findViewById(R.id.commandText)
        startButton = findViewById(R.id.startButton)
        settingsButton = findViewById(R.id.settingsButton)
        
        // Initialize TTS
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.US
            }
        }
        
        // Set button listeners
        startButton.setOnClickListener {
            if (isServiceRunning) {
                stopVoiceService()
            } else {
                startVoiceService()
            }
        }
        
        settingsButton.setOnClickListener {
            openAccessibilitySettings()
        }
        
        // Check initial setup
        checkSetup()
    }
    
    private fun checkSetup() {
        // Check permissions
        if (!hasRequiredPermissions()) {
            showPermissionDialog()
            return
        }
        
        // Check accessibility service
        if (!isAccessibilityServiceEnabled()) {
            showAccessibilityDialog()
            return
        }
        
        // Check Vosk model
        val voskManager = VoskManager.getInstance(this)
        if (!voskManager.isModelReady()) {
            statusText.text = "Downloading speech model..."
            voskManager.downloadModel {
                runOnUiThread {
                    if (it) {
                        statusText.text = "Ready! Tap Start to begin"
                        Toast.makeText(this, "Model downloaded successfully!", Toast.LENGTH_SHORT).show()
                    } else {
                        statusText.text = "Failed to download model"
                        Toast.makeText(this, "Failed to download speech model", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        } else {
            statusText.text = "Ready! Tap Start to begin"
        }
    }
    
    private fun hasRequiredPermissions(): Boolean {
        return REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    private fun showPermissionDialog() {
        AlertDialog.Builder(this)
            .setTitle("Permissions Required")
            .setMessage("VAANI needs the following permissions to work:\n\n" +
                    "• Microphone - To hear your voice\n" +
                    "• Phone - To make calls\n" +
                    "• SMS - To send messages\n" +
                    "• Contacts - To find contacts")
            .setPositiveButton("Grant") { _, _ ->
                requestPermissions()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun requestPermissions() {
        ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_PERMISSIONS)
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_PERMISSIONS) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                checkSetup()
            } else {
                Toast.makeText(this, "All permissions are required", Toast.LENGTH_LONG).show()
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
    
    private fun showAccessibilityDialog() {
        AlertDialog.Builder(this)
            .setTitle("Enable Accessibility Service")
            .setMessage("VAANI needs Accessibility permission to control your phone.\n\n" +
                    "Please enable 'VAANI Voice Assistant' in the next screen.")
            .setPositiveButton("Open Settings") { _, _ ->
                openAccessibilitySettings()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun openAccessibilitySettings() {
        startActivityForResult(
            Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS),
            REQUEST_ACCESSIBILITY
        )
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_ACCESSIBILITY) {
            checkSetup()
        }
    }
    
    private fun startVoiceService() {
        if (!hasRequiredPermissions()) {
            showPermissionDialog()
            return
        }
        
        if (!isAccessibilityServiceEnabled()) {
            showAccessibilityDialog()
            return
        }
        
        val intent = Intent(this, VaaniVoiceService::class.java)
        ContextCompat.startForegroundService(this, intent)
        
        VaaniVoiceService.setStatusListener(this)
        
        isServiceRunning = true
        startButton.text = "Stop Listening"
        statusText.text = "Starting..."
    }
    
    private fun stopVoiceService() {
        val intent = Intent(this, VaaniVoiceService::class.java)
        stopService(intent)
        
        VaaniVoiceService.setStatusListener(null)
        
        isServiceRunning = false
        startButton.text = "Start Listening"
        statusText.text = "Stopped"
        commandText.text = ""
    }
    
    // StatusListener implementation
    override fun onStatusChanged(status: String) {
        runOnUiThread {
            statusText.text = status
        }
    }
    
    override fun onCommandReceived(command: String) {
        runOnUiThread {
            commandText.text = "Last command: $command"
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        tts?.shutdown()
        if (isServiceRunning) {
            stopVoiceService()
        }
    }
}
