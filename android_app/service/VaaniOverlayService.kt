
package com.vaani.service

import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.IBinder
import android.view.Gravity
import android.view.WindowManager
import android.widget.ImageView
import android.util.Log

class VaaniOverlayService : Service() {

    private val TAG = "VaaniOverlayService"
    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: ImageView

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VaaniOverlayService created")

        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager

        floatingView = ImageView(this)
        // TODO: Replace with a proper drawable for the overlay
        floatingView.setBackgroundColor(0xFF0000FF.toInt()) // Blue for listening

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )

        params.gravity = Gravity.TOP or Gravity.START
        params.x = 0
        params.y = 100

        windowManager.addView(floatingView, params)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "VaaniOverlayService started")
        // TODO: Implement logic to update overlay color based on assistant state
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "VaaniOverlayService destroyed")
        windowManager.removeView(floatingView)
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
}
