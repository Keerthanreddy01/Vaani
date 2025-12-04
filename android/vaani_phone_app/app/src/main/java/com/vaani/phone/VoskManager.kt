package com.vaani.phone

import android.content.Context
import android.util.Log
import org.vosk.Model
import java.io.File
import java.io.IOException
import java.net.URL
import java.util.zip.ZipInputStream

class VoskManager private constructor(private val context: Context) {
    
    private var model: Model? = null
    private val modelDir = File(context.filesDir, "vosk-model")
    
    companion object {
        const val TAG = "VoskManager"
        const val MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        
        @Volatile
        private var instance: VoskManager? = null
        
        fun getInstance(context: Context): VoskManager {
            return instance ?: synchronized(this) {
                instance ?: VoskManager(context.applicationContext).also { instance = it }
            }
        }
    }
    
    fun isModelReady(): Boolean {
        return modelDir.exists() && modelDir.listFiles()?.isNotEmpty() == true
    }
    
    fun getModel(): Model? {
        if (model == null && isModelReady()) {
            try {
                model = Model(modelDir.absolutePath)
                Log.d(TAG, "Model loaded from ${modelDir.absolutePath}")
            } catch (e: Exception) {
                Log.e(TAG, "Error loading model", e)
            }
        }
        return model
    }
    
    fun downloadModel(callback: (Boolean) -> Unit) {
        Thread {
            val success = downloadModelSync()
            callback(success)
        }.start()
    }
    
    fun downloadModelSync(): Boolean {
        try {
            Log.d(TAG, "Downloading model from $MODEL_URL")
            
            // Create model directory
            if (!modelDir.exists()) {
                modelDir.mkdirs()
            }
            
            // Download and extract
            val url = URL(MODEL_URL)
            val connection = url.openConnection()
            connection.connect()
            
            val zipInput = ZipInputStream(connection.getInputStream())
            var entry = zipInput.nextEntry
            
            while (entry != null) {
                val entryFile = File(modelDir, entry.name)
                
                if (entry.isDirectory) {
                    entryFile.mkdirs()
                } else {
                    entryFile.parentFile?.mkdirs()
                    entryFile.outputStream().use { output ->
                        zipInput.copyTo(output)
                    }
                }
                
                entry = zipInput.nextEntry
            }
            
            zipInput.close()
            
            Log.d(TAG, "Model downloaded successfully")
            return true
            
        } catch (e: IOException) {
            Log.e(TAG, "Error downloading model", e)
            return false
        }
    }
}
