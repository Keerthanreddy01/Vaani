
package com.vaani.ui

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.vaani.R
import com.vaani.service.VaaniAudioService
import com.vaani.service.VaaniOverlayService
import com.vaani.service.TTSService

class MainActivity : AppCompatActivity() {

    private val PERMISSION_REQUEST_CODE = 101

    private lateinit var assistantNameEditText: EditText
    private lateinit var languageSpinner: Spinner

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        assistantNameEditText = findViewById(R.id.assistantNameEditText)
        languageSpinner = findViewById(R.id.languageSpinner)

        // Populate Spinner
        ArrayAdapter.createFromResource(
            this,
            R.array.languages_array,
            android.R.layout.simple_spinner_item
        ).also { adapter ->
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
            languageSpinner.adapter = adapter
        }

        val getStartedButton = findViewById<Button>(R.id.getStartedButton)
        getStartedButton.setOnClickListener {
            savePreferences()
            requestPermissions()
        }
    }

    private fun savePreferences() {
        val sharedPref = getSharedPreferences("VaaniPrefs", Context.MODE_PRIVATE) ?: return
        with(sharedPref.edit()) {
            putString("assistantName", assistantNameEditText.text.toString())
            putString("language", languageSpinner.selectedItem.toString())
            apply()
        }
        Toast.makeText(this, "Preferences saved", Toast.LENGTH_SHORT).show()
    }

    private fun requestPermissions() {
        // ... (permission logic remains the same)
    }

    private fun startAllServices() {
        startService(Intent(this, VaaniAudioService::class.java))
        startService(Intent(this, VaaniOverlayService::class.java))
        startService(Intent(this, TTSService::class.java))
    }

    // ... (rest of the permission handling code)
}
