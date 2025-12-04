package com.vaani.phone

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Check if onboarding is complete
            val prefs = context.getSharedPreferences(OnboardingActivity.PREFS_NAME, Context.MODE_PRIVATE)
            if (prefs.getBoolean(OnboardingActivity.KEY_ONBOARDING_COMPLETE, false)) {
                // Start voice service in background
                val serviceIntent = Intent(context, VaaniVoiceService::class.java)
                context.startForegroundService(serviceIntent)
            }
        }
    }
}
