package com.vaani.overlay

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    private val OVERLAY_PERMISSION_REQUEST_CODE = 1001
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        val statusText = findViewById<TextView>(R.id.status_text)
        val startButton = findViewById<Button>(R.id.start_button)
        val stopButton = findViewById<Button>(R.id.stop_button)
        
        startButton.setOnClickListener {
            if (checkOverlayPermission()) {
                startOverlayService()
                statusText.text = "✅ VAANI Overlay Active"
                Toast.makeText(this, "Overlay service started", Toast.LENGTH_SHORT).show()
            } else {
                requestOverlayPermission()
            }
        }
        
        stopButton.setOnClickListener {
            stopOverlayService()
            statusText.text = "⏹️ VAANI Overlay Stopped"
            Toast.makeText(this, "Overlay service stopped", Toast.LENGTH_SHORT).show()
        }
        
        // Auto-start if permission granted
        if (checkOverlayPermission()) {
            startOverlayService()
            statusText.text = "✅ VAANI Overlay Active"
        } else {
            statusText.text = "⚠️ Permission Required"
        }
    }
    
    private fun checkOverlayPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Settings.canDrawOverlays(this)
        } else {
            true
        }
    }
    
    private fun requestOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivityForResult(intent, OVERLAY_PERMISSION_REQUEST_CODE)
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == OVERLAY_PERMISSION_REQUEST_CODE) {
            if (checkOverlayPermission()) {
                startOverlayService()
                findViewById<TextView>(R.id.status_text).text = "✅ VAANI Overlay Active"
                Toast.makeText(this, "Permission granted! Starting overlay...", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Permission denied", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun startOverlayService() {
        val intent = Intent(this, VaaniOverlayService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }
    
    private fun stopOverlayService() {
        val intent = Intent(this, VaaniOverlayService::class.java)
        stopService(intent)
    }
}

