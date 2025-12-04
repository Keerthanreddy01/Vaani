package com.vaani.accessibility

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.graphics.Path
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import androidx.annotation.RequiresApi
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import java.net.ServerSocket
import java.net.Socket
import org.json.JSONObject
import kotlin.concurrent.thread

/**
 * VAANI Accessibility Service
 * 
 * Provides hands-free voice control for Android devices.
 * Exposes actions via HTTP server for Python integration.
 */
class VaaniService : AccessibilityService() {

    private var serverSocket: ServerSocket? = null
    private var isRunning = false
    private val PORT = 8765

    override fun onServiceConnected() {
        super.onServiceConnected()
        
        // Start HTTP server
        startServer()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Handle accessibility events if needed
    }

    override fun onInterrupt() {
        // Handle interruption
    }

    override fun onDestroy() {
        super.onDestroy()
        stopServer()
    }

    private fun startServer() {
        isRunning = true
        
        thread {
            try {
                serverSocket = ServerSocket(PORT)
                
                while (isRunning) {
                    val client = serverSocket?.accept()
                    client?.let { handleClient(it) }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun stopServer() {
        isRunning = false
        serverSocket?.close()
    }

    private fun handleClient(client: Socket) {
        thread {
            try {
                val reader = BufferedReader(InputStreamReader(client.getInputStream()))
                val writer = PrintWriter(client.getOutputStream(), true)
                
                val request = reader.readLine()
                val response = processRequest(request)
                
                writer.println(response)
                client.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun processRequest(request: String): String {
        try {
            val json = JSONObject(request)
            val action = json.getString("action")
            
            return when (action) {
                "tap" -> tap(json.getInt("x"), json.getInt("y"))
                "swipe" -> swipe(
                    json.getInt("x1"), json.getInt("y1"),
                    json.getInt("x2"), json.getInt("y2")
                )
                "openApp" -> openApp(json.getString("package"))
                "back" -> performBack()
                "home" -> performHome()
                "readScreen" -> readScreen()
                "readNotifications" -> readNotifications()
                "call" -> makeCall(json.getString("number"))
                "sms" -> sendSMS(json.getString("number"), json.getString("message"))
                "type" -> typeText(json.getString("text"))
                else -> """{"status": "error", "message": "Unknown action"}"""
            }
        } catch (e: Exception) {
            return """{"status": "error", "message": "${e.message}"}"""
        }
    }

    @RequiresApi(Build.VERSION_CODES.N)
    private fun tap(x: Int, y: Int): String {
        val path = Path()
        path.moveTo(x.toFloat(), y.toFloat())
        
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 100))
            .build()
        
        val result = dispatchGesture(gesture, null, null)
        
        return if (result) {
            """{"status": "success", "message": "Tapped at ($x, $y)"}"""
        } else {
            """{"status": "error", "message": "Tap failed"}"""
        }
    }

    @RequiresApi(Build.VERSION_CODES.N)
    private fun swipe(x1: Int, y1: Int, x2: Int, y2: Int): String {
        val path = Path()
        path.moveTo(x1.toFloat(), y1.toFloat())
        path.lineTo(x2.toFloat(), y2.toFloat())
        
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 300))
            .build()
        
        val result = dispatchGesture(gesture, null, null)
        
        return if (result) {
            """{"status": "success", "message": "Swiped"}"""
        } else {
            """{"status": "error", "message": "Swipe failed"}"""
        }
    }

    private fun openApp(packageName: String): String {
        return try {
            val intent = packageManager.getLaunchIntentForPackage(packageName)
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                startActivity(intent)
                """{"status": "success", "message": "Opened $packageName"}"""
            } else {
                """{"status": "error", "message": "App not found"}"""
            }
        } catch (e: Exception) {
            """{"status": "error", "message": "${e.message}"}"""
        }
    }

    private fun performBack(): String {
        return if (performGlobalAction(GLOBAL_ACTION_BACK)) {
            """{"status": "success", "message": "Back pressed"}"""
        } else {
            """{"status": "error", "message": "Back failed"}"""
        }
    }

    private fun performHome(): String {
        return if (performGlobalAction(GLOBAL_ACTION_HOME)) {
            """{"status": "success", "message": "Home pressed"}"""
        } else {
            """{"status": "error", "message": "Home failed"}"""
        }
    }

    private fun readScreen(): String {
        val rootNode = rootInActiveWindow ?: return """{"status": "error", "message": "No active window"}"""

        val texts = mutableListOf<String>()
        extractTexts(rootNode, texts)

        val screenText = texts.joinToString(" ")
        return """{"status": "success", "message": "Screen read", "data": {"text": "$screenText"}}"""
    }

    private fun extractTexts(node: AccessibilityNodeInfo, texts: MutableList<String>) {
        if (node.text != null && node.text.isNotEmpty()) {
            texts.add(node.text.toString())
        }

        if (node.contentDescription != null && node.contentDescription.isNotEmpty()) {
            texts.add(node.contentDescription.toString())
        }

        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                extractTexts(child, texts)
                child.recycle()
            }
        }
    }

    private fun readNotifications(): String {
        // This would require notification listener service
        return """{"status": "error", "message": "Notification reading requires NotificationListenerService"}"""
    }

    private fun makeCall(phoneNumber: String): String {
        return try {
            val intent = Intent(Intent.ACTION_CALL)
            intent.data = Uri.parse("tel:$phoneNumber")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
            """{"status": "success", "message": "Calling $phoneNumber"}"""
        } catch (e: Exception) {
            """{"status": "error", "message": "${e.message}"}"""
        }
    }

    private fun sendSMS(phoneNumber: String, message: String): String {
        return try {
            val intent = Intent(Intent.ACTION_SENDTO)
            intent.data = Uri.parse("smsto:$phoneNumber")
            intent.putExtra("sms_body", message)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
            """{"status": "success", "message": "SMS sent"}"""
        } catch (e: Exception) {
            """{"status": "error", "message": "${e.message}"}"""
        }
    }

    private fun typeText(text: String): String {
        // This requires input method or accessibility node manipulation
        return """{"status": "error", "message": "Text input not yet implemented"}"""
    }
}


