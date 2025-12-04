package com.vaani.phone

import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.graphics.Color
import android.os.Handler
import android.os.Looper

class FloatingOrbService : Service() {
    
    private var windowManager: WindowManager? = null
    private var floatingView: View? = null
    private var orbView: ImageView? = null
    private var isShowing = false
    
    private val handler = Handler(Looper.getMainLooper())
    private var hideRunnable: Runnable? = null
    
    companion object {
        const val ACTION_SHOW = "com.vaani.phone.SHOW_ORB"
        const val ACTION_HIDE = "com.vaani.phone.HIDE_ORB"
        const val ACTION_UPDATE_STATUS = "com.vaani.phone.UPDATE_STATUS"
        const val EXTRA_STATUS = "status"
        
        const val STATUS_LISTENING = "listening"
        const val STATUS_PROCESSING = "processing"
        const val STATUS_SPEAKING = "speaking"
        const val STATUS_SUCCESS = "success"
        const val STATUS_ERROR = "error"
        const val STATUS_IDLE = "idle"
    }
    
    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_SHOW -> showOrb()
            ACTION_HIDE -> hideOrb()
            ACTION_UPDATE_STATUS -> {
                val status = intent.getStringExtra(EXTRA_STATUS) ?: STATUS_IDLE
                updateStatus(status)
            }
        }
        return START_STICKY
    }
    
    private fun showOrb() {
        if (isShowing) return
        
        try {
            floatingView = LayoutInflater.from(this).inflate(R.layout.floating_orb, null)
            orbView = floatingView?.findViewById(R.id.orbView)
            
            val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                WindowManager.LayoutParams.TYPE_PHONE
            }
            
            val params = WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                layoutFlag,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                        WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or
                        WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH,
                PixelFormat.TRANSLUCENT
            )
            
            params.gravity = Gravity.TOP or Gravity.END
            params.x = 20
            params.y = 100
            
            windowManager?.addView(floatingView, params)
            isShowing = true
            
            updateStatus(STATUS_LISTENING)
            
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun hideOrb() {
        if (!isShowing) return
        
        try {
            windowManager?.removeView(floatingView)
            floatingView = null
            orbView = null
            isShowing = false
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun updateStatus(status: String) {
        if (!isShowing || orbView == null) {
            showOrb()
        }
        
        // Cancel any pending hide
        hideRunnable?.let { handler.removeCallbacks(it) }
        
        orbView?.let { orb ->
            when (status) {
                STATUS_LISTENING -> {
                    setOrbColor(orb, Color.parseColor("#3B82F6")) // Blue
                    startPulseAnimation(orb)
                }
                STATUS_PROCESSING -> {
                    setOrbColor(orb, Color.parseColor("#F59E0B")) // Yellow/Orange
                    startPulseAnimation(orb)
                }
                STATUS_SPEAKING -> {
                    setOrbColor(orb, Color.parseColor("#A855F7")) // Purple
                    stopPulseAnimation(orb)
                }
                STATUS_SUCCESS -> {
                    setOrbColor(orb, Color.parseColor("#10B981")) // Green
                    stopPulseAnimation(orb)
                    scheduleHide(2000)
                }
                STATUS_ERROR -> {
                    setOrbColor(orb, Color.parseColor("#EF4444")) // Red
                    stopPulseAnimation(orb)
                    scheduleHide(3000)
                }
                STATUS_IDLE -> {
                    scheduleHide(1000)
                }
            }
        }
    }
    
    private fun setOrbColor(orb: ImageView, color: Int) {
        orb.setColorFilter(color)
    }
    
    private var pulseAnimator: ValueAnimator? = null
    
    private fun startPulseAnimation(orb: ImageView) {
        stopPulseAnimation(orb)
        
        pulseAnimator = ValueAnimator.ofFloat(0.6f, 1.0f).apply {
            duration = 1000
            repeatCount = ValueAnimator.INFINITE
            repeatMode = ValueAnimator.REVERSE
            addUpdateListener { animation ->
                val value = animation.animatedValue as Float
                orb.scaleX = value
                orb.scaleY = value
                orb.alpha = value
            }
            start()
        }
    }
    
    private fun stopPulseAnimation(orb: ImageView) {
        pulseAnimator?.cancel()
        pulseAnimator = null
        orb.scaleX = 1.0f
        orb.scaleY = 1.0f
        orb.alpha = 1.0f
    }
    
    private fun scheduleHide(delayMillis: Long) {
        hideRunnable = Runnable {
            hideOrb()
        }
        handler.postDelayed(hideRunnable!!, delayMillis)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        hideOrb()
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
