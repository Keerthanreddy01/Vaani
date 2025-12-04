
package com.vaani.service

import android.Manifest
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.IBinder
import android.util.Log
import androidx.core.app.ActivityCompat
import java.util.concurrent.atomic.AtomicBoolean

class VaaniAudioService : Service() {

    private val TAG = "VaaniAudioService"
    private lateinit var audioRecord: AudioRecord
    private var recordingThread: Thread? = null
    private val isRecording = AtomicBoolean(false)

    private val sampleRate = 16000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    private var bufferSize = 0

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VaaniAudioService created")
        bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            Log.e(TAG, "Audio recording permission not granted")
            // TODO: Handle permission not granted case. Maybe stop the service.
            return
        }
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelConfig,
            audioFormat,
            bufferSize
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "VaaniAudioService started")
        startRecording()
        return START_STICKY
    }

    private fun startRecording() {
        if (isRecording.get()) {
            Log.w(TAG, "Recording is already in progress")
            return
        }

        audioRecord.startRecording()
        isRecording.set(true)

        recordingThread = Thread {
            processAudioStream()
        }
        recordingThread?.start()
        Log.d(TAG, "Recording started")
    }

    private fun processAudioStream() {
        val audioBuffer = ShortArray(bufferSize / 2)
        while (isRecording.get()) {
            val readSize = audioRecord.read(audioBuffer, 0, audioBuffer.size)
            if (readSize > 0) {
                // TODO: Pass this audioBuffer to the wake word engine.
                // For now, just logging the audio data presence.
                // Log.v(TAG, "Read $readSize shorts from microphone.")
            }
        }
    }

    private fun stopRecording() {
        if (!isRecording.get()) {
            Log.w(TAG, "Recording is not in progress")
            return
        }

        isRecording.set(false)
        recordingThread?.interrupt()
        recordingThread = null

        if (::audioRecord.isInitialized && audioRecord.recordingState == AudioRecord.RECORDSTATE_RECORDING) {
            audioRecord.stop()
        }
        Log.d(TAG, "Recording stopped")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "VaaniAudioService destroyed")
        stopRecording()
        if (::audioRecord.isInitialized) {
            audioRecord.release()
        }
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
