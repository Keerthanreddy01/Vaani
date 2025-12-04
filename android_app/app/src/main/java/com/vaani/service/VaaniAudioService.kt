
package com.vaani.service

import android.Manifest
import android.app.Service
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
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

    private var wakeWordService: WakeWordService? = null
    private var isWakeWordServiceBound = false

    private val wakeWordServiceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            val binder = service as WakeWordService.LocalBinder
            wakeWordService = binder.getService()
            isWakeWordServiceBound = true
            Log.d(TAG, "WakeWordService connected")
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            wakeWordService = null
            isWakeWordServiceBound = false
            Log.d(TAG, "WakeWordService disconnected")
        }
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VaaniAudioService created")
        bufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "Audio recording permission not granted")
            return
        }
        audioRecord = AudioRecord(MediaRecorder.AudioSource.MIC, sampleRate, channelConfig, audioFormat, bufferSize)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "VaaniAudioService started")
        startRecording()
        Intent(this, WakeWordService::class.java).also { wakeWordIntent ->
            bindService(wakeWordIntent, wakeWordServiceConnection, Context.BIND_AUTO_CREATE)
        }
        return START_STICKY
    }

    private fun startRecording() {
        if (isRecording.get()) return
        audioRecord.startRecording()
        isRecording.set(true)
        recordingThread = Thread { processAudioStream() }
        recordingThread?.start()
        Log.d(TAG, "Recording started")
    }

    private fun processAudioStream() {
        val audioBuffer = ShortArray(bufferSize / 2)
        while (isRecording.get()) {
            val readSize = audioRecord.read(audioBuffer, 0, audioBuffer.size)
            if (readSize > 0 && isWakeWordServiceBound) {
                wakeWordService?.processAudio(audioBuffer)
            }
        }
    }

    private fun stopRecording() {
        if (!isRecording.get()) return
        isRecording.set(false)
        recordingThread?.interrupt()
        recordingThread = null
        audioRecord.stop()
        Log.d(TAG, "Recording stopped")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "VaaniAudioService destroyed")
        stopRecording()
        audioRecord.release()
        if (isWakeWordServiceBound) {
            unbindService(wakeWordServiceConnection)
            isWakeWordServiceBound = false
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
