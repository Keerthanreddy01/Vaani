package com.vaani.phone

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class VaaniAccessibilityService : AccessibilityService() {
    
    companion object {
        const val TAG = "VaaniAccessibility"
        
        @Volatile
        var instance: VaaniAccessibilityService? = null
    }
    
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.d(TAG, "✅ Accessibility service connected")
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Monitor events if needed
    }
    
    override fun onInterrupt() {
        Log.d(TAG, "Service interrupted")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.d(TAG, "Service destroyed")
    }
    
    /**
     * Perform back button action
     */
    fun performBack(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_BACK)
    }
    
    /**
     * Perform home button action
     */
    fun performHome(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_HOME)
    }
    
    /**
     * Open notifications
     */
    fun openNotifications(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
    }
    
    /**
     * Scroll down
     */
    fun scrollDown(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val result = rootNode.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        rootNode.recycle()
        return result
    }
    
    /**
     * Scroll up
     */
    fun scrollUp(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val result = rootNode.performAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)
        rootNode.recycle()
        return result
    }
    
    /**
     * Perform tap at coordinates
     */
    fun performTap(x: Float, y: Float): Boolean {
        val path = Path().apply {
            moveTo(x, y)
        }
        
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 100))
            .build()
        
        return dispatchGesture(gesture, null, null)
    }
    
    /**
     * Perform swipe gesture
     */
    fun performSwipe(direction: String): Boolean {
        // Get screen dimensions (assuming 1080x2400)
        val centerX = 540f
        val centerY = 1200f
        val distance = 500f
        
        val (x1, y1, x2, y2) = when (direction) {
            "down" -> arrayOf(centerX, centerY - distance, centerX, centerY + distance)
            "up" -> arrayOf(centerX, centerY + distance, centerX, centerY - distance)
            "left" -> arrayOf(centerX + distance, centerY, centerX - distance, centerY)
            "right" -> arrayOf(centerX - distance, centerY, centerX + distance, centerY)
            else -> return false
        }
        
        val path = Path().apply {
            moveTo(x1, y1)
            lineTo(x2, y2)
        }
        
        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 300))
            .build()
        
        return dispatchGesture(gesture, null, null)
    }
    
    /**
     * Read all text from current screen
     */
    fun readScreenText(): String {
        val rootNode = rootInActiveWindow ?: return ""
        val texts = mutableListOf<String>()
        
        extractTexts(rootNode, texts)
        rootNode.recycle()
        
        val result = texts.take(10).joinToString(". ") // Limit to first 10 items
        Log.d(TAG, "Screen text: $result")
        return result
    }
    
    /**
     * Recursively extract text from node tree
     */
    private fun extractTexts(node: AccessibilityNodeInfo, texts: MutableList<String>) {
        // Get text from this node
        node.text?.toString()?.let {
            if (it.isNotBlank()) {
                texts.add(it)
            }
        }
        
        node.contentDescription?.toString()?.let {
            if (it.isNotBlank() && !texts.contains(it)) {
                texts.add(it)
            }
        }
        
        // Recurse to children
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                extractTexts(child, texts)
                child.recycle()
            }
        }
    }
    
    /**
     * Find UI element by text
     */
    fun findElementByText(text: String): AccessibilityNodeInfo? {
        val rootNode = rootInActiveWindow ?: return null
        return findNodeByText(rootNode, text)
    }
    
    private fun findNodeByText(node: AccessibilityNodeInfo, text: String): AccessibilityNodeInfo? {
        // Check this node
        if (node.text?.toString()?.contains(text, ignoreCase = true) == true ||
            node.contentDescription?.toString()?.contains(text, ignoreCase = true) == true) {
            return node
        }
        
        // Check children
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                val found = findNodeByText(child, text)
                if (found != null) {
                    child.recycle()
                    return found
                }
                child.recycle()
            }
        }
        
        return null
    }
    
    /**
     * Click element by text
     */
    fun clickElement(text: String): Boolean {
        val node = findElementByText(text)
        if (node != null) {
            val result = node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            node.recycle()
            return result
        }
        return false
    }
    
    /**
     * Type text into focused input field
     */
    fun typeText(text: String): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val focusedNode = findFocusedEditText(rootNode)
        
        if (focusedNode != null) {
            val arguments = android.os.Bundle()
            arguments.putCharSequence(
                AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                text
            )
            val result = focusedNode.performAction(
                AccessibilityNodeInfo.ACTION_SET_TEXT,
                arguments
            )
            focusedNode.recycle()
            rootNode.recycle()
            return result
        }
        
        rootNode.recycle()
        return false
    }
    
    /**
     * Find focused EditText
     */
    private fun findFocusedEditText(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isFocused && node.className == "android.widget.EditText") {
            return node
        }
        
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                val found = findFocusedEditText(child)
                if (found != null) {
                    child.recycle()
                    return found
                }
                child.recycle()
            }
        }
        
        return null
    }
    
    /**
     * Press enter key
     */
    fun pressEnter(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val focusedNode = findFocusedEditText(rootNode)
        
        if (focusedNode != null) {
            // Try to click a search/send button nearby
            val result = focusedNode.performAction(AccessibilityNodeInfo.ACTION_IME_ENTER)
            focusedNode.recycle()
            rootNode.recycle()
            return result
        }
        
        rootNode.recycle()
        return false
    }
}
