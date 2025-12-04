package com.vaani.overlay

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import androidx.core.app.NotificationCompat
import java.net.ServerSocket
import java.net.Socket
import kotlin.concurrent.thread

class VaaniOverlayService : Service() {
    
    private var windowManager: WindowManager? = null
    private var overlayView: View? = null
    private var statusDot: ImageView? = null
    private val handler = Handler(Looper.getMainLooper())
    private var hideRunnable: Runnable? = null
    private var pulseAnimator: ObjectAnimator? = null
    private var serverSocket: ServerSocket? = null
    private var isRunning = false
    
    companion object {
        const val PORT = 8766
        const val HIDE_DELAY = 5000L
        const val NOTIFICATION_ID = 1001
        const val CHANNEL_ID = "vaani_overlay_channel"
    }

    override fun onCreate() {
        super.onCreate()
        startForeground()
        createOverlay()
        startSocketServer()
    }

    private fun startForeground() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "VAANI Overlay Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Shows VAANI status overlay on screen"
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("VAANI Overlay Active")
            .setContentText("Visual feedback enabled")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

        startForeground(NOTIFICATION_ID, notification)
    }
    
    private fun createOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                WindowManager.LayoutParams.TYPE_PHONE
            },
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                    WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        )
        
        layoutParams.gravity = Gravity.TOP or Gravity.END
        layoutParams.x = 20
        layoutParams.y = 100
        
        overlayView = LayoutInflater.from(this).inflate(R.layout.overlay_bubble, null)
        statusDot = overlayView?.findViewById(R.id.status_dot)
        
        windowManager?.addView(overlayView, layoutParams)
        
        // Initially hidden
        overlayView?.visibility = View.GONE
    }
    
    private fun startSocketServer() {
        isRunning = true
        thread {
            try {
                serverSocket = ServerSocket(PORT)
                while (isRunning) {
                    try {
                        val client = serverSocket?.accept()
                        client?.let { handleClient(it) }
                    } catch (e: Exception) {
                        if (isRunning) {
                            e.printStackTrace()
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    private fun handleClient(client: Socket) {
        thread {
            try {
                val reader = client.getInputStream().bufferedReader()
                while (isRunning) {
                    val message = reader.readLine() ?: break
                    handleMessage(message.trim())
                }
            } catch (e: Exception) {
                e.printStackTrace()
            } finally {
                client.close()
            }
        }
    }
    
    private fun handleMessage(message: String) {
        handler.post {
            when (message.uppercase()) {
                "LISTENING" -> showStatus(Color.BLUE, true)
                "PROCESSING" -> showStatus(Color.YELLOW, true)
                "SPEAKING" -> showStatus(Color.parseColor("#9C27B0"), true) // Purple
                "ACTION_OK" -> showStatus(Color.GREEN, false)
                "ACTION_FAILED" -> showStatus(Color.RED, false)
                "IDLE" -> hideStatus()
            }
        }
    }
    
    private fun showStatus(color: Int, pulse: Boolean) {
        overlayView?.visibility = View.VISIBLE
        statusDot?.setColorFilter(color)
        
        // Cancel previous hide
        hideRunnable?.let { handler.removeCallbacks(it) }
        
        // Stop previous animation
        pulseAnimator?.cancel()
        
        if (pulse) {
            // Pulse animation
            pulseAnimator = ObjectAnimator.ofFloat(statusDot, "alpha", 1f, 0.3f).apply {
                duration = 800
                repeatCount = ValueAnimator.INFINITE
                repeatMode = ValueAnimator.REVERSE
                start()
            }
        } else {
            statusDot?.alpha = 1f
            // Auto-hide after delay
            hideRunnable = Runnable { hideStatus() }
            handler.postDelayed(hideRunnable!!, HIDE_DELAY)
        }
    }
    
    private fun hideStatus() {
        pulseAnimator?.cancel()
        overlayView?.visibility = View.GONE
    }
    
    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        serverSocket?.close()
        pulseAnimator?.cancel()
        overlayView?.let { windowManager?.removeView(it) }
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
}

