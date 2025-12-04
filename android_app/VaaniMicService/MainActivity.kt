package com.vaani.micservice

import android.Manifest
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.OutputStream
import java.net.ServerSocket
import java.net.Socket
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    
    private var isRecording = false
    private var audioRecord: AudioRecord? = null
    private var serverSocket: ServerSocket? = null
    private var clientSocket: Socket? = null
    private var outputStream: OutputStream? = null
    
    private lateinit var statusText: TextView
    private lateinit var startButton: Button
    
    companion object {
        const val SAMPLE_RATE = 16000
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        const val PORT = 8888
        const val REQUEST_RECORD_AUDIO = 1
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        statusText = findViewById(R.id.statusText)
        startButton = findViewById(R.id.startButton)
        
        startButton.setOnClickListener {
            if (isRecording) {
                stopRecording()
            } else {
                if (checkPermissions()) {
                    startRecording()
                } else {
                    requestPermissions()
                }
            }
        }
        
        updateUI()
    }
    
    private fun checkPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    private fun requestPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.RECORD_AUDIO),
            REQUEST_RECORD_AUDIO
        )
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_RECORD_AUDIO) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startRecording()
            }
        }
    }
    
    private fun startRecording() {
        isRecording = true
        updateUI()
        
        thread {
            try {
                // Start server socket
                serverSocket = ServerSocket(PORT)
                statusText.post { statusText.text = "Waiting for connection on port $PORT..." }
                
                // Wait for laptop to connect
                clientSocket = serverSocket?.accept()
                outputStream = clientSocket?.getOutputStream()
                
                statusText.post { statusText.text = "Connected! Recording..." }
                
                // Initialize AudioRecord
                val bufferSize = AudioRecord.getMinBufferSize(
                    SAMPLE_RATE,
                    CHANNEL_CONFIG,
                    AUDIO_FORMAT
                )
                
                audioRecord = AudioRecord(
                    MediaRecorder.AudioSource.MIC,
                    SAMPLE_RATE,
                    CHANNEL_CONFIG,
                    AUDIO_FORMAT,
                    bufferSize
                )
                
                audioRecord?.startRecording()
                
                // Stream audio data
                val buffer = ByteArray(bufferSize)
                while (isRecording) {
                    val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (read > 0) {
                        outputStream?.write(buffer, 0, read)
                        outputStream?.flush()
                    }
                }
                
            } catch (e: Exception) {
                e.printStackTrace()
                statusText.post { statusText.text = "Error: ${e.message}" }
            } finally {
                cleanup()
            }
        }
    }
    
    private fun stopRecording() {
        isRecording = false
        cleanup()
        updateUI()
    }
    
    private fun cleanup() {
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        
        outputStream?.close()
        clientSocket?.close()
        serverSocket?.close()
        
        statusText.post { statusText.text = "Stopped" }
    }
    
    private fun updateUI() {
        startButton.text = if (isRecording) "Stop Recording" else "Start Recording"
        if (!isRecording) {
            statusText.text = "Ready"
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        stopRecording()
    }
}

