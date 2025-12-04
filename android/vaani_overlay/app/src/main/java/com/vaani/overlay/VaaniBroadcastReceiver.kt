package com.vaani.overlay

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build

class VaaniBroadcastReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED,
            "com.vaani.overlay.START_SERVICE" -> {
                val serviceIntent = Intent(context, VaaniOverlayService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent)
                } else {
                    context.startService(serviceIntent)
                }
            }
        }
    }
}

